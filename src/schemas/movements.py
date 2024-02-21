# -*- coding: utf-8 -*-

from enum import StrEnum
from pydantic import BaseModel, constr, field_validator, conint


class TransactionType(StrEnum):
    c = "c"
    d = "d"


class TransactionSchema(BaseModel):
    id: int
    valor: conint(le=2147483647, gt=0)
    tipo: TransactionType
    descricao: constr(min_length=1, max_length=10)
