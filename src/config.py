# -*- coding: utf-8 -*-

import os

APP_PATH = os.path.abspath(os.path.dirname(__file__))
FIREBIRD_DSN = os.getenv('FIREBIRD_DSN')
FIREBIRD_USER = os.getenv('FIREBIRD_USER')
FIREBIRD_PASSWORD = os.getenv('FIREBIRD_PASSWORD')
