# -*- coding: utf-8 -*-

import os
import json
import asyncio
import traceback
import subprocess
from utils.setup import create_users


async def setup():
    """Make initial setup"""
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'users.json')) as users_file:
        users = json.loads(users_file.read())
        await create_users(users)


if __name__ == '__main__':
    try:
        asyncio.run(setup())
        subprocess.call(
            f'hypercorn --bind="{os.getenv("INSTANCE_BIND")}" '
            f'--workers={os.getenv("INSTANCE_WORKERS")} app:app', shell=True)
    except Exception:
        traceback.print_exc()
