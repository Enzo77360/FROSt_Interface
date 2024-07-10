# -*- coding: utf-8 -*-
import logging
logging.basicConfig(level=logging.DEBUG)
from libmozza.mozza import MozzaUSB

def test_basic_timings():
    with MozzaUSB() as mozza:
        # find connected Mozza devices
        serials = mozza.get_serials()
        if serials:
            print('Found Mozza device with serials: %r'%serials)
            mozza.connect(serial=serials[0])
            freq_kHz = mozza.get_trigger_frequency()*1e-3
            print('Mozza external trigger frequency: %.1f kHz'%freq_kHz)
        else:
            print('No Mozza device is found')

if __name__ == '__main__':
    import logging
    logging.getLogger().setLevel(logging.DEBUG)
    test_basic_timings()