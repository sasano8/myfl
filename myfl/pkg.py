from pathlib import Path

from .clients import local, web, remote, ssh, git_http, sql, pytorch, kaggle
from .api import create_api
from .cli import create_cli
from .core import Client
from .core.config import WsConfig
from .core.exceptions import MyflInternalException
from typing import Callable, Dict, Type
from pydantic import BaseModel


class PkgConfig(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    pkg_name: str
    config_cls: Type[WsConfig]
    clients: Dict[str, Callable]
    create_cli: Callable
    create_api: Callable

    def build_cli(self, client: Client):
        return self.create_cli(client)

    def build_api(self, client: Client):
        return self.create_api(client)

    def get_client(self, ws) -> Client:
        return self.clients["local"](ws)


def import_pkg(pkg_name):
    import importlib

    try:
        module = importlib.import_module(pkg_name)
    except Exception as e:
        raise MyflInternalException(f"Cannot import module: {pkg_name}") from e


def setup_pkg_config(
    pkg_name,
    config_cls=None,
    clients=None,
    create_cli=None,
    create_api=None,
):
    global PKG_CONFIG

    params = {k: v for k, v in locals() if v is not None}
    params = {**PKG_CONFIG.dict(), **params}

    pkg = PkgConfig(**params)

    PKG_CONFIG = pkg
    return pkg


PKG_CONFIG = PkgConfig(
    pkg_name=Path(__file__).parent.name,
    config_cls=WsConfig,
    clients={
        "local": local,
        "web": web,
        "remote": remote,
        "ssh": ssh,
        "git_http": git_http,
        "sql": sql,
        "pytorch": pytorch,
        "kaggle": kaggle,
    },
    create_cli=create_cli,
    create_api=create_api,
)


def run_cli():
    from .core.workspaces import WorkSpace
    import os

    ws = WorkSpace(os.getcwd())
    client = PKG_CONFIG.get_client(ws)
    cli = PKG_CONFIG.build_cli(client)
    cli()
