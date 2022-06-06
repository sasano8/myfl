import tempfile
import json
from pathlib import Path
from typing import Iterable, Union, Any
import os
from shutil import rmtree
from io import BufferedReader
from pydantic import BaseModel
from datetime import datetime


class FileInfo(BaseModel):
    id: str = None
    name: str
    path: Path
    is_file: bool
    created_at: datetime = None
    update_at: datetime
    accessed_at: datetime
    size: float

    @classmethod
    def create_from_path(cls, path: Path):
        # st_mode = 33188  # -node の保護モード
        # st_ino = 163679  # i-node 番号
        # st_dev = 2096  # i-nodeが存在するデバイス
        # st_nlink = 1  # i-nodeへのリンク数
        # st_uid = 1000  # 所有者のユーザID
        # st_gid = 1000  # 所有者のグループID
        # st_size = 870  # バイト単位
        # st_atime = 1654116369  # 最終アクセス日時
        # st_mtime = 1653497808  # 最終内容更新日時
        # st_ctime = 1653497808  # 最終メタデータ更新日時
        # birthtime           # 一部OSのみ作成日時

        stat = path.stat()

        return cls(
            name=path.name,
            path=path.absolute(),
            is_file=path.is_file(),
            created_at=getattr(stat, "st_birthtime", None),
            update_at=stat.st_mtime,
            accessed_at=stat.st_atime,
            size=stat.st_size,
        )


class WorkSpace:
    @classmethod
    def read_model(cls, fd: BufferedReader, info: FileInfo):
        return fd.read()

    @classmethod
    def write_model(cls, fd: BufferedReader, model):
        fd.write(model)

    def __init__(self, dir: Union[str, Path, tempfile.TemporaryDirectory]):
        if isinstance(dir, tempfile.TemporaryDirectory):
            self.temp = dir
            self.dir = Path(dir.name)

        if isinstance(dir, str):
            dir = Path(dir)

        if not isinstance(dir, Path):
            raise TypeError()

        self.dir = dir

    def init(self, conf: dict = None):
        if not (isinstance(conf, dict) or conf is None):
            raise TypeError()

        conf = conf or {}
        file_json = self.dir / "conf.json"
        file_py = self.dir / "conf.py"

        if file_json.exists():
            raise RuntimeError("Already initialized: `conf.json` already exists.")

        if file_py.exists():
            raise RuntimeError("Already initialized: `conf.py` already exists.")

        with open(self.dir / "conf.json") as f:
            json.dump(conf, f, ensure_ascii=False)

    def __str__(self):
        return str(self.dir)

    def __truediv__(self, other: str) -> Path:
        return self.dir / other  # type: ignore

    def __enter__(self):
        if hasattr(self, "temp"):
            self.temp.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        if hasattr(self, "temp"):
            self.temp.__exit__(*args, **kwargs)

    def get_safe_path(self, path: str) -> Path:
        if not isinstance(path, str):
            raise ValueError()

        if "/" in path:
            raise ValueError()

        if ".." in path:
            raise ValueError()

        return self / path

    def list(self, path: str, *args, **kwargs) -> Iterable[FileInfo]:
        p = self.get_safe_path(path)
        return (
            FileInfo.create_from_path(x) for x in p.iterdir() if x.name != ".gitignore"
        )

    def get_info(self, path: str, *args, **kwargs) -> Union[FileInfo, None]:
        p = self.get_safe_path(path)
        if not p.exists():
            return None

        if p.name != ".gitignore":
            return None
        return FileInfo.create_from_path(p)

    def get(self, path: str) -> Any:
        info = self.get_info(path)
        if not info:
            raise KeyError("Not Found.")

        with open(info.path, mode="rb") as f:
            return self.read_model(f, info)

    def put(self, path: str, model) -> FileInfo:
        p = self.get_safe_path(path)
        if p.exists():
            ...
        else:
            ...

        with open(p, mode="wb") as f:
            self.write_model(f, model)
            return FileInfo.create_from_path(p)

    def delete(self, path: str, *args, **kwargs) -> Union[FileInfo, None]:
        info = self.get_info(path)
        if not info:
            return None

        if info.is_file:
            os.remove(info.path)
        else:
            rmtree(info.path, ignore_errors=False)

        return info


class TempWorkSpace(WorkSpace):
    def __init__(self):
        # TODO: 一時ファイルの削除漏れを防ぐには？
        # linux ではスクリプトが終了すると一時ディレクトリは削除される
        # 強制終了などで、削除処理が漏れた場合は、linux では cronによって自動削除される
        # ただし、dockerなどではcronが動かないためゴミが溜まる
        super().__init__(tempfile.TemporaryDirectory())

    def init(self, conf: dict = None):
        raise NotImplementedError()


class HttpWorkSpace(WorkSpace):
    def __init__(self, url, *args, **kwargs):
        self.url = url

    def init(self, conf: dict = None):
        raise NotImplementedError()

    def __str__(self):
        return str(self.url)

    def __truediv__(self, other: str):
        return self.url + "/" + other

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        ...

    def list(self, path, *args, **kwargs):
        p = self / path

    def get(self, path, *args, **kwargs):
        p = self / path

    def get_info(self, path, *args, **kwargs):
        p = self / path

    def put(self, path, *args, **kwargs):
        p = self / path

    def delete(self, path, *args, **kwargs):
        p = self / path
