# -*- coding: utf-8 -*-

from pydantic import BaseModel, constr


class TransactionSchema(BaseModel):
    id: int
    valor: int
    tipo: constr(regex='^[cd]$')
    descricao: constr(max_length=10)
