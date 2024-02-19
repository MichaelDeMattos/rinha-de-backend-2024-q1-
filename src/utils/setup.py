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
            await session.execute(text(
                "INSERT INTO POSICAO_CLIENTE"
                " (CLIENTE_ID, CLIENTE_LIMITE, SALDO_LIMITE, SALDO_TOTAL)"
                "  VALUES"
                " (:user_id, :user_limite, :user_limite, 0)"),
                {"user_id": user.id, "user_limite": user.limite})
            await session.commit()
        return True
    except Exception:
        traceback.print_exc()
        return False


async def remove_old_data_from_movements_table() -> bool:
    """Remove old data from Movements table"""
    try:
        async with engine.connect() as session:
            await session.execute(text('DELETE FROM EXTRATO_CLIENTE'))
            await session.execute(text('DELETE FROM POSICAO_CLIENTE'))
            await session.commit()
            return True
    except Exception:
        traceback.print_exc()
        return False


async def make_initial_setup(users: list) -> None:
    """Create initial users"""
    try:
        validated_users = ClientListSchema(each_item=users)
        if await remove_old_data_from_movements_table():
            for user in validated_users.each_item:
                if await create_user(user=user):
                    print(f'User: {user.id} was created in database with successfully!!!')
        await engine.dispose()
    except Exception:
        traceback.print_exc()
