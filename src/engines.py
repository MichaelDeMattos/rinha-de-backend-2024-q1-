# -*- coding: utf-8 -*-


from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    url='postgresql+asyncpg://foo:foo@localhost:5432/foo',
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30)
