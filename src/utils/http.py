# -*- coding: utf-8 -*-

from werkzeug.http import HTTP_STATUS_CODES


async def http_status_message(code: int) -> str:
    """Maps an HTTP status code to the textual status"""
    return HTTP_STATUS_CODES.get(code, '')
