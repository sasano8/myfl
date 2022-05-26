from typing import Literal, TYPE_CHECKING, Type, Any

if TYPE_CHECKING:
    from .core import WorkSpace
else:
    WorkSpace = Any


PKG_NAME = "my_fl"
DEFAULT_DIR = ".fed"
WS_CLS: Type[WorkSpace] = None  # type: ignore
MANAGER = None

# DEFAULT SERVER
ENV_DEFAULT_HOST = ""

# API PATH
ROOT_PREFIX = ""
ROUTER_PREFIX = ""
PATH = "/federate"
DEFAULT_PORT = 5000


def customize_pkg(
    PKG_NAME: str = None,
    DEFAULT_DIR: str = None,
    WS_CLS: Type[WorkSpace] = None,
    ENV_DEFAULT_HOST: str = None,
    ROOT_PREFIX: str = None,
    ROUTER_PREFIX: str = None,
    PATH: str = None,
    DEFAULT_PORT: int = None,
):
    from myfl import server_config

    if PKG_NAME is not None:
        server_config.PKG_NAME = PKG_NAME

    if DEFAULT_DIR is not None:
        server_config.DEFAULT_DIR = DEFAULT_DIR

    if WS_CLS is not None:
        server_config.WS_CLS = WS_CLS

    if ENV_DEFAULT_HOST is not None:
        server_config.ENV_DEFAULT_HOST = ENV_DEFAULT_HOST

    if ROOT_PREFIX is not None:
        server_config.ROOT_PREFIX = ROOT_PREFIX

    if ROUTER_PREFIX is not None:
        server_config.ROUTER_PREFIX = ROUTER_PREFIX

    if PATH is not None:
        server_config.PATH = PATH

    if DEFAULT_PORT is not None:
        server_config.DEFAULT_PORT = DEFAULT_PORT


def init_pkg():
    from myfl import server_config

    if server_config.WS_CLS is None:
        from .core import WorkSpace

        server_config.WS_CLS = WorkSpace

    if server_config.MANAGER is None:
        from .core.manager_trainer import Manager

        server_config.MANAGER = Manager


def get_entry_point(host="localhost", port=None):
    if port is None:
        port = DEFAULT_PORT

    return f"{host}:{port}{ROOT_PREFIX}{ROUTER_PREFIX}{PATH}"


def get_websocket_client(
    module: Literal["requests", "httpx"] = "requests", host="localhost", port=None
):
    entry_point = get_entry_point(host, port)
    from functools import partial

    if module == "requests":
        import requests

        return partial(requests.get, entry_point)
    elif module == "httpx":

        async def get(**kwargs):
            import httpx

            async with httpx.AsyncClient() as client:
                return await client.get(entry_point, **kwargs)

        return get

    else:
        raise RuntimeError(f"Unkown module: {module}")


def run_server(module: str, path=None, port=5000, config={}):
    from myfl.core.workspace import WorkSpace
    from myfl.server_factories import build_server

    if path is None:
        import os

        path = os.getcwd()

    import uvicorn

    dir = WorkSpace(path)
    dir.init()
    config_store, data_store, model_store = dir.get_stores()
    server = build_server(
        config_store=config_store,
        data_store=data_store,
        model_store=model_store,
    )

    uvicorn.run(server, port=port, log_level="info")


def execute_server(path=None, port=5000, config={}):

    from multiprocessing import Process

    class Executor:
        def __init__(self, p: Process):
            self.p = p

        def __enter__(self):
            self.start()
            return self

        def __exit__(self, *args, **kwargs):
            self.close()

        async def __aenter__(self):
            return self.__enter__()

        async def __aexit__(self, *args, **kwargs):
            return self.__exit__(*args, **kwargs)

        def start(self):
            self.p.start()

        def close(self):
            self.p.kill()

    # concurrent.futures.ProcessPoolExecutorではキャンセルができない
    p = Process(
        target=run_server,
        kwargs={"module": PKG_NAME, "path": path, "port": port, "config": config},
    )
    return Executor(p)
