import asyncio
import pytest
import pytest_asyncio
from datetime import datetime
from pymongo import MongoClient
from httpx import AsyncClient
from server import api
from src.entities.user import User

def pytest_sessionstart(session):
    setup()

def pytest_sessionfinish(session, exitstatus):
    teardown()

def setup():
    client = MongoClient('mongodb://localhost:27017/')
    client.drop_database('LemonTCG')
    db = client['LemonTCG']
    users_collection = db['users']

    test1 = User.new("test-1", "1")
    test2 = User.new("test-2", "2")
    test3 = User.new("test-3", "3")
    users_collection.insert_one(test1.model_dump(exclude={"id"}))
    users_collection.insert_one(test2.model_dump(exclude={"id"}))
    users_collection.insert_one(test3.model_dump(exclude={"id"}))
    client.close()

def teardown():
    client = MongoClient('mongodb://localhost:27017/')
    client.drop_database('LemonTCG')
    client.close()

@pytest.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(app=api, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="function")
def header1():
    return {"X-API-Key": "1"}

@pytest.fixture(scope="function")
def header2():
    return {"X-API-Key": "2"}

@pytest.fixture(scope="function")
def header3():
    return {"X-API-Key": "3"}