from pathlib import Path
from contextlib import contextmanager
from typing import Union, TYPE_CHECKING
import tempfile

from . import server_config as server_config

if TYPE_CHECKING:
    from .core import WorkSpace
else:
    if server_config.WS_CLS is None:
        from .core import WorkSpace

        server_config.WS_CLS = WorkSpace


class Config_0_0_1:
    VERSION: str = "0.0.1"

    def __init__(self, ws: WorkSpace, name: str = "default"):
        self.ws = ws
        self.name = name
        self.conf = {}
        self.reload()

    def reload(self):
        self.conf = {}


Config = Config_0_0_1


def create_ws(path: Union[str, Path, None] = None):
    if path is None:
        import os

        path = os.getcwd()

    if not isinstance(path, (str, Path)):
        raise TypeError()

    return server_config.WS_CLS(path)


@contextmanager
def create_ws_as_temporary():
    with tempfile.TemporaryDirectory() as path:
        yield create_ws(path)


def get_conf(ws: WorkSpace, name: str = "default"):
    return Config(ws, name)


def create_server(conf: Config):
    config_store, data_store, model_store = conf.ws.get_stores()
    server = build_server(
        config_store=config_store,
        data_store=data_store,
        model_store=model_store,
    )

    return server


def create_client(conf: Config):
    ...


def run_client(*, lib: str = "my_fl", ws_path: str, conf_name: str = "default"):
    import asyncio

    ws = create_ws(ws_path)
    conf = get_conf(ws, conf_name)
    client = create_client(conf)
    asyncio.run(client.train())


def run_server(
    *, pkg: str = "my_fl", path: str, conf_name: str = "default", port: int = 5000
):
    import importlib
    import uvicorn
    from .server_factories import build_server

    importlib.import_module(pkg, pkg)

    ws = create_ws(path)
    conf = get_conf(ws, conf_name)
    config_store, data_store, model_store = conf.ws.get_stores()
    asgi_app = build_server(
        config_store=config_store,
        data_store=data_store,
        model_store=model_store,
    )

    uvicorn.run(asgi_app, port=port, log_level="info")


def create_server_executor(
    ws: Union[str, Path, "WorkSpace"], *, conf_name: str = "default", port: int = 5000
):
    if isinstance(ws, WorkSpace):
        ws = ws.path

    if isinstance(ws, Path):
        ws = str(ws)

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

    p = Process(
        target=run_server,
        kwargs={
            "pkg": server_config.PKG_NAME,
            "path": ws,
            "port": port,
            "conf_name": conf_name,
        },
    )
    return Executor(p)
