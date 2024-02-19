# -*- coding: utf-8 -*-

import os
from quart import Quart
from controllers.transactions import transactions_bp

# app config
app = Quart(__name__)
app.config['APP_PATH'] = os.path.abspath(os.path.dirname(__file__))

# blueprints
app.register_blueprint(transactions_bp)
