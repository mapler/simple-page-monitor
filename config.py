#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Config File Wrapper
"""
from ConfigParser import ConfigParser

CONF_PATH = './config.ini'


class ConfParser(object):
    """
    ConfigParser of a config File.
    """
    def __init__(self, path=None):
        self._conf_path = path if path else CONF_PATH
        self.parser = ConfigParser()
        self.parser.read(self._conf_path)


class Conf(object):
    """
    Wrap ConfigParser as a 'constant'.
    """
    def __init__(self, confparser, section):
        self.confparser = confparser.parser
        self.section = section

    def __getattr__(self, key):
        return self.confparser.get(self.section, key)


CONFPARSER = ConfParser(CONF_PATH)


class ConfMixin(object):
    """
    Config Mixin for class which use config.
    """
    conf_section = None

    @property
    def conf(self):
        """
        the config 'constant'
        """
        return Conf(CONFPARSER, self.conf_section)
