import os
import json

from typing import Union
from .exceptions import ConfigKeyError
from .params import DEFAULT_CONFIG


# TODO: 第一階層しか対応していない
def deep_merge(dic1, dic2):
    result = {}
    for k, v in dic1.items():
        if k in dic2:
            v = dict(v, **dic2[k])
        else:
            ...

        result[k] = v

    return result


class WorkSpace:
    def __init__(self, path):
        if isinstance(path, str):
            from pathlib import Path

            path = Path(path)

        conf_dir = path / ".fed"

        self.cache = conf_dir / "cache"
        self.datasets = conf_dir / "datasets"
        self.models = conf_dir / "models"
        self.file_conf = conf_dir / "conf.json"
        self.file_override = conf_dir / "conf.override.json"
        self.file_ignore = conf_dir / ".gitignore"

        self.dir_root = conf_dir
        self.path = path

    @classmethod
    def as_tmp_dir(cls):
        import tempfile
        from contextlib import contextmanager

        @contextmanager
        def tmp_dir():
            with tempfile.TemporaryDirectory() as path:
                yield cls(path)

        return tmp_dir()

    @classmethod
    def from_cwd(cls):
        conf = cls(os.getcwd())
        return conf

    def init(self):
        dir_root = self.dir_root
        dir_cache = self.cache
        dir_datasets = self.datasets
        dir_models = self.models
        file_conf = self.file_conf
        file_override = self.file_override
        file_ignore = self.file_ignore

        if not dir_root.exists():
            os.mkdir(dir_root)

        if not dir_cache.exists():
            os.mkdir(dir_cache)

        if not dir_datasets.exists():
            os.mkdir(dir_datasets)

        if not dir_models.exists():
            os.mkdir(dir_models)

        if not file_conf.exists():
            with open(file_conf, "w") as f:
                json.dump({"default": DEFAULT_CONFIG}, f, indent=2, ensure_ascii=False)

        if not file_override.exists():
            with open(file_override, "w") as f:
                json.dump({"default": {}}, f, indent=2, ensure_ascii=False)

        if not file_ignore.exists():
            with open(file_ignore, "w") as f:
                f.write("""cache""")

    def load(self):
        with open(self.file_conf) as f:
            conf = json.load(f)

        with open(self.file_override) as f:
            override = json.load(f)
            conf = deep_merge(conf, override)

        return conf

    def get(self, config_name: str = None):
        conf = self.load()

        if config_name is None:
            config_name = "default"

        try:
            return conf[config_name]
        except KeyError:
            raise ConfigKeyError(config_name)

    def get_stores(self):
        from .store import LocalConfigStore, LocalDataStore, LocalModelStore

        return LocalConfigStore(self), LocalDataStore(self), LocalModelStore(self)


class LocalRepository:
    def __init__(self, dir: WorkSpace, config_name: Union[str, None] = "default"):
        if config_name is None:
            config_name = "default"

        self.dir = dir
        self.config_name = config_name

    @classmethod
    def from_cwd(cls, config_name: Union[str, None] = "default"):
        root = WorkSpace(os.getcwd())
        return cls(root, config_name)

    def get_config(self, config_name=None):
        if config_name is None:
            config_name = self.config_name

        return self.dir.get(config_name)

    def get_datasets(self):
        return [x.name for x in self.dir.datasets.iterdir()]

    def get_dataset(self, name: str):
        with open(self.dir.datasets / name) as f:
            return f.read()

    def get_models(self):
        return [x.name for x in self.dir.models.iterdir() if x.is_file()]

    def get_model(self, name):
        arr = set(x.name for x in self.dir.models.iterdir() if x.is_file())
        if name not in arr:
            raise KeyError(name)

        with open(self.dir.models / name) as f:
            return f.read()
