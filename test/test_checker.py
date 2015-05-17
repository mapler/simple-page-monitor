#!/usr/bin/env python
# -*- coding: utf-8 -*-
import responses
import requests
import unittest
from checker import PageChecker


class PageCheckerTestCase(unittest.TestCase):

    def setUp(self):
        self.checker = PageChecker()
        self.page_content = 'test_content'
        self.page_content2 = 'test_content2'
        self.default_url = 'http://aaa.com'
        self.output_format = '{keywords}{matched_messages}{url}'

    def _add_response_mock(self, url, body, status=200):
        responses.add(responses.GET, url,
                body=body, status=status,
                content_type='text/plain')

    def _add_response_exception_mock(self, url):
        responses.add(responses.GET, url,
                body=ValueError('test exception'))
 
    @responses.activate
    def test_get_page_content(self):
        url = self.default_url
        self._add_response_mock(url, self.page_content)
        assert self.page_content == self.checker._get_page_content(url)

    @responses.activate
    def test_get_page_content_error(self):
        url = self.default_url
        self._add_response_mock(url, self.page_content, status=404)
        assert '' == self.checker._get_page_content(url)

    @responses.activate
    def test_get_page_content_exception(self):
        url = self.default_url
        self._add_response_exception_mock(url)
        assert '' == self.checker._get_page_content(url)

    def test_build_message(self):
        message_list = ['a', 'b']
        keywords = ['test']
        output_message = self.checker._build_message(
            url=self.default_url,
            output_format=self.output_format,
            message_list=message_list,
            keywords=keywords)

        assert self.output_format.format(
            keywords=keywords,
            matched_messages=u"".join([u"<li>{}</li>".format(message.strip())
                                       for message in message_list]),
            url=self.default_url
        ) == output_message

    def test_build_message_fail(self):
        message_list = []
        keywords = ['test']
        output_message = self.checker._build_message(
            url=self.default_url,
            output_format=self.output_format,
            message_list=message_list,
            keywords=keywords)
        assert u"" == output_message

    @responses.activate
    def test_get_ip(self):
        url = self.default_url
        self.checker.keywords = ['test']
        self.checker.url = url
        self.checker.output_format = unicode(self.output_format)
        self._add_response_mock(url, self.page_content)
        output = self.output_format.format(
            keywords=self.checker.formatted_keywords,
            matched_messages='<li>test_content</li>',
            url=url,
        )
        assert output == self.checker.get_matched_message()
