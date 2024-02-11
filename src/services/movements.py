# -*- coding: utf-8 -*-

import json
import traceback
from datetime import datetime
from engines import redis_client
from utils.http import http_status_message
from schemas.movements import TransactionSchema


class MovementsService(object):
    def __init__(self, inputted_params: TransactionSchema = None, client_id: int = None) -> None:
        self.inputted_params = inputted_params
        self.client_id = client_id

    async def get_client_statement(self) -> tuple:
        """
        :return: http_status, http_message
        """
        try:
            if client_account := await self.get_client_position_account(client_id=self.client_id):
                balance = client_account.get('saldo')
                balance['data_extrato'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                last_operations = client_account.get('ultimas_transacoes')[0:10]
                return 200, {'saldo': balance, 'ultimas_transacoes': last_operations}
            else:
                return 404, f'404 - {await http_status_message(404)}'
        except Exception:
            traceback.print_exc()
            return 503, f'503 - {await http_status_message(503)}'

    async def get_client_position_account(self, client_id: int) -> dict:
        """
        :param: client_id: int
        :return: dict object with current client position
        """
        try:
            if current_client_position := await redis_client.get(f'user_{client_id}'):
                return json.loads(current_client_position)
            else:
                return {}
        except Exception:
            traceback.print_exc()
            return {}

    async def update_current_user_account_position(self) -> tuple:
        """
        :return: http_status, http_message
        """
        try:
            if client_account := await self.get_client_position_account(client_id=self.inputted_params.id):
                customer = client_account.get('cliente')
                balance = client_account.get('saldo')
                last_operations = client_account.get('ultimas_transacoes')
                if self.inputted_params.tipo == 'd' and \
                        (abs(self.inputted_params.valor) > customer.get('limite') or
                         abs(self.inputted_params.valor) > balance.get('limite')):
                    return 422, f'422 - {await http_status_message(422)}'
                if self.inputted_params.tipo == 'c':
                    balance['total'] += self.inputted_params.valor
                    balance['limite'] += self.inputted_params.valor
                    if balance['limite'] > customer['limite']:
                        balance['limite'] = customer['limite']
                    last_operations.insert(0, {
                        'valor': self.inputted_params.valor,
                        'tipo': self.inputted_params.tipo,
                        'descricao': self.inputted_params.descricao,
                        'realizada_em': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')})
                    await redis_client.set(f'user_{self.inputted_params.id}', json.dumps({
                        'cliente': customer,
                        'saldo': balance,
                        'ultimas_transacoes': last_operations}))
                    return 200, {'limite': balance['limite'], 'saldo': balance['total']}
                elif self.inputted_params.tipo == 'd':
                    balance['total'] += abs(self.inputted_params.valor) * -1
                    balance['limite'] += abs(self.inputted_params.valor) * -1
                    last_operations.insert(0, {
                        'valor': abs(self.inputted_params.valor),
                        'tipo': self.inputted_params.tipo,
                        'descricao': self.inputted_params.descricao,
                        'realizada_em': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')})
                    await redis_client.set(f'user_{self.inputted_params.id}', json.dumps({
                        'cliente': customer,
                        'saldo': balance,
                        'ultimas_transacoes': last_operations}))
                    return 200, {'limite': balance['limite'], 'saldo': balance['total']}
            else:
                return 404, f'404 - {await http_status_message(404)}'
        except Exception:
            traceback.print_exc()
            return 503, f'503 - {await http_status_message(503)}'
