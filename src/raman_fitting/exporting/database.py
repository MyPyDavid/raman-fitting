#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 16:15:25 2021

@author: zmg
"""

import sqlite3

from raman_fitting.config import filepath_settings


class RamanDB:
    def __init__(self):
        self.dbpath = filepath_settings.RESULTS_DIR.joinpath("sqlite.db")

    def conn(self):
        self.conn = sqlite3.connect(self.dbpath)
