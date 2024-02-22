# -*- coding: utf-8 -*-

import os
import traceback
from datetime import datetime
from sqlalchemy import text
from engines import db
from schemas.movements import TransactionSchema
from utils.http import http_status_message


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
            async with db.begin() as session:
                result = await session.execute(text('''
                    SELECT
                        row_to_json(posicao_cliente) AS posicao_cliente
                    FROM (
                        SELECT
                            jsonb_build_object(
                                'total', posicao_cliente.saldo_total,
                                'limite', posicao_cliente.saldo_limite,
                                'data_extrato', to_char(current_timestamp, 'YYYY-MM-DD"T"HH24:MI:SS.US"Z"')) as saldo,
                            (SELECT coalesce(json_agg(row_to_json(extrato_cliente)), '[]')
                             FROM (
                                 SELECT
                                     extrato_cliente.descricao AS descricao,
                                     extrato_cliente.tipo AS tipo,
                                     extrato_cliente.valor AS valor,
                                     to_char(extrato_cliente.realizada_em, 'YYYY-MM-DD"T"HH24:MI:SS.US"Z"') AS realizada_em
                                 FROM
                                     extrato_cliente
                                 WHERE
                                     extrato_cliente.cliente_id = :cliente_id
                                 ORDER BY extrato_cliente.realizada_em DESC
                                 LIMIT 10) extrato_cliente) AS ultimas_transacoes
                        FROM
                            posicao_cliente AS posicao_cliente
                        WHERE
                            posicao_cliente.cliente_id = :cliente_id) AS posicao_cliente'''), {'cliente_id': client_id})
                if result:
                    return result.fetchone()[0]
                else:
                    return {}
        except Exception:
            traceback.print_exc()
            return {}

    async def get_client_statement(self) -> tuple:
        """
        :return: http_status, http_message
        """
        try:
            if client_account := await self.get_client_position_account(client_id=self.client_id, limit=10):
                return 200, client_account
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
            async with db.begin() as session:
                if trans_tipo == 'c':
                    try:
                        await session.execute(text(f'select pg_advisory_xact_lock({cli_id})'))
                        result = await session.execute(
                            text('''SELECT INSERT_CREDIT(
                                :client_id, :trans_valor, :trans_desc, :trans_ref_date)'''),
                            {'client_id': cli_id,
                             'trans_valor': abs(trans_valor),
                             'trans_desc': trans_desc,
                             'trans_ref_date': datetime.now()})
                        if result:
                            return 200, result.fetchone()[0]
                        else:
                            return 422, f'422 - {await http_status_message(422)}'
                    except Exception as e:
                        if os.getenv('DEBUG') == 'true':
                            traceback.print_exc()
                        if 'Client not found' in e.args[0]:
                            return 404, f'404 - {await http_status_message(404)}'
                        else:
                            return 422, f'422 - {await http_status_message(422)}'
                elif trans_tipo == 'd':
                    try:
                        await session.execute(text(f'select pg_advisory_xact_lock({cli_id})'))
                        result_update_client_position = await session.execute(
                            text('SELECT INSERT_DEBIT(:client_id, :trans_valor, :trans_desc)'),
                            {'client_id': cli_id, 'trans_valor': abs(trans_valor) * -1, 'trans_desc': trans_desc})
                        result_update_client_position_json = result_update_client_position.fetchone()[0]
                        if result_update_client_position_json:
                            await session.execute(
                                text('''
                                    INSERT INTO EXTRATO_CLIENTE (DESCRICAO, TIPO, VALOR, CLIENTE_ID)
                                    VALUES (:trans_desc, 'd', :trans_valor, :client_id)'''),
                                {'client_id': cli_id, 'trans_valor': abs(trans_valor) * -1, 'trans_desc': trans_desc})
                            await session.commit()
                            return 200, result_update_client_position_json
                        else:
                            return 422, {'error': f'422 - {await http_status_message(422)}'}
                    except Exception as e:
                        traceback.print_exc()
                        if os.getenv('DEBUG') == 'true':
                            traceback.print_exc()
                        if 'Client not found' in e.args[0]:
                            return 404, {'error': f'404 - {await http_status_message(404)}'}
                        else:
                            return 422, {'error': f'422 - {await http_status_message(422)}'}
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
