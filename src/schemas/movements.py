# -*- coding: utf-8 -*-

from enum import StrEnum

from pydantic import BaseModel, constr, field_validator


class TransactionType(StrEnum):
    c = "c"
    d = "d"


class TransactionSchema(BaseModel):
    id: int
    valor: int
    tipo: TransactionType
    descricao: constr(min_length=1, max_length=10)

    @field_validator("valor")
    @classmethod
    def greater_then_zero(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("valor must be greater then zero")
        return v
