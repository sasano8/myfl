from .local import FileSystemWorkspace
from myfl.core.protocols import Client
from pathlib import Path
from contextlib import contextmanager

__all__ = ["local", "web", "remote", "ssh", "git_http", "sql", "pytorch"]


@contextmanager
def local(path: str):
    with Client(
        name=Path(__file__).parent.name, ws=FileSystemWorkspace(path)
    ) as client:
        assert client.name == "myfl"
        yield client


@contextmanager
def web(path: str, url: str):
    with Client(name="myfl", ws=FileSystemWorkspace(path)) as client:
        assert client.name == "myfl"
        raise NotImplementedError()
        yield client


@contextmanager
def remote(path: str, remote_path: str):
    with Client(
        name=Path(__file__).parent.name, ws=FileSystemWorkspace(path)
    ) as client:
        assert client.name == "myfl"
        yield client


@contextmanager
def ssh(
    path: str,
    username: str,
    hostname: str,
    port: int = 22,
    password: str = None,
    pkey: str = None,
    readonly: bool = True,
):
    kwargs = {k: v for k, v in locals() if v}
    readonly = kwargs.pop("readonly")
    # git@github.com:yourname/reponame.git
    # https://github.com/paramiko/paramiko
    import paramiko
    import scp

    with paramiko.SSHClient() as ssh:
        # skip Are you sure you want to continue connecting (yes/no)?
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(**kwargs)
        with scp.SCPClient(ssh.get_transport()) as scp:
            scp.get("xxx.tar.gz", "xxx.tar.gz")

            with Client(name="ssh", ws=FileSystemWorkspace(path)) as client:
                assert client.name == "ssh"
                raise NotImplementedError()
                yield client


@contextmanager
def git_http(path: str, url: str):
    if url[:-4] != ".git":
        raise Exception()

    with Client(name="git", ws=FileSystemWorkspace(path)) as client:
        assert client.name == "git_http"
        raise NotImplementedError()
        yield client


@contextmanager
def sql(path: str, connection_string: str, lib: str = ""):
    with Client(name="myfl", ws=FileSystemWorkspace(path)) as client:
        assert client.name == "myfl"
        raise NotImplementedError()
        yield client


@contextmanager
def pytorch(path: str, url: str):
    with Client(name="myfl", ws=FileSystemWorkspace(path)) as client:
        assert client.name == "myfl"
        raise NotImplementedError()
        yield client


false = False
true = True
null = None

{
    "pipelines": [
        {
            "name": "sample",
            "description": "",
            "dataset": [
                "pytorch",
                {
                    "save_as": "FashionMNIST",
                    "dataset": "FashionMNIST",
                    "download": false,
                    "transform": "ToTensor",
                },
            ],
            "dataloader": [
                "pytorch",
                {"batch_size": 1024, "shuffle": true, "num_workers": 1},
            ],
            "train": [
                "pytorch",
                {
                    "epoch": 2,
                    "model": "models.Net",
                    "optim": "SGD",
                    "lr": 0.001,
                    "momentum": 0.9,
                },
            ],
            "report": [
                "mlflow",
                {
                    "file": "path",
                    "sql": "<dialect>+<driver>://<username>:<password>@<host>:<port>/<database>",
                    "tracking_uri": "https://xxxx.xx/",
                    "every_n_iter": 1,
                },
            ],
        }
    ]
}
