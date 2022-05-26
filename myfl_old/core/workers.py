class Worker:
    ...


class ServerWorker:
    ...


class StandaloneWorker:
    def __init__(self, *, is_gpu: bool = False):
        ...


class DistributedWorker:
    def __init__(self, *, common, mpi_hosts):
        raise NotImplementedError()
