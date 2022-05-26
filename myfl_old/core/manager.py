from .communicators import CommunicatorBase
from .store import IStore


class IManager:
    def __init__(
        self,
        comm: CommunicatorBase,
    ):
        self.comm = comm

    async def __aenter__(self):
        await self.comm.accept()
        self._state = {}
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.comm.close()

    async def run(self):
        raise NotImplementedError()

    def is_server(self):
        raise NotImplementedError()

    async def wait_disconnected(self):
        raise NotImplementedError()

    @classmethod
    def create(cls, comm):
        ...


class ClientDrivenServerManager(IManager):
    def __init__(
        self,
        comm: CommunicatorBase,
        config_store: IStore,
        data_store: IStore,
        model_store: IStore,
    ):
        super().__init__(comm)
        self.config_store = config_store
        self.data_store = data_store
        self.model_store = model_store

        comm.add_events(
            [self.config_pull, self.model_pull, self.data_load, self.model_push]
        )

    async def is_server(self):
        return True

    async def run(self):

        await self.comm.wait_disconnected()

    async def wait_disconnected(self):
        return await self.comm.wait_disconnected()

    async def config_pull(self, **kwargs):
        result = await self.config_store.pull(**kwargs)
        return await self.comm.send("config_pull", {"info": True, "result": result})

    async def model_pull(self, **kwargs):
        result = await self.store.model_pull(**kwargs)
        return await self.comm.send("model_pull", {"info": True, "result": result})

    async def data_load(self, **kwargs):
        result = await self.store.data_load(**kwargs)
        return await self.comm.send("data_load", {"info": True, "result": result})

    async def model_push(self, **kwargs):
        result = await self.store.model_push(**kwargs)
        return await self.comm.send("model_push", {"info": True, "result": result})

    async def train(self):
        class Trainer:
            def __init__(self, comm: CommunicatorBase):
                self.comm = comm

            async def train(self):
                await self.comm.wait("hello")
                await self.comm.send("hello", "test hello!")
                await self.comm.wait("pull_config")
                await self.comm.wait("pull_model")
                await self.comm.wait("pull_data")
                await self.comm.wait("aggregate_model")
                await self.comm.wait("feedback_model")
                await self.comm.wait("commit")
                # self.comm.upstream.send()
                await self.comm.wait("bye")

        return await Trainer(self.comm).train()


class ClientDrivenClientManager(IManager):
    def __init__(self, comm: CommunicatorBase):
        super().__init__(comm)

    async def run(self):
        await self.comm.wait_disconnected()

    async def wait_disconnected(self):
        return await self.comm.wait_disconnected()

    async def is_server(self):
        return False

    async def config_pull(self, **kwargs):
        return await self.comm.request("config_pull", kwargs)

    async def model_pull(self, **kwargs):
        return await self.comm.request("model_pull", kwargs)

    async def data_load(self, **kwargs):
        return await self.comm.request("data_load", kwargs)

    async def model_push(self, **kwargs):
        return await self.comm.request("model_push", kwargs)

    async def train(self):
        conf = await self.config_pull()
        model = await self.model_pull()
        data = await self.data_load()

        def train(conf, data, model):
            ...

        train(conf, data, model)

        await self.model_push()
        await self.model_pull()


class P2PSelfManager(IManager):
    def __init__(self, comm: CommunicatorBase):
        super().__init__(comm)

    async def is_server(self):
        return True

    async def wait_disconnected(self):
        return await self.comm.wait_disconnected()


class P2POtherManager(IManager):
    def __init__(self, comm: CommunicatorBase):
        super().__init__(comm)

    async def is_server(self):
        return False

    async def wait_disconnected(self):
        return await self.comm.wait_disconnected()
