# -*- coding: utf-8 -*-

import os
import json
import asyncio
from app import app
from pathlib import Path
from dotenv import load_dotenv
from utils.setup import make_initial_setup

if __name__ == '__main__':
    load_dotenv(dotenv_path=os.path.join(Path(__file__).parent.parent, '.env'))
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'users.json')) as users_file:
        users = json.loads(users_file.read())
        asyncio.run(make_initial_setup(users=users))
    app.run(debug=True)
