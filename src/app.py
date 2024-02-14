# -*- coding: utf-8 -*-

import os
from quart import Quart
from controllers.movements import movements_bp

# app config
app = Quart(__name__)
app.config['APP_PATH'] = os.path.abspath(os.path.dirname(__file__))
app.config.from_pyfile(os.path.join(app.config['APP_PATH'], 'config.py'))

# blueprints
app.register_blueprint(movements_bp)
