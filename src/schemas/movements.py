# -*- coding: utf-8 -*-

from pydantic import BaseModel, constr


class TransactionSchema(BaseModel):
    id: int
    valor: int
    tipo: str # constr(regex='^[cd]$')
    descricao: constr(min_length=1, max_length=10)
