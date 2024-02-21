# -*- coding: utf-8 -*-

from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(
    url='postgresql+asyncpg://foo:foo@localhost:5432/foo',
    poolclass=QueuePool,
    pool_size=50,
    max_overflow=0,
    isolation_level='READ COMMITTED')

db = async_sessionmaker(
    bind=engine,
    autoflush=False,
    future=True)
