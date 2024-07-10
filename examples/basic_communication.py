# -*- coding: utf-8 -*-
from libmozza.mozza import MozzaUSB

def test_basic_communication():
    with MozzaUSB() as mozza:
        # find connected Mozza devices
        serials = mozza.get_serials()
        if serials:
            print('Found Mozza device with serials: %r'%serials)
            mozza.connect(serial=serials[0])
            print()
            print('commands: \n\t%s'%'\n\t'.join(str(mozza.handle[0].cmd[i]) for i in range(mozza.handle[0].nbofcmds)))
            print('errors: \n\t%s'%'\n\t'.join(str(mozza.handle[0].error[i]) for i in range(mozza.handle[0].nboferrors)))
        else:
            print('No Mozza device is found')
        print(mozza.handle[0]) # prints commands, errors and default acq./process params

if __name__ == '__main__':
    import logging
    logging.getLogger().setLevel(logging.DEBUG)
    test_basic_communication()
