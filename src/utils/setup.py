# -*- coding: utf-8 -*-

import json
import traceback
from engines import redis_client
from schemas.client import ClientListSchema


async def create_users(users: list) -> None:
    """Create initial users"""
    try:
        validated_users = ClientListSchema(each_item=users)
        for user in validated_users.each_item:
            if cache := await redis_client.get(f'user_{user.id}'):
                print(f'UserId: {user.id} already was created\n'
                      f'Content {cache}', flush=True)
            else:
                await redis_client.set(f'user_{user.id}', json.dumps({
                    'cliente': {
                        'id': user.id,
                        'limite': user.limite},
                    'saldo': {
                        'total': 0,
                        'data_extrato': None,
                        'limite': user.limite
                    },
                    'ultimas_transacoes': []}))
    except Exception:
        traceback.print_exc()
