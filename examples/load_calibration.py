# -*- coding: utf-8 -*-
import numpy as np
from libmozza.mozza import MozzaUSB
from calibration import make_freqs_amps

def test_calibration(calib_dir):
    with MozzaUSB() as mozza:
        serials = mozza.get_serials()
        if serials:
            print('Found Mozza device with serials: %r'%serials)
            mozza.connect(serial=serials[0])

            get_freqs_amps = make_freqs_amps(calib_dir) # create freq/amp table generator

            wls_nm = (2500, 2550)
            wnums = np.arange(1e7/wls_nm[1], 1e7/wls_nm[0], 5)
            mozza.write_table(*get_freqs_amps(wnums))
            print(list(mozza.table))
        else:
            print('No Mozza device is found')

if __name__ == '__main__':
    import logging
    logging.getLogger().setLevel(logging.DEBUG)
    import os

    my_dir = os.path.join(os.path.dirname(__file__), '..\..', 'Calib')

    test_calibration(my_dir)