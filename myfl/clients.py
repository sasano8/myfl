from .impl.local import FileSystemWorkspace
from .core.protocols import Client
from pathlib import Path
from contextlib import contextmanager


@contextmanager
def local(path: str):
    client = Client(name=Path(__file__).parent.name, ws=FileSystemWorkspace(path))
    assert client.name == "myfl"
    yield client


@contextmanager
def remote(path: str, remote_path: str):
    client = Client(name=Path(__file__).parent.name, ws=FileSystemWorkspace(path))
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

            client = Client(name="ssh", ws=FileSystemWorkspace(remote))
            assert client.name == "ssh"
            raise NotImplementedError()
            yield client


@contextmanager
def git_http(path: str, url: str):
    if url[:-4] != ".git":
        raise Exception()

    client = Client(name="git", ws=FileSystemWorkspace(url))
    assert client.name == "git_http"
    raise NotImplementedError()
    yield client


@contextmanager
def web(path: str, url: str):
    client = Client(name="myfl", ws=FileSystemWorkspace(url))
    assert client.name == "myfl"
    raise NotImplementedError()
    yield client
