# -*- coding: utf-8 -*-
import sys, os
sys.path.append('.') 
import numpy as np
from libmozza import mozza_defines as MD
from libmozza.mozza import MozzaUSB, MozzaError
import struct

def test_acquisition():
    with MozzaUSB() as mozza:
        serials = mozza.get_serials()
        if serials:
            print('Found Mozza device with serials: %r'%serials)
            mozza.connect(serial=serials[0])

            print(struct.unpack('q', mozza.handle))
            print(mozza.handle[0])

            wls_nm = (2000, 6000)
            wnums = np.arange(1e7/wls_nm[1], 1e7/wls_nm[0], 5)
            mozza.set_wavenumber_array(wnums)
            mozza.acquisition_params.trigger_source = MD.INTERNAL
            mozza.acquisition_params.trigger_frequency_Hz = 10000
            mozza.set_auto_params()

            print(mozza.acquisition_params)
            print(mozza.process_params)

            bytes_to_read = mozza.begin_acquisition()
            print('bytes_to_read: %d'%bytes_to_read)
            try:
                raw = mozza.read_raw()
            except MozzaError as e:
                print(e)
            signal, reference = mozza.separate_sig_ref(raw)
            try:
                mozza.end_acquisition()
            except MozzaError as e:
                print(e)
            spectrum = mozza.process_spectrum(sig_data=signal,
                                              ref_data=reference)
            return (wnums, spectrum, signal, reference)
        else:
            print('No Mozza device is found')
            return None

if __name__ == '__main__':
    import os
    import logging
    import pylab as plt
    logging.getLogger().setLevel(logging.DEBUG)
    
    
    result = test_acquisition()
    if result is not None:
        wnums, data, signal, reference = result

        fig, ax = plt.subplots(2,1)
        ax[0].plot(wnums, data)
        ax[0].set_xlabel('wavenumber [cm$^{-1}$]')
        ax[0].set_ylabel('intensity [arb. units]')
        ax[0].grid()

        smean, sstd = np.mean(signal), np.std(signal)
        rmean, rstd = np.mean(reference), np.std(reference)
        ax[1].plot(signal, label='signal mean=%.0f$\pm$%.1f'%(smean, sstd))
        ax[1].plot(reference, label='reference mean=%.0f$\pm$%.1f'%(rmean, rstd))
        ax[1].grid()
        ax[1].legend()

        fig.savefig('mozza.png')

        plt.show()
    else :
        print('No Mozza device is found')