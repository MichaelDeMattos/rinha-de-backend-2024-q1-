# -*- coding: utf-8 -*-


from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    url='postgresql+asyncpg://foo:foo@localhost:5432/foo',
    poolclass=QueuePool,
    pool_size=120,
    max_overflow=30,
    pool_timeout=120,
    isolation_level='AUTOCOMMIT')
