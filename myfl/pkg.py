from pathlib import Path

from .clients import local, web, remote, ssh, git_http, sql, pytorch, kaggle
from .api import create_api
from .cli import create_cli
from .core import Client
from .core.config import Config
from .core.exceptions import MyflInternalException


pkg_name = Path(__file__).parent.name
config = Config
clients = [local, web, remote, ssh, git_http, sql, pytorch, kaggle]


def build_cli(client: Client):
    return create_cli(client)


def build_api(client: Client):
    return create_api(client)


def import_pkg(pkg_name):
    import importlib

    try:
        module = importlib.import_module(pkg_name)
    except Exception as e:
        raise MyflInternalException(f"Cannot import module: {pkg_name}") from e

    result = check_module(module)
    if not all(result.items()):
        raise MyflInternalException("Invalid module.", result)

    result = check_config(module.config)
    if not all(result.items()):
        raise MyflInternalException("Invalid config.", result)

    kwargs = {k: getattr(module.config, k) for k in result.keys()}
    update_pkg_config(**kwargs)


def update_pkg_config(
    custom_pkg_name,
    custom_config=None,
    custom_clients=None,
    custom_create_cli=None,
    custom_create_api=None,
):
    # global pkg_name
    # pkg_name = custom_pkg_name

    # if custom_config is not None:
    #     global config
    #     config = custom_config

    # if custom_clients is not None:
    #     global clients
    #     clients = custom_clients

    # if custom_create_cli is not None:
    #     global create_cli
    #     create_cli = custom_create_cli

    # if custom_create_api is not None:
    #     global create_api
    #     create_api = custom_create_api

    dic = globals()

    dic["pkg_name"] = custom_pkg_name

    if custom_config is not None:
        dic["config"] = custom_config

    if custom_clients is not None:
        dic["clients"] = custom_clients

    if custom_create_cli is not None:
        dic["create_cli"] = custom_create_cli

    if custom_create_api is not None:
        dic["create_api"] = custom_create_api


def check_module(module):
    return {"config": hasattr(module, "config")}


def check_config(config):
    return {
        "pkg_name": hasattr(config, "pkg_name"),
        "config": hasattr(config, "config"),
        "create_cli": hasattr(config, "create_cli"),
        "create_api": hasattr(config, "create_api"),
        "clients": hasattr(config, "clients"),
    }


update_pkg_config(
    custom_pkg_name=Path(__file__).parent.name,
    custom_config=Config,
    custom_clients={
        "local": local,
        "web": web,
        "remote": remote,
        "ssh": ssh,
        "git_http": git_http,
        "sql": sql,
        "pytorch": pytorch,
        "kaggle": kaggle,
    },
    custom_create_cli=create_cli,
    custom_create_api=create_api,
)