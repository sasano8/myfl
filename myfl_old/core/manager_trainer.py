class DummyDatasetLoader:
    ...


class DummyModelLoader:
    ...


class DummyAggregator:
    ...


class DummyTrainer:
    LOADERS = {"dummy": DummyDatasetLoader}
    MODELS = {"dummy": DummyModelLoader}
    AGGREGATOR = DummyAggregator

    def __init__(self, comm, is_server: bool = False, conf={}):
        self.comm = comm
        self.is_server = is_server
        self.conf = conf
        self.__post_init__(**conf)

    def __post_init__(self, **kwargs):
        typ, kwargs = kwargs["loader"]
        typ, kwargs = kwargs["model"]

    async def run(self):
        if self.is_server:
            await self.run_server()
        else:
            await self.run_client()

    async def run_server(self):
        # await self.wait("start_train")
        # await self.wait("pull_model")
        # await self.wait("pull_data")
        # await self.wait("aggregate_model")
        # await self.wait("commit")
        await self.wait("end_train")

    async def run_client(self):
        # await self.comm.request("pull_model") == (None, "test hello!")
        # await self.comm.request("pull_data") == (None, "test hello!")
        # await self.comm.request("aggregate_model") == (
        #     None,
        #     "test hello!",
        # )
        # await self.comm.request("commit") == (None, "test hello!")
        await self.comm.request("end_train")


class Manager:
    TRAINERS = {"dummy": DummyTrainer, "default": DummyTrainer}

    def __init__(self, comm, is_server: bool = False, conf={}):
        self.comm = comm
        self.is_server = is_server
        self.conf = conf
        self.__post_init__(**conf)

    def __post_init__(self, **kwargs):
        ...

    async def run(self):
        if self.is_server:
            await self.run_server()
        else:
            await self.run_client()

    async def run_server(self):
        await self.comm.wait("hello")
        await self.comm.wait("pull_config")
        trainer_cls = await self.comm.wait("ready_train", self.get_trainer)
        trainer = trainer_cls(self.comm, is_server=True, conf={})
        await trainer.serve()
        await self.comm.wait("bye")

    async def run_client(self):
        await self.comm.request("hello")
        await self.comm.request("pull_config")
        await self.comm.request("ready_train")
        trainer_cls = self.get_trainer(None, "dummy")
        trainer = trainer_cls(self.comm, is_server=False, conf={})
        await trainer.train()
        await self.comm.request("bye")

    @classmethod
    async def get_trainer(cls, info, value):
        return cls.TRAINERS[value]
