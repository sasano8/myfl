from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from .workspace import LocalRepository
else:
    LocalRepository = Any


class IStore:
    async def pull(self, **kwargs):
        raise NotImplementedError()

    async def push(self, **kwargs):
        raise NotImplementedError()


class DummyConfigStore(IStore):
    async def pull(self, **kwargs):
        return {}


class DummyDataStore(IStore):
    async def pull(self, **kwargs):
        return []


class DummyModelStore(IStore):
    async def pull(self, **kwargs):
        return "".encode("utf-8")

    async def push(self, **kwargs):
        return {"id": 1}


class LocalConfigStore(IStore):
    def __init__(self, rep: LocalRepository):
        self.rep = rep

    def pull(self, **kwargs):
        return self.rep.get_config(**kwargs)

    # def push(self, **kwargs):
    #     ...


class LocalDataStore(IStore):
    def __init__(self, rep: LocalRepository):
        self.rep = rep

    def pull(self, **kwargs):
        return self.rep.get_dataset(**kwargs)

    # def push(self, **kwargs):
    #     ...


class LocalModelStore(IStore):
    def __init__(self, rep: LocalRepository):
        self.rep = rep

    def pull(self, **kwargs):
        return self.rep.get_model(**kwargs)

    # def push(self, **kwargs):
    #     ...
