""" Generate Wichtel combinations and send invitation via mail.
"""
import random
import hashlib
import time
import json
import os
# the following packages need to be installed
import sympy
import smtplib
import email.utils
from email.mime.text import MIMEText


class Wichtel():
    """
    The Wichtel class.
    """
    def __init__(self):
        # the valid combination
        self._combination = None


    def _read_database(self, database_file):
        # load database
        if os.path.isfile(database_file):
            self._database_file = database_file
            with open(self._database_file, 'r') as part:
                self._database = json.load(part)
            # initialize randomizer
            random.seed(time.time())
            # check if database already contains all possible combinations{}
            if len(self._database['hashtable']) == \
                sympy.subfactorial(len(self._database['participants'])):
                # keep the last entry of the hashtable and empty the rest
                self._database['hashtable'] = [self._database['hashtable'][-1]]
                print('New db')
            return True
        else:
            print('Invalid database {}'.format(database_file))
            return False
            
    def _create_combination(self):
        """
        create a single combination

        Returns:
            dict(combination): The combination
        """
        done = False
        while not done:
            # the combinations
            combination = dict()
            # the participants
            participants = set(self._database['participants'].keys())
            # select a wichtel for each participant
            for idx, first in enumerate(list(self._database['participants'].keys())):
                # choose single combination
                second = list(participants)[random.randint(0, len(participants)-1)]
                # single combination itself is valid
                combination.update({first: second})
                participants.remove(second)
            # assume we're finished here
            done = True
            # check if this is a valid combination
            for first in combination:
                second = combination[first]
                if first == second:
                    # somebody choose him/herself
                    done = False
        return combination
    
    def _send_mails(self):
        """
        Send mails to participants
        """
        for sender in self._combination:
            # get participants
            sender_mail = self._database['participants'][sender]
            receiver = self._combination[sender]
            receiver_mail = self._database['participants'][receiver]
            # create mail text
            msg = MIMEText('Hallo {0}!\n\nDein Wichtel ist {1}.\n\n'\
                'Viele Gruesse,\nDer Wichteladmin'
                .format(sender, receiver))
            # prepare message
            msg['To'] = email.utils.formataddr((sender, sender_mail))
            msg['From'] = email.utils.formataddr((self._database['admin_name'], self._database['admin_mail']))
            msg['Subject'] = 'Dein Wichtel'
            # send message
            #server = smtplib.SMTP('gmail-smtp-in.l.google.com', 25)
            server = smtplib.SMTP('localhost', 25)
            server.set_debuglevel(False)
            try:
                server.sendmail(self._database['admin_mail'], [sender_mail], msg.as_string())
            finally:
                server.quit()
    
    def wichtel_it(self, database_file):
        """
        Do the actual wichtel.
        """
        # read database 
        if self._read_database(database_file):
            # do wichteling
            hashes_found = list()
            while True:
                # create a combination
                combination = self._create_combination()
                self._combination = combination
                # create the hash
                hash_in = ';'.join(['{}-{}'.format(first,\
                    combination[first]) for first in combination])
                the_hash = hashlib.md5(str(hash_in).encode('utf-8')).hexdigest()
                # if the hash exists already in the database it means
                # that this combination already existed in the past years
                if the_hash not in self._database['hashtable']:
                    break
                else:
                    hashes_found.append(the_hash)
            # add new combination to database
            self._database['hashtable'].append(str(the_hash))
            # store new hash in database        
            with open(self._database_file, 'w') as part:
                json.dump(self._database, part, indent=4)
            # send mails
            self._send_mails()
