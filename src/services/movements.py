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

    async def insert_new_operation(
            self,
            cli_id: int,
            cli_lim_org: int,
            saldo_total: int,
            saldo_lim: int,
            utl_trans_desc: str,
            utl_trans_tipo: str,
            utl_trans_valor: int) -> bool:
        """
        :param cli_id: int
        :param cli_lim_org: int
        :param saldo_total: int
        :param saldo_lim: int
        :param utl_trans_desc: str
        :param utl_trans_tipo: str
        :param utl_trans_valor: int
        :return: bool
        """
        try:
            with fdb.connect(
                    dsn=self.app_config.get("FIREBIRD_DSN"),
                    user=self.app_config.get("FIREBIRD_USER"),
                    password=self.app_config.get("FIREBIRD_PASSWORD")) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    'INSERT INTO MOVEMENTS'
                    ' (CLI_ID, CLI_LIM_ORG, SALDO_TOTAL,'
                    '  SALDO_LIM, UTL_TRANS_DESC, UTL_TRANS_REAL_EM,'
                    '  UTL_TRANS_TIPO, UTL_TRANS_VALOR)'
                    '  VALUES'
                    ' (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?)',
                    (cli_id, cli_lim_org, saldo_total, saldo_lim, utl_trans_desc, utl_trans_tipo, utl_trans_valor))
                connection.commit()
                return True
        except Exception:
            traceback.print_exc()
            return False

    async def update_current_user_account_position(self) -> tuple:
        """
        :return: http_status, http_message
        """
        try:
            if client_account := await self.get_client_position_account(client_id=self.inputted_params.id):
                customer = client_account.get('cliente')
                balance = client_account.get('saldo')
                last_operations = client_account.get('ultimas_transacoes')
                # not limit for debit operation
                if self.inputted_params.tipo == 'd' and \
                    abs(self.inputted_params.valor) > balance.get('total') and \
                    (abs(self.inputted_params.valor) > customer.get('limite') or
                     abs(self.inputted_params.valor) > balance.get('limite')):
                    return 422, f'422 - {await http_status_message(422)}'
                if self.inputted_params.tipo == 'c':
                    balance['total'] += abs(self.inputted_params.valor)
                    balance['limite'] += abs(self.inputted_params.valor)
                    if balance['limite'] > customer['limite']:
                        balance['limite'] = customer['limite']
                    await self.insert_new_operation(
                        cli_id=self.inputted_params.id,
                        cli_lim_org=customer.get('limite'),
                        saldo_total=balance.get('total'),
                        saldo_lim=balance.get('limite'),
                        utl_trans_desc=self.inputted_params.descricao,
                        utl_trans_tipo=self.inputted_params.tipo,
                        utl_trans_valor=self.inputted_params.valor)
                    return 200, {'limite': balance['limite'], 'saldo': balance['total']}
                elif self.inputted_params.tipo == 'd':
                    if abs(self.inputted_params.valor) > balance['total']:
                        balance['limite'] += abs(self.inputted_params.valor) * -1
                    balance['total'] += abs(self.inputted_params.valor) * -1
                    await self.insert_new_operation(
                        cli_id=self.inputted_params.id,
                        cli_lim_org=customer.get('limite'),
                        saldo_total=balance.get('total'),
                        saldo_lim=balance.get('limite'),
                        utl_trans_desc=self.inputted_params.descricao,
                        utl_trans_tipo=self.inputted_params.tipo,
                        utl_trans_valor=self.inputted_params.valor)
                    return 200, {'limite': balance['limite'], 'saldo': balance['total']}
            else:
                return 404, f'404 - {await http_status_message(404)}'
        except Exception:
            traceback.print_exc()
            return 503, f'503 - {await http_status_message(503)}'
