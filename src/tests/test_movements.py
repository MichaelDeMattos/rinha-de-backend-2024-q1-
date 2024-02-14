# -*- coding: utf-8 -*-

import sys
import pytest
import os.path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from app import app as my_app


@pytest.fixture()
def app():
    app = my_app
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.mark.asyncio
async def test_client_not_found(client):
    """Test for not found client"""
    # GET
    resp = await client.get("/clientes/6/extrato")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_client_statement(client):
    """Test for not found client"""
    # GET
    resp = await client.get("/clientes/1/extrato")
    assert resp.status_code == 200
    resp = await client.get("/clientes/2/extrato")
    assert resp.status_code == 200
    resp = await client.get("/clientes/3/extrato")
    assert resp.status_code == 200
    resp = await client.get("/clientes/4/extrato")
    assert resp.status_code == 200
    resp = await client.get("/clientes/5/extrato")
    assert resp.status_code == 200
