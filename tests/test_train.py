import pytest

# from myfl.core.workspace import WorkSpace
# from myfl.server_factories import build_server
from functools import wraps
import asyncio
from myfl import api


def to_sync(async_func):
    @wraps(async_func)
    def wrapper(*args, **kwargs):
        coro = async_func(*args, **kwargs)
        return asyncio.run(coro)

    return wrapper


def create_server(config=None):
    with WorkSpace.as_tmp_dir() as dir:
        dir.init()
        # dir.set_config(config)
        config_store, data_store, model_store = dir.get_stores()

        server = build_server(
            config_store=config_store, data_store=data_store, model_store=model_store
        )
        yield server


@pytest.fixture(scope="function")
def local_server():
    yield from create_server(config={})


@pytest.fixture(scope="function")
def remote_server():
    yield from create_server(config={})


@to_sync
async def test_standalone_cross_device():
    import time
    from myfl.core.communicators import WebsocketClient
    from myfl.core.manager_trainer import Manager, DummyTrainer

    with api.create_ws_as_temporary() as ws:
        with api.create_server_executor(ws):
            time.sleep(1)  # wait start server.
            async with WebsocketClient.create("ws://127.0.0.1:5000/federate") as comm:
                manager = Manager(comm, is_server=False)
                await manager.run()

                assert await comm.request("hello") == (None, "test hello!")
                assert await comm.request("pull_config") == (None, "test hello!")
                assert await comm.request("ready_trainer") == (None, "test hello!")
                assert await comm.request("pull_model") == (None, "test hello!")
                assert await comm.request("pull_data") == (None, "test hello!")
                assert await comm.request("aggregate_model") == (None, "test hello!")
                assert await comm.request("commit") == (None, "test hello!")
                assert await comm.request("bye") == (None, "test hello!")


def test_standalone_cross_silo():
    ...
