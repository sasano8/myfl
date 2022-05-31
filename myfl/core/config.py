import os
from pydantic import BaseModel
from typing import List, Dict, Any, Tuple


class Config(BaseModel):
    inherit: List[str] = []
    # env: Dict[str, Dict[str, Any]]
    clients: Dict[str, Tuple[str, Dict[str, Any]]]


conf = Config(
    inherit=["../conf.json"],
    clients={
        "default": ["local", {}],
        "web": [
            "web",
            {
                "header": {
                    "Content-type": "application/json",
                    "user": os.getenv("API_KEY"),
                    "pass": os.getenv("API_SECRET"),
                }
            },
        ],
    },
)


# conf.clients()["local"](os.getcwd(), header={})

# from .utils import create_temp_dir

# create_temp_dir(conf.dict())

# with Workspace(conf.dict()) as ws:
#     ...
