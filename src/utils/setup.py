# -*- coding: utf-8 -*-

import traceback
from engines import engine
from sqlalchemy import text
from schemas.client import ClientListSchema, ClientSchema


async def create_user(user: ClientSchema) -> bool:
    """
    :return:
    """
    try:
        async with engine.connect() as session:
            await session.execute(text('DELETE FROM MOVEMENTS'))
            await session.execute(text(
                "INSERT INTO MOVEMENTS"
                " (CLI_ID, CLI_LIM_ORG, SALDO_TOTAL,"
                "  SALDO_LIM, UTL_TRANS_DESC, UTL_TRANS_REAL_EM,"
                "  UTL_TRANS_TIPO, UTL_TRANS_VALOR)"
                "  VALUES"
                " (:user_id, :user_limite, 0, :user_limite, 'balance-0', CURRENT_TIMESTAMP, 'c', 0)"),
                {"user_id": user.id, "user_limite": user.limite})
            await session.commit()
        await engine.dispose()
        return True
    except Exception:
        traceback.print_exc()
        return False


async def make_initial_setup(users: list) -> None:
    """Create initial users"""
    try:
        validated_users = ClientListSchema(each_item=users)
        for user in validated_users.each_item:
            if await create_user(user=user):
                print(f'User: {user.id} was created in database with successfully!!!')
    except Exception:
        traceback.print_exc()
