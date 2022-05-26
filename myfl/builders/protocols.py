# from myfl import WorkSpace
from pydantic import BaseModel
from datetime import datetime
from typing import Protocol

from .cli import create_cli
from .api import create_api


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


class App(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    ws: IWorkspace = NotImplementedWorkspace()
    data_store: IDataStore = NotImplementedDataStore()
    base_model_store: IBaseModelStore = NotImplementedBaseModelStore()
    model_store: IModelStore = NotImplementedModelStore()
    fl_config_store: IFLConfigStore = NotImplementedFLConfigStore()

    @classmethod
    def create(cls, kwargs: dict):
        return cls(**{k: v for k, v in kwargs.items() if v is not None})


def build_cli(
    ws: IWorkspace = None,
    data_store: IDataStore = None,
    base_model_store: IBaseModelStore = None,
    model_store: IModelStore = None,
    fl_config_store: IFLConfigStore = None,
):
    app = App.create(locals())
    return create_cli(app)


def build_api(
    ws: IWorkspace = None,
    data_store: IDataStore = None,
    base_model_store: IBaseModelStore = None,
    model_store: IModelStore = None,
    fl_config_store: IFLConfigStore = None,
):
    app = App.create(locals())
    return create_api(app)
