#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sender import SenderManager
from checker import PageChecker

if __name__ == '__main__':
    checker = PageChecker()
    matched_message = checker.get_matched_message()
    if matched_message:
        sender_manager = SenderManager()
        sender_manager.send(matched_message)
