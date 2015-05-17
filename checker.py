#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Page Getter
"""
import requests
import re
from bs4 import BeautifulSoup
from config import ConfMixin


class PageChecker(ConfMixin):
    """
    Get the page and check match.
    """

    conf_section = 'Page'

    def __init__(self):
        self.url = self.conf.URL
        self.keywords = self.conf.KEYWORDS.split('\n')
        self.output_format = unicode(self.conf.OUTPUT_FORMAT)

    @property
    def formatted_keywords(self):
        return u", ".join(["'{}'".format(keyword)
                          for keyword in self.keywords])

    @staticmethod
    def _get_page_content(url):
        """
        Get the page
        """
        service_url = url
        try:
            res = requests.get(service_url, timeout=5)
        except:
            res = None
        if res:
            return res.content
        else:
            return u''

    @staticmethod
    def _check_match(word, content):
        """
        Get matched list.
        """
        soup = BeautifulSoup(content)
        return soup.find_all(text=re.compile(word))

    @staticmethod
    def _build_message(url, output_format, message_list, keywords):
        """
        Build message.
        """
        if message_list:
            matched_messages = u"".join([u"<li>{}</li>".format(message.strip())
                                        for message in message_list])
            return output_format.format(
                keywords=keywords,
                matched_messages=matched_messages,
                url=url
            )
        else:
            return u""

    def get_matched_message(self):
        """
        Loop keywords, fetch matched message.
        """
        page_content = self._get_page_content(self.url)
        matched_message_list = []
        for keyword in self.keywords:
            matched_list = [matched for matched in
                            self._check_match(keyword, page_content)
                            if keyword in matched]
            matched_message_list.extend(matched_list)
        return self._build_message(self.url,
                                   self.output_format,
                                   matched_message_list,
                                   self.formatted_keywords)
