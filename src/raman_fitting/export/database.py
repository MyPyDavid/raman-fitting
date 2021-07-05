#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 16:15:25 2021

@author: zmg
"""

import sqlite3

from ..config import config


class RamanDB:
    def __init__(self):
        self.dbpath = config.RESULTS_DIR.joinpath("sqlite.db")

    def conn(self):
        self.conn = sqlite3.connect(self.dbpath)
