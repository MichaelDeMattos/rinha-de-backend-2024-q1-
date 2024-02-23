# -*- coding: utf-8 -*-

import random
from locust import HttpUser, task, constant


class QuickstartUser(HttpUser):
    wait_time = constant(0)
    host = 'http://localhost:5000'

    @task
    def test_get_statement_client_ok(self):
        req = self.client.get(f'/clientes/{random.randint(1, 5)}/extrato')
        assert req.status_code == 200

    @task
    def test_debit_operation_for_client_01(self):
        req = self.client.post(f'/clientes/1/transacoes', json={
            'valor': random.randint(1, 9999),
            'tipo': ['c', 'd'][random.randint(0, 1)],
            'descricao': ['pix', 'ted', 'doc', 'remessa'][random.randint(0, 3)]})
        assert req.status_code in (422, 200)

    @task
    def test_debit_operation_for_client_02(self):
        req = self.client.post(f'/clientes/2/transacoes', json={
            'valor': random.randint(1, 9999),
            'tipo': ['c', 'd'][random.randint(0, 1)],
            'descricao': ['pix', 'ted', 'doc', 'remessa'][random.randint(0, 3)]})
        assert req.status_code in (422, 200)

    @task
    def test_debit_operation_for_client_03(self):
        req = self.client.post(f'/clientes/3/transacoes', json={
            'valor': random.randint(1, 9999),
            'tipo': ['c', 'd'][random.randint(0, 1)],
            'descricao': ['pix', 'ted', 'doc', 'remessa'][random.randint(0, 3)]})
        assert req.status_code in (422, 200)

    @task
    def test_debit_operation_for_client_04(self):
        req = self.client.post(f'/clientes/4/transacoes', json={
            'valor': random.randint(1, 9999),
            'tipo': ['c', 'd'][random.randint(0, 1)],
            'descricao': ['pix', 'ted', 'doc', 'remessa'][random.randint(0, 3)]})
        assert req.status_code in (422, 200)

    @task
    def test_debit_operation_for_client_05(self):
        req = self.client.post(f'/clientes/5/transacoes', json={
            'valor': random.randint(1, 9999),
            'tipo': ['c', 'd'][random.randint(0, 1)],
            'descricao': ['pix', 'ted', 'doc', 'remessa'][random.randint(0, 3)]})
        assert req.status_code in (422, 200)
