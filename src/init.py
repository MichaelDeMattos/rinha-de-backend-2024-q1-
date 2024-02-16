# -*- coding: utf-8 -*-

import os
import json
import asyncio
import traceback
import subprocess
from utils.setup import make_initial_setup


async def setup():
    """Make initial setup"""
    if os.getenv('INSTANCE_NAME') == 'api_instance_a':
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'users.json')) as users_file:
            users = json.loads(users_file.read())
            await make_initial_setup(users=users)


if __name__ == '__main__':
    try:
        asyncio.run(setup())
        subprocess.call(
            f'hypercorn --bind="{os.getenv("INSTANCE_BIND")}" '
            f'--workers={os.getenv("INSTANCE_WORKERS")} --max-requests 999999 --worker-class uvloop app:app', shell=True)
    except Exception:
        traceback.print_exc()
