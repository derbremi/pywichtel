import argparse
import asyncore

import pywichtel

if __name__ == "__main__":
    my_args = argparse.ArgumentParser()
    my_args.add_argument('-d',
                         dest='database',
                         type=str,
                         default=None,
                         help='Database file.')
    my_args.add_argument('-s',
                         dest='smtpstart',
                         action='store_true',
                         default=False,
                         help='Start SMTP server.')
    in_args = my_args.parse_args()

    # run wichtel
    wi = pywichtel.Wichtel()
    if in_args.database:
        wi.wichtel_it(in_args.database)
    if in_args.smtpstart:
        server = pywichtel.CustomSMTPServer(('127.0.0.1', 1025), None)
        asyncore.loop()
