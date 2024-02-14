# -*- coding: utf-8 -*-

import os
import fdb
import traceback
from schemas.client import ClientListSchema, ClientSchema

FIREBIRD_DSN = os.getenv('FIREBIRD_DSN')
FIREBIRD_USER = os.getenv('FIREBIRD_USER')
FIREBIRD_PASSWORD = os.getenv('FIREBIRD_PASSWORD')


async def create_user(user: ClientSchema) -> bool:
    """
    :return:
    """
    try:
        with fdb.connect(dsn=FIREBIRD_DSN, user=FIREBIRD_USER, password=FIREBIRD_PASSWORD) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO MOVEMENTS"
                " (CLI_ID, CLI_LIM_ORG, SALDO_TOTAL,"
                "  SALDO_LIM, UTL_TRANS_DESC, UTL_TRANS_REAL_EM,"
                "  UTL_TRANS_TIPO, UTL_TRANS_VALOR)"
                "  VALUES"
                f" ({user.id}, {user.limite}, 0, {user.limite}, 'balance-0', CURRENT_TIMESTAMP, 'c', 0)")
            connection.commit()
            return True
    except Exception:
        traceback.print_exc()
        return False


async def create_table() -> bool:
    """
    :return:
    """
    try:
        with fdb.connect(dsn=FIREBIRD_DSN, user=FIREBIRD_USER, password=FIREBIRD_PASSWORD) as connection:
            cursor = connection.cursor()
            # drop old table
            try:
                cursor.execute('DROP TABLE MOVEMENTS')
                connection.commit()
            except Exception:
                pass
            # create empty table
            cursor.execute('''
                CREATE TABLE MOVEMENTS (
                    ID INTEGER GENERATED BY DEFAULT AS IDENTITY NOT NULL,
                    CLI_ID INTEGER NOT NULL,
                    CLI_LIM_ORG INTEGER NOT NULL,
                    SALDO_TOTAL INTEGER NOT NULL,
                    SALDO_LIM INTEGER NOT NULL CHECK (SALDO_LIM > 0),
                    UTL_TRANS_DESC VARCHAR(10),
                    UTL_TRANS_REAL_EM TIMESTAMP NOT NULL,
                    UTL_TRANS_TIPO CHAR(1) CHECK (UTL_TRANS_TIPO IN ('c', 'd')),
                    UTL_TRANS_VALOR INTEGER,
                    CONSTRAINT MOV_PK PRIMARY KEY (ID))''')
            cursor.execute(
                'ALTER TABLE MOVEMENTS ALTER COLUMN UTL_TRANS_REAL_EM SET DEFAULT CURRENT_TIMESTAMP')
            connection.commit()
            return True
    except Exception:
        traceback.print_exc()
        return False


async def make_initial_setup(users: list) -> None:
    """Create initial users"""
    try:
        if await create_table():
            validated_users = ClientListSchema(each_item=users)
            for user in validated_users.each_item:
                if await create_user(user=user):
                    print(f'User: {user.id} was created in database with successfully!!!')
    except Exception:
        traceback.print_exc()
