import tempfile
import json
from pathlib import Path


class WorkSpaceBase:
    def __str__(self):
        return str(self.dir)

    def __truediv__(self, other: str):
        return self.dir / other  # type: ignore

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        ...


class WorkSpace(WorkSpaceBase):
    def __init__(self, dir):
        if isinstance(dir, str):

            dir = Path(dir)

        if not isinstance(dir, Path):
            raise TypeError()

        self.dir = dir


class TempWorkSpace(WorkSpaceBase):
    def __init__(self, conf: dict = None):
        if not (isinstance(conf, dict) or conf is None):
            raise TypeError()

        conf = conf or {}

        # TODO: 一時ファイルの削除漏れを防ぐには？
        # linux ではスクリプトが終了すると一時ディレクトリは削除される
        # 強制終了などで、削除処理が漏れた場合は、linux では cronによって自動削除される
        # ただし、dockerなどではcronが動かないためゴミが溜まる
        dir = tempfile.TemporaryDirectory()
        with open(dir.name + "/conf.json") as f:
            json.dump(conf, f, ensure_ascii=False)

        self.temp = dir

        self.dir = Path(self.temp.name)

    def __enter__(self):
        self.temp.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        self.temp.__exit__(*args, **kwargs)
