#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sender Strategies.
"""
import smtplib
import requests
import sys
from config import ConfMixin
from abc import ABCMeta, abstractmethod


class SenderError(Exception):
    """Errors when send IP."""
    pass


class SenderConfError(SenderError):
    """Errors when sender config Valid."""
    pass


class SenderBase(object):
    """
    Base class of Senders
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def send(self, message):
        """
        Sender strategy interface.
        """
        raise NotImplementedError


class Output(SenderBase, ConfMixin):
    """
    Print out.
    """

    conf_section = 'Output'

    def output(self, ostream, message):
        """
        Change stdout to some ostream, 
        output message, and restore stdout.
        """
        saved_stdout = sys.stdout
        sys.stdout = ostream
        print message
        sys.stdout = saved_stdout

    def send(self, message):
        ostream = sys.stdout
        self.output(ostream, message)


class FileOutput(Output):
    """
    Save to File.
    """

    conf_section = 'File'

    def send(self, message):
        """
        Overwrite ostream with a file, output message.
        """
        with open(self.conf.FILE_PATH, 'w') as f:
            self.output(f, message.decode('utf8'))


class MailSender(SenderBase, ConfMixin):
    """
    Send by smtp lib.
    """

    conf_section = 'Mail'

    def __init__(self):
        self.server = smtplib.SMTP_SSL(self.conf.HOST, self.conf.PORT)
        self.server.ehlo()
        self.server.starttls()
        self.server.login(self.conf.USER, self.conf.PASS)

    def send(self, message):
        message = """\nFrom: {}\nTo: {}\nSubject: {}\n\n{}""".format(self.conf.FROM,
                                                                    self.conf.TO,
                                                                    self.conf.SUBJECT,
                                                                    unicode(message))
        self.server.sendmail(self.conf.FROM, self.conf.TO, message)
        self.server.close()
        print 'sent mail:', message


class Mailgun(SenderBase, ConfMixin):
    """
    Send by mailgun.com
    """
    conf_section = 'Mailgun'

    def __init__(self):
        self.url = self.conf.API_BASE_URL + '/messages'

    def send(self, message):
        auth = ('api', self.conf.KEY)
        data = {'from': self.conf.FROM,
                'to': [self.conf.TO],
                'subject': self.conf.SUBJECT,
                'text': unicode(message)}
        ret = requests.post(self.url, auth=auth, data=data)
        ret.raise_for_status()


class CustomSender(SenderBase, ConfMixin):
    """
    Custom Sender
    You can write your sender here for some DNS Service.
    """
    conf_section = 'Custom'

    def send(self, message):
        pass


SENDERS = {
    'Mail': MailSender,
    'Mailgun': Mailgun,
    'Output': Output,
    'File': FileOutput,
    'Custom': CustomSender,
}


class SenderManager(ConfMixin):
    """
    Keep a broadcast list and send messages.
    """
    conf_section = 'Global'

    def __init__(self):
        self.senders = []
        self.methods = self.conf.SENDERS.split('\n')

    def add_sender(self, sender):
        """
        Add sender to broadcast list.
        """
        self.senders.append(sender)

    def set_senders(self):
        for sender in self.methods:
            if sender in SENDERS:
                self.add_sender(SENDERS[sender]())
            else:
                raise SenderConfError('Unknown sender method {}.'.format(sender))

    def check_message_repeated(self, message):
        """
        check if message repeated
        available when 'File' sender is On
        """
        file_sender = SENDERS['File']()
        try:
            f = open(file_sender.conf.FILE_PATH, 'r')
        except (IOError, OSError) as e:
            # Saved File does not exist, Stop checking, and return False
            return False
        else:
            try:
                saved_message = f.read().strip()
            finally:
                f.close()
        return bool(saved_message == message)

    def send(self, message):
        """
        Broadcast the message
        """
        if not self.check_message_repeated(message):
            self.set_senders()
            for sender in self.senders:
                try:
                    sender.send(message)
                except Exception as error:
                    print error.message
        else:
            print "'{}' again. Stop sending.".format(message)

