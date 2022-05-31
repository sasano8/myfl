# from myfl import WorkSpace
from pydantic import BaseModel
from datetime import datetime
from typing import Protocol


class IItem:
    name: str
    created_at: datetime = datetime.utcnow()


class Item(BaseModel):
    name: str
    created_at: datetime = datetime.utcnow()


class IWorkspace(Protocol):
    def login(self, user, pw):
        raise NotImplementedError()


class IConfigStore(Protocol):
    def list(self):
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


class NotImplementedConfigStore(IConfigStore):
    ...


class NotImplementedDataStore(IDataStore):
    ...


class NotImplementedBaseModelStore(IBaseModelStore):
    ...


class NotImplementedModelStore(IModelStore):
    ...


class NotImplementedFLConfigStore(IFLConfigStore):
    ...


class DummyConfigStore:
    def list(self):
        return [Item(name=x) for x in ["a", "b", "c"]]


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


class Client(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    name: str
    ws: IWorkspace = NotImplementedWorkspace()
    config_store: IConfigStore = NotImplementedConfigStore()
    data_store: IDataStore = NotImplementedDataStore()
    base_model_store: IBaseModelStore = NotImplementedBaseModelStore()
    model_store: IModelStore = NotImplementedModelStore()
    fl_config_store: IFLConfigStore = NotImplementedFLConfigStore()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        return None

    @classmethod
    def create(cls, kwargs: dict):
        return cls(**{k: v for k, v in kwargs.items() if v is not None})
