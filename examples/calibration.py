# -*- coding: utf-8 -*-

import os
import yaml
import numpy as np

def make_freqs_amps(fdir):
    calib_file = 'calibration.yaml'

    with open(os.path.join(fdir, calib_file)) as file:
        calib = yaml.load(file)

    def get_freqs_amps(wnums):
        freqs = np.interp(wnums, calib['cm'], calib['MHz'])
        amps = np.interp(freqs, calib['power_MHz'], calib['power'])

        return freqs, amps

    return get_freqs_amps

def make_correction(fdir):
    calib_amp_file_sigma = 'Intensity_Correction_Sigma.txt'
    calib_amp_file_value = 'Intensity_Correction_Value.txt'

    sigma = np.loadtxt(os.path.join(fdir, calib_amp_file_sigma), delimiter=',')
    value = np.loadtxt(os.path.join(fdir, calib_amp_file_value), delimiter=',')

    return lambda x: np.interp(x, sigma, value)