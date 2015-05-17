#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sender import (
        Output,
        FileOutput,
        SenderManager,
        SenderConfError,
        SENDERS,
    )
import unittest
import mock
import sys
import os
import shutil


class OutputTestCase(unittest.TestCase):

    def setUp(self):
        self.output_sender = Output()

    def test_output(self):
        self.output_sender.output(sys.stdout, 'test')
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")  # pragma: no cover
        output = sys.stdout.getvalue().strip()
        assert 'test' == output

    def test_send(self):
        self.output_sender.send('test')
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")  # pragma: no cover
        output = sys.stdout.getvalue().strip()
        assert 'test' == output


class FileOutputTestCase(unittest.TestCase):

    def setUp(self):
        self.file_output = FileOutput()

    def tearDown(self):
        open(self.file_output.conf.FILE_PATH, 'w').close()

    def test_send(self):
        test_message = 'test message'
        self.file_output.send(test_message)
        with open(self.file_output.conf.FILE_PATH, 'r') as f:
            saved_message = f.read().strip()
            assert test_message == saved_message

class SenderManagerTestCase(unittest.TestCase):

    def setUp(self):
        self.sender_manager = SenderManager()

    def tearDown(self):
        file_path = SENDERS['File']().conf.FILE_PATH
        open(file_path, 'w').close()

    def test_add_sender(self):
        sender1 = 'fake_sender'
        sender2 = 'fake_sender2'
        self.sender_manager.add_sender(sender1)
        assert self.sender_manager.senders == [sender1]
        self.sender_manager.add_sender(sender2)
        assert self.sender_manager.senders == [sender1, sender2]

    def test_set_senders(self):
        self.sender_manager.methods = ['File', 'Output', 'Mailgun']
        self.sender_manager.set_senders()
        assert sorted([sender.__class__ for sender in self.sender_manager.senders]) == sorted([SENDERS['File'], SENDERS['Output'], SENDERS['Mailgun']])

    def test_set_senders_exception(self):
        self.sender_manager.methods = ['Fake']
        self.assertRaises(SenderConfError, self.sender_manager.set_senders)

    def test_send(self):
        self.sender_manager.methods = ['Output', 'File']
        self.sender_manager.send('test')
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")  # pragma: no cover
        output = sys.stdout.getvalue().strip()
        assert 'test' == output
        for sender in self.sender_manager.senders:
            if hasattr(sender.conf, 'FILE_PATH'):
                file_path = sender.conf.FILE_PATH
        with open(file_path, 'r') as f:
            saved_message = f.read().strip()
            assert 'test' == saved_message

    def test_send_exception(self):
        exception_message = 'test exception'
        self.sender_manager.methods = ['Mailgun']
        self.sender_manager.set_senders()
        for sender in self.sender_manager.senders:
            sender.send = mock.MagicMock(side_effect=ValueError(exception_message))
        self.sender_manager.set_senders = mock.Mock(return_value=None)
        self.sender_manager.send('test')
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")  # pragma: no cover
        output = sys.stdout.getvalue().strip()
        assert exception_message == output

    def test_send_check_message_repeated(self):
        file_path = SENDERS['File']().conf.FILE_PATH
        test_message = 'test'
        with open(file_path, 'w') as f:
            f.write(test_message)
        is_repeated = self.sender_manager.check_message_repeated(test_message)
        assert is_repeated == True

    def test_send_check_message_repeated_fail(self):
        file_path = SENDERS['File']().conf.FILE_PATH
        test_message_1 = 'test'
        test_message_2 = 'test2'
        with open(file_path, 'w') as f:
            f.write(test_message_1)
        is_repeated = self.sender_manager.check_message_repeated(test_message_2)
        assert is_repeated == False

    def test_send_check_message_repeated_when_file_not_exist(self):
        file_path = SENDERS['File']().conf.FILE_PATH
        bak_path = file_path + '.bak'
        shutil.copyfile(file_path, bak_path)
        os.remove(file_path)
        test_message = 'test'
        is_repeated = self.sender_manager.check_message_repeated(test_message)
        assert is_repeated == False
        shutil.copyfile(bak_path, file_path)
        os.remove(bak_path)

    def test_send_when_repeated(self):
        self.sender_manager.methods = ['File']
        self.sender_manager.set_senders()
        self.sender_manager.send('test')
        if not hasattr(sys.stdout, "getvalue"):
            self.fail("need to run in buffered mode")  # pragma: no cover
        self.sender_manager.send('test')
        output = sys.stdout.getvalue().strip()
        assert "'{}' again. Stop sending.".format('test') == output

