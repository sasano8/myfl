import os
import json
from myfl.core.protocols import (
    IConfigStore,
    IBaseModelStore,
    IDataStore,
    IFLConfigStore,
    IModelStore,
    IWorkspace,
)
from myfl.core.exceptions import ConfigKeyError
from pathlib import Path


def get_workspace(path) -> "FileSystemWorkspace":
    return FileSystemWorkspace(path)


class FileSystemWorkspace:
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
                json.dump({"default": {}}, f, indent=2, ensure_ascii=False)

        if not file_override.exists():
            with open(file_override, "w") as f:
                json.dump({"default": {}}, f, indent=2, ensure_ascii=False)

        if not file_ignore.exists():
            with open(file_ignore, "w") as f:
                f.write("""cache""")


class ConfigStore(IConfigStore):
    def __init__(self, ws: FileSystemWorkspace):
        self.ws = ws
        self.path: Path = self.ws.file_conf

    def _write(self, conf):
        with open(self.path, "w") as f:
            json.dump(conf, f, indent=2, ensure_ascii=False)

    def init(self):
        if not self.path.exists():
            conf = {"default": {}}
            self._write(conf)

    def list(self):
        with open(self.path) as f:
            conf = json.load(f)

        # with open(self.file_override) as f:
        #     override = json.load(f)
        #     conf = deep_merge(conf, override)

        return conf

    def get(self, config_name: str = "default"):
        conf = self.list()

        try:
            return conf[config_name]
        except KeyError:
            raise ConfigKeyError(config_name)

    def save(self, data, name):
        conf = self.list()
        conf[name] = data
        self._write(conf)


class DatasetStore(IDataStore):
    def __init__(self, ws: FileSystemWorkspace):
        self.ws = ws
        self.path: Path = self.ws.file_conf

    def init(self):
        if not self.path.exists():
            os.mkdir(self.path)

    def list(self):
        return [x.name for x in self.path.iterdir()]

    def get(self, name: str):
        with open(self.path / name) as f:
            return f.read()

    def get_info(self, name: str):
        ...

    def save(self, data, name: str):
        with open(self.path / name, "w") as f:
            f.write(data)


class ModelStore(IDataStore):
    def __init__(self, ws: FileSystemWorkspace):
        self.ws = ws
        self.path: Path = self.ws.file_conf

    def init(self):
        if not self.path.exists():
            os.mkdir(self.path)

    def list(self):
        return [x.name for x in self.path.iterdir()]

    def get(self, name: str):
        with open(self.path / name) as f:
            return f.read()

    def get_info(self, name: str):
        ...

    def save(self, model, name: str):
        import torch.nn as nn
        import torch
        import shutil

        if isinstance(model, nn.Module):
            path = self.path / name
            shutil.rmtree(path)
            os.mkdir(path)
            with open(path / "info", "w") as f:
                json.dump(
                    {"name": name, "type": "mymodel", "fw": "pytorch"},
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
            torch.save(model.state_dict(), path / "model")
        else:
            raise TypeError()

    def load(self, name: str):
        path = self.path / name
        with open(path / "info") as f:
            meta = json.load(f)

        if meta["fw"] == "pytorch":
            import torch

            model = define_cnn()
            model.load_state_dict(torch.load(path / "model"))
        else:
            raise TypeError()

        return meta, model
