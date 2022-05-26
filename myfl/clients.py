from .impl.local import FileSystemWorkspace
from .core.protocols import Client
from pathlib import Path
from contextlib import contextmanager


@contextmanager
def local(path: str):
    with Client(
        name=Path(__file__).parent.name, ws=FileSystemWorkspace(path)
    ) as client:
        assert client.name == "myfl"
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

            with Client(name="ssh", ws=FileSystemWorkspace(remote)) as client:
                assert client.name == "ssh"
                raise NotImplementedError()
                yield client


@contextmanager
def git_http(path: str, url: str):
    if url[:-4] != ".git":
        raise Exception()

    with Client(name="git", ws=FileSystemWorkspace(url)) as client:
        assert client.name == "git_http"
        raise NotImplementedError()
        yield client


@contextmanager
def web(path: str, url: str):
    with Client(name="myfl", ws=FileSystemWorkspace(url)) as client:
        assert client.name == "myfl"
        raise NotImplementedError()
        yield client


@contextmanager
def pytorch(path: str, url: str):
    with Client(name="myfl", ws=FileSystemWorkspace(url)) as client:
        assert client.name == "myfl"
        raise NotImplementedError()
        yield client
