# -*- coding: utf-8 -*-

import json
import traceback
from pydantic import ValidationError
from utils.http import http_status_message
from schemas.movements import TransactionSchema
from services.movements import MovementsService
from quart import Blueprint, make_response, jsonify, request

movements_bp = Blueprint('movements', __name__)


@movements_bp.route('/clientes/<int:client_id>/transacoes', methods=['POST'])
async def transactions_api(client_id: int) -> make_response:
    """
    :param client_id: int = client_id
    :return: make_response = http_response
    """
    try:
        body = await request.data
        body_parse = json.loads(body)
        body_parse.update({'id': client_id})
        validated_inputted_params = TransactionSchema(**body_parse)
        movements_object = MovementsService(inputted_params=validated_inputted_params)
        http_status, http_message = await movements_object.update_current_user_account_position()
        return await make_response(
            jsonify(http_message) if http_status == 200 else http_message, http_status)
    except ValidationError as e:
        traceback.print_exc()
        return await make_response(jsonify({
            'response': f'400 - {await http_status_message(400)}',
            'reason': e.errors(),
            'status': 400}), 400)
    except Exception:
        traceback.print_exc()
        return await make_response(jsonify({
            'response': f'503 - {await http_status_message(503)}',
            'status': 503}), 503)


@movements_bp.route('/clientes/<int:client_id>/extrato', methods=['GET'])
async def statement_api(client_id: int) -> make_response:
    """
    :param client_id: int = client_id
    :return: make_response = http_response
    """
    try:
        movements_object = MovementsService(client_id=client_id)
        http_status, http_message = await movements_object.get_client_statement()
        return await make_response(
            jsonify(http_message) if http_status == 200 else http_message, http_status)
    except Exception:
        traceback.print_exc()
        return await make_response(jsonify({
            'response': f'503 - {await http_status_message(503)}',
            'status': 503}), 503)
