# -*- coding: utf-8 -*-

import fdb
import json
import traceback
from datetime import datetime
from flask import current_app
from utils.http import http_status_message
from schemas.movements import TransactionSchema


class MovementsService(object):
    def __init__(
            self,
            inputted_params: TransactionSchema = None,
            client_id: int = None,
            app_config: dict = None) -> None:
        self.inputted_params = inputted_params
        self.client_id = client_id
        self.app_config = app_config

    async def get_client_statement(self) -> tuple:
        """
        :return: http_status, http_message
        """
        try:
            if client_account := await self.get_client_position_account(client_id=self.client_id, limit=10):
                balance = client_account.get('saldo')
                balance['data_extrato'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                last_operations = client_account.get('ultimas_transacoes')
                return 200, {'saldo': balance, 'ultimas_transacoes': last_operations}
            else:
                return 404, f'404 - {await http_status_message(404)}'
        except Exception:
            traceback.print_exc()
            return 503, f'503 - {await http_status_message(503)}'

    async def get_client_position_account(self, client_id: int, limit: int = 1) -> dict:
        """
        :param: client_id: int
        :return: dict object with current client position
        """
        try:
            with fdb.connect(
                    dsn=self.app_config.get("FIREBIRD_DSN"),
                    user=self.app_config.get("FIREBIRD_USER"),
                    password=self.app_config.get("FIREBIRD_PASSWORD")) as connection:
                cursor = connection.cursor()
                rows = cursor.execute('''SELECT * FROM GET_MOVEMENTS(?)''', (client_id,)).fetchall()
                if rows:
                    last_operations = []
                    for row in list(filter(lambda x: (x[5] != "balance-0"), rows)):
                        last_operations.append({
                            'valor': int(row[8]),
                            'tipo': str(row[7]),
                            'descricao': str(row[5]),
                            'realizada_em': row[6].strftime('%Y-%m-%dT%H:%M:%S.%fZ')})
                    return {
                        'saldo': {
                            'total': int(rows[0][3]),
                            'limite': int(rows[0][4]),
                        },
                        'ultimas_transacoes': last_operations,
                        'cliente': {
                            'id': int(rows[0][1]),
                            'limite': int(rows[0][2])}
                    }
                else:
                    return {}
        except Exception:
            traceback.print_exc()
            return {}

    async def insert_new_operation(self, cli_id: int, trans_valor: int, trans_desc: str, trans_tipo: str) -> tuple:
        """
        :param cli_id: int
        :param trans_valor: int
        :param trans_desc: str
        :param trans_tipo: str
        :return: dict
        """
        try:
            with fdb.connect(
                    dsn=self.app_config.get("FIREBIRD_DSN"),
                    user=self.app_config.get("FIREBIRD_USER"),
                    password=self.app_config.get("FIREBIRD_PASSWORD")) as connection:
                cursor = connection.cursor()
                if trans_tipo == 'c':
                    try:
                        limite, saldo = cursor.execute('EXECUTE PROCEDURE INSERT_CREDIT_ON_MOVEMENTS(?, ?, ?)',
                                                       (cli_id, abs(trans_valor), trans_desc)).fetchone()
                        connection.commit()
                        return 200, {'limite': limite, 'saldo': saldo}
                    except fdb.fbcore.DatabaseError as e:
                        if 'CLIENT_NOT_FOUND' in e.args[0]:
                            return 404, f'404 - {await http_status_message(404)}'
                        else:
                            return 422, f'422 - {await http_status_message(422)}'
                elif trans_tipo == 'd':
                    try:
                        limite, saldo = cursor.execute('EXECUTE PROCEDURE INSERT_DEBIT_ON_MOVEMENTS(?, ?, ?)',
                                                       (cli_id, abs(trans_valor) * -1, trans_desc)).fetchone()
                        connection.commit()
                        return 200, {'limite': limite, 'saldo': saldo}
                    except fdb.fbcore.DatabaseError as e:
                        print(e.args[0])
                        if 'CLIENT_NOT_FOUND' in e.args[0]:
                            return 404, f'404 - {await http_status_message(404)}'
                        else:
                            return 422, f'422 - {await http_status_message(422)}'
        except Exception:
            traceback.print_exc()
            return 422, f'422 - {await http_status_message(422)}'

    async def update_current_user_account_position(self) -> tuple:
        """
        :return: http_status, http_message
        """
        try:
            status, message = await self.insert_new_operation(
                cli_id=self.inputted_params.id,
                trans_valor=self.inputted_params.valor,
                trans_desc=self.inputted_params.descricao,
                trans_tipo=self.inputted_params.tipo)
            return status, message
        except Exception:
            traceback.print_exc()
            return 503, f'503 - {await http_status_message(503)}'
