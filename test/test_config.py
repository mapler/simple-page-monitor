#!/usr/bin/env python
# -*- coding: utf-8 -*-
import responses
import requests
from config import ConfParser, Conf, ConfMixin
 

def test_conf():
    global_conf = Conf(ConfParser(), 'Global')
    assert global_conf.SENDERS == 'Output\nFile'
    class TestConfKlass(ConfMixin):
        conf_section = 'Mailgun'
    test_conf_obj = TestConfKlass()
    assert test_conf_obj.conf.SUBJECT == 'Simple Page Monitor Notifier'
