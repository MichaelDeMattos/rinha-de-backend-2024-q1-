# -*- coding: utf-8 -*-
import os
import traceback
from engines import engine
from datetime import datetime
from sqlalchemy import text
from utils.http import http_status_message
from schemas.movements import TransactionSchema


class TransactionsService(object):
    def __init__(
            self,
            inputted_params: TransactionSchema = None,
            client_id: int = None,
            app_config: dict = None) -> None:
        self.inputted_params = inputted_params
        self.client_id = client_id
        self.app_config = app_config

    async def get_client_position_account(self, client_id: int, limit: int = 1) -> dict:
        """
        :param: client_id: int
        :return: dict object with current client position
        """
        try:
            async with engine.connect() as session:
                returning_object = {}
                result = await session.execute(text('''
                    select
                        pc.saldo_total as total,
                        to_char(current_timestamp, 'YYYY-MM-DD"T"HH24:MI:SS.US"Z"') as data_extrato,
                        pc.saldo_limite as limite,
                        ec.valor as valor,
                        ec.tipo as tipo,
                        ec.descricao as descricao,
                        to_char(ec.realizada_em, 'YYYY-MM-DD"T"HH24:MI:SS.US"Z"') as realizada_em
                    from posicao_cliente pc
                    left join extrato_cliente ec
                    on ec.cliente_id = pc.cliente_id
                    where pc.cliente_id = :cliente_id
                    order by ec.realizada_em desc
                    limit 10'''), {'cliente_id': client_id})
                if result:
                    rows = result.fetchall()
                    for index, row in enumerate(rows):
                        total, data_extrato, limite, valor, tipo, descricao, realizada_em = row
                        if index == 0:
                            returning_object.update({
                                'saldo': {
                                    'total': total,
                                    'data_extrato': data_extrato,
                                    'limite': limite}})
                            if valor and tipo and descricao and realizada_em:
                                returning_object.update({
                                    'ultimas_transacoes': [{
                                        'valor': valor,
                                        'tipo': tipo,
                                        'descricao': descricao,
                                        'realizada_em': realizada_em}]})
                            else:
                                returning_object.update({'ultimas_transacoes': []})
                        else:
                            returning_object['ultimas_transacoes'].append({
                                'valor': valor,
                                'tipo': tipo,
                                'descricao': descricao,
                                'realizada_em': realizada_em})
                    return returning_object
                else:
                    return returning_object
        except Exception:
            traceback.print_exc()
            return {}

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

    async def insert_new_operation(self, cli_id: int, trans_valor: int, trans_desc: str, trans_tipo: str) -> tuple:
        """
        :param cli_id: int
        :param trans_valor: int
        :param trans_desc: str
        :param trans_tipo: str
        :return: dict
        """
        try:
            async with engine.connect() as session:
                if trans_tipo == 'c':
                    try:
                        result = await session.execute(
                            text('''SELECT * FROM INSERT_CREDIT(
                                :client_id, :trans_valor, :trans_desc, :trans_ref_date)'''),
                            {'client_id': cli_id,
                             'trans_valor': abs(trans_valor),
                             'trans_desc': trans_desc,
                             'trans_ref_date': datetime.now()})
                        limite, saldo = result.fetchone()
                        return 200, {'limite': limite, 'saldo': saldo}
                    except Exception as e:
                        if os.getenv('DEBUG') == 'true':
                            traceback.print_exc()
                        if 'Client not found' in e.args[0]:
                            return 404, f'404 - {await http_status_message(404)}'
                        else:
                            return 422, f'422 - {await http_status_message(422)}'
                elif trans_tipo == 'd':
                    try:
                        result = await session.execute(
                            text('SELECT * FROM INSERT_DEBIT(:client_id, :trans_valor, :trans_desc)'),
                            {'client_id': cli_id, 'trans_valor': abs(trans_valor) * -1, 'trans_desc': trans_desc})
                        limite, saldo = result.fetchone()
                        return 200, {'limite': limite, 'saldo': saldo}
                    except Exception as e:
                        if os.getenv('DEBUG') == 'true':
                            traceback.print_exc()
                        if 'Client not found' in e.args[0]:
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
            if result := await self.insert_new_operation(
                    cli_id=self.inputted_params.id,
                    trans_valor=self.inputted_params.valor,
                    trans_desc=self.inputted_params.descricao,
                    trans_tipo=self.inputted_params.tipo):
                return result[0], result[1]
            else:
                return 422, f'422 - {await http_status_message(422)}'
        except Exception:
            traceback.print_exc()
            return 503, f'503 - {await http_status_message(503)}'
