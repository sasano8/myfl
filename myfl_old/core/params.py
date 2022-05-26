from pydantic import BaseModel
from typing import Tuple, Union, Literal

# class Discriminator(NamedTuple):
#     name: str
#     args: dict = {}

Discriminator = Tuple[str, Union[dict, None]]


DEFAULT_CONFIG = {
    "version": "0.1",
    "domain": [
        # "local",
        # {}
        "remote",
        {"host": "xxx.com"},
        # "p2p",
        # {"central": "", "hosts": []},
    ],
    # "distributed": [
    #     # "standalone"
    #     "mpi",
    #     {"gpu": 0, "communicator": "mpi", "nodes": []},
    # ],
    "worker": [
        "distributed",  # standalone, distributed, server
        {
            "common": {"is_gpu": False},
            "mpi_hosts": [{"device_a": 1}],
        },
    ],
    "federation": [
        "fedavg",
        {
            "config_name": "config_1",
            "description": "",
            "output_model_name": "mymodel",
            "security": {
                "allow_anonymous_domain": True,
                "allow_anonymous_device": True,
            },
        },
    ],
    "trainer": [
        "local",
        {
            "loader": [
                "fileloader",
                {"type": "csv", "path": "aaa/bbb/ccc/aaaa.csv", "cache": True},
            ],
            "model": ["LogisticRegression", {"input_dim": 1, "output_dim": 1}],
        },
    ],
    "events": [
        "default",
        {
            "on_success": None,
            "on_error": None,
            "on_complete": None,
        },
    ],
    "logger": [],
    "args": {
        #         "comm_round": 1,
        #         "batch_size": 1,
        #         "epochs": 1,
        #         "client_optimizer": "",
        #         "lr": 1,
        #         "ci": 0,
        #         "partition_method": "hetero",
        #         "client_num_in_total": 1,
        #         "client_num_per_round": 1
    },
}


class FederateConfig(BaseModel):
    version: str
    worker: Discriminator = ("standalone", None)
    federation: Discriminator
    manager: Discriminator
    trainer: Discriminator
    loader: Discriminator
    model: Discriminator

    class Config:
        schema_extra = {"examples": [DEFAULT_CONFIG]}

    def to_server_config(self):
        conf = self.dict()
        conf["worker"] = ("server", {})
        return self.__class__(**conf)

    def to_standalone_config(self):
        conf = self.dict()
        worker = getattr(conf["worker"], ("",))

        if worker[0] == "distributed":
            conf = worker[1]
        else:
            conf = {}

        conf["worker"] = ("standalone", conf)
        return self.__class__(**conf)


WORKER = Literal["server", "standalone", "distributed"]
