# -*- coding: utf-8 -*-

from typing import List
from pydantic import BaseModel, constr


class ClientSchema(BaseModel):
    id: int
    limite: int


class ClientListSchema(BaseModel):
    each_item: List[ClientSchema]
