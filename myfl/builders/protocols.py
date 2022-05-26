# from myfl import WorkSpace
from pydantic import BaseModel
from datetime import datetime
from typing import Protocol

from .cli import create_cli
from .api import create_api
from myfl.core.protocols import Client


class IItem:
    name: str
    created_at: datetime = datetime.utcnow()


class Item(BaseModel):
    name: str
    created_at: datetime = datetime.utcnow()


class IWorkspace(Protocol):
    def login(self, user, pw):
        raise NotImplementedError()


class IDataStore(Protocol):
    def list(self):
        raise NotImplementedError()


class IBaseModelStore(Protocol):
    def list(self):
        raise NotImplementedError()


class IModelStore(Protocol):
    def list(self):
        raise NotImplementedError()


class IFLConfigStore(Protocol):
    def list(self):
        raise NotImplementedError()


class NotImplementedWorkspace(IWorkspace):
    ...


class NotImplementedDataStore(IDataStore):
    ...


class NotImplementedBaseModelStore(IBaseModelStore):
    ...


class NotImplementedModelStore(IModelStore):
    ...


class NotImplementedFLConfigStore(IFLConfigStore):
    ...


class DummyDataStore:
    def list(self):
        return [Item(name=x) for x in ["a", "b", "c"]]


class DummyBaseModelStore:
    def list(self):
        return [Item(name=x) for x in ["a", "b", "c"]]


class DummyModelStore:
    def list(self):
        return [Item(name=x) for x in ["a", "b", "c"]]


class DummyFLConfigStore:
    def list(self):
        return [Item(name=x) for x in ["a", "b", "c"]]


def build_cli(client: Client):
    return create_cli(client)


def build_api(client: Client):
    return create_api(client)
