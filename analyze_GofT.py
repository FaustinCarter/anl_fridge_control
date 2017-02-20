# analyze_GofT.py
#
# Some tools for measuring G(T). The main outward-facing function in this module
# is 'find_G_params', which will extract Psat values from 'drop_bolos' data and
# fit it to a functional form to measure the G(T).
#
# Adam Anderson
# adama@fnal.gov
# 10 May 2016 (reorganized from existing code)

import pydfmux.analysis.analyze_IV as analyze_IV
import cPickle as pickle
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def find_G_params(data_files, Rp=[], plot_path=None, T_range=[0.2, 0.6]):
    '''
    Finds Psat values for all data acquired by drop_bolos in paths supplied in
    arguments, at various temperatures, then fits Psat data for each bolometer
    as a function of temperature to the functional form described in the
    'fit_PsatofT' docstring.

    Parameters
    ----------
    data_files : python dictionary
        {temperatures -> full path to pickle produced by 'drop_bolos'}
    Rp : python dictionary
        {bolo name -> parasitic resistance}}
    plot_path (default=None) : string
        Full path of file with plot (png)
    T_range : python list
        Range of temperatures to plot

    Returns
    -------
    fit_params : python dictionary
        {channel name -> fit parameters}
    fit_errs : python dictionary
        {channel name -> fit errors}
    '''
    PsatVtemp = dict()
    # loop over temperatures and data to find Psats at each point
    for temp in data_files:
        Psats = dict()
        IV_file = file(data_files[temp])
        IV_data = pickle.load(IV_file)
        IV_file.close()
#        if len(Rp) == 0:
#            Zp = 0
#        else:
#            Zp = Rp

        Psat_at_T = analyze_IV.find_Psat(data_files[temp], R_threshold='pturn', Zp=Rp, plot_dir=None)
        for channum in Psat_at_T: #IV_data['subtargets']:
            boloname = IV_data['subtargets'][channum]['bolometer']
            if boloname not in PsatVtemp:
                PsatVtemp[boloname] = dict()
                PsatVtemp[boloname]['T'] = np.array(data_files.keys())
                PsatVtemp[boloname]['Psat'] = np.zeros(len(PsatVtemp[boloname]['T']))
            PsatVtemp[boloname]['Psat'][temp==PsatVtemp[boloname]['T']] = Psat_at_T[channum]

    # now do the fitting of Psat(T)
    fit_params = dict()
    fit_errs = dict()
    for boloname in PsatVtemp:
        fitp, cov = fit_PsatofT(PsatVtemp[boloname]['T'], PsatVtemp[boloname]['Psat'])
        if type(fitp) == np.ndarray:
            fit_params[boloname] = fitp
            fit_errs[boloname] = [np.sqrt(cov[ind][ind]) for ind in range(cov.shape[0])]

    # make plots if desired
    # (don't make empty plots)
    if plot_path != None and len(PsatVtemp) > 0:
        f = plot_PsatofT(data_files.keys(), PsatVtemp, fit_params, fit_errs, T_range)
        f.savefig(plot_path)

    return fit_params, fit_errs, PsatVtemp


def fit_PsatofT(T, Psat):
    '''
    Fits Psat as a function of temeperature to the following functional form:
        P(T) = k(Tc^n - T^n)
    with k, Tc, and n as fit parameters. The conductance is given by Taylor
    expanding around Tc:
        G = knTc^(n-1)

    Parameters
    ----------
    T : numpy array
        Temperature data [K]
    Psat : numpy array
        Psat data [W]

    Returns
    -------
    fit_params : numpy array
        Best-fit parameters to Psat(T) model
    fit_cov : numpy array
        Covariance matrix for fit parameters
    '''
    fit_params = np.zeros(3)
    fit_cov = np.zeros((3,3))

    try:
        # return zeros if no viable points
        datacut = (np.isnan(Psat)==False) & (Psat > 0.5e-12)
        if len(Psat[datacut])>3:
            fit_params, fit_cov = curve_fit(PsatofT, T[datacut], Psat[datacut], p0=[5e-10, 0.55, 3.])
        else:
            fit_params = 0
            fit_cov = 0
    except RuntimeError as err:
        print err
    return fit_params, fit_cov


def PsatofT(Tb, k, Tc, n):
    '''
    Functional form for fitting Psats as a function of bath temperature.

    Parameters
    ----------
    Tb : float
        Bath temperature [K]
    k : float
        Electron-phonon coupling
    Tc : float
        Critical temperature [K]
    n : float
        Exponent

    Returns
    -------
    power : float
        Net power transfer from TES to bath [W]
    '''
    power = k * (Tc**n - Tb**n)
    return power


def plot_PsatofT(T, Psat, fit_params, fit_errs, T_range=[0.2, 0.6]):
    '''
    Make plots of the results of the Psat(T) analysis.

    Parameters
    ----------
    T : numpy array
        Temperature data
    Psat : python dictionary
        Psat values corresponding to T, indexed by bolometer
    fit_params : python list
        Fit parameters from fit_PsatofT
    fit_errs : python list
        Fit parameter errors correspond to values in fit_params
    T_range : python list
        Min and max of temperature range to plot

    Returns
    -------
    fig : handle to figure
    '''
    ncols = np.ceil(np.sqrt(len(Psat)))
    if ncols == 0:
        nrows = 0
    else:
        nrows = np.ceil(len(Psat) / ncols)

    fig = plt.figure(figsize=(ncols*5., nrows*3.))
    plt.suptitle('$P=k({T_c}^n-{T_B}^n)$',fontsize=20,weight='bold')
    for jbolo, bolo in enumerate(fit_params):
        plt.subplot(nrows, ncols, jbolo+1)
        plt.plot(Psat[bolo]['T'], 1.0e12*(Psat[bolo]['Psat']), marker='o', color='k', linestyle='None')

        plot_T = np.linspace(T_range[0], T_range[1], 100)
        plot_Psat = PsatofT(plot_T, *fit_params[bolo])
        plt.plot(plot_T, 1.0e12*plot_Psat, color='b')
        plt.xlim(T_range)
        plt.ylim([-5, 1.2*np.min([100, np.max(1.0e12*plot_Psat)])])
        plt.grid(True)

        k = fit_params[bolo][0]
        Tc = fit_params[bolo][1]
        n = fit_params[bolo][2]
        PsatAt300mK = PsatofT(0.300, k, Tc, n)

        plt.xlabel('Bath Temperature [K]')
        plt.ylabel('Power on TES [pW]')
        ax = plt.gca()
        ax.annotate('k = %.0f$\pm$ %.0f' % (1e12*k, 1e12*fit_errs[bolo][0]),xy=(.05,.5),xycoords='axes fraction')
        ax.annotate('Tc = %.3fK$\pm$ %.3fK' % (Tc, fit_errs[bolo][1]),xy=(.05,.4),xycoords='axes fraction')
        ax.annotate('n = %.1f$\pm$ %.2f' % (n, fit_errs[bolo][2]),xy=(.05,.3),xycoords='axes fraction')
        ax.annotate('Psat(300mK) = %.1f pW' % (1e12*PsatAt300mK),xy=(.05,.2),xycoords='axes fraction')
        ax.annotate('G(Tc) = %.0f pW/K' % (1e12*n*k*(Tc**(n-1))),xy=(.05,.1),xycoords='axes fraction')
        ax.annotate(bolo, fontsize=14,xy=(.02,.89),xycoords='axes fraction')
    return fig
