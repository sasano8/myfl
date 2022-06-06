# Introduction


# Getting Started

```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
source $HOME/.poetry/env
poetry config virtualenvs.in-project true
poetry install
```

# Awasome Data Science

- https://github.com/huggingface/datasets: データセットのハブ
- https://github.com/allegroai/clearml: 実験管理・モデルサービングなど
- https://dvc.org/: データバージョン管理・再現可能なパイプライン
- https://www.mlflow.org/docs/latest/models.html: 実験管理・モデルサービングなど


``` python
import os
from myfl import WorkSpace, TempWorkSpace

ws = WorkSpace(os.getcwd()).init({})
```

``` shell
myfl init
```


``` python
import os
from myfl import WorkSpace, TempWorkSpace

print(WorkSpace(os.getcwd()).get_client("default").dataset.list())

ws = WorkSpace(os.getcwd())
```

``` shell
myfl dataset list
```