import websocket
from websocket import WebSocket as websocket_WebSocket, ABNF
import json
import asyncio
from functools import partial

from .abc import CommunicatorBase


class IExecutor:
    async def submit(self, fn, *args, **kwargs):
        raise NotImplementedError()


class EventPoolExecutor(IExecutor):
    def __init__(self, loop):
        from asyncio import BaseEventLoop

        self.loop: BaseEventLoop = loop

    async def submit(self, fn, *args, **kwargs):
        func = partial(fn, *args, **kwargs)

        future = self.loop.run_in_executor(None, func)
        name = fn.__name__
        print(f"eventloop start: {name=} {args=} {kwargs=}")
        result = await future
        print("eventloop end")
        return result


class DummyExecutor(IExecutor):
    async def submit(self, fn, *args, **kwargs):
        name = fn.__name__
        print(f"no eventloop start: {name=} {args=} {kwargs=}")
        result = fn(*args, **kwargs)
        print("no eventloop end")
        return result


class WebsocketClient(CommunicatorBase):
    @classmethod
    def create(cls, url, timeout=None, **options) -> "WebsocketClient":
        ws = websocket.create_connection(url, timeout=timeout, **options)
        executor = cls.get_executor()
        return cls(ws, executor)

    @classmethod
    def create_no_async(cls, url, timeout=None, **options):
        try:
            loop = asyncio.get_running_loop()
            raise Exception("Instances can only be created not in asyncio eventloop.")
        except RuntimeError:
            ...

        executor = DummyExecutor()

        ws = websocket.create_connection(url, timeout=timeout, **options)
        return cls(ws, executor).as_no_async()

    def __init__(self, websocket: websocket_WebSocket, executor: IExecutor = None):
        super().__init__()

        if not isinstance(websocket, websocket_WebSocket):
            raise TypeError(f"{websocket}")

        self.comm = websocket
        self.set_executor(executor)

    def set_executor(self, executor: IExecutor = None):
        if executor is None:
            executor = self.get_executor()

        self.executor = executor

    @staticmethod
    def get_executor():
        try:
            loop = asyncio.get_running_loop()
            executor = EventPoolExecutor(loop)
        except RuntimeError:
            executor = DummyExecutor()

        return executor

    async def accept(self) -> None:
        ...

    async def close(self):
        self.comm.close()

    def is_closed(self):
        return not self.comm.connected

    async def send_bytes(self, data) -> None:
        if not isinstance(data, bytes):
            raise TypeError(f"expected type: {bytes} actual type: {type(data)}")

        code = await self.executor.submit(
            self.comm.send, data, opcode=ABNF.OPCODE_BINARY
        )
        return code

    async def send_json(self, data) -> None:
        encoded = json.dumps(data, ensure_ascii=False)
        return await self.executor.submit(
            self.comm.send, encoded, opcode=ABNF.OPCODE_TEXT
        )

    async def receive_bytes(self):
        result = await self.executor.submit(self.comm.recv)
        if isinstance(result, str):
            return result.decode("utf-8")
        else:
            return result

    async def receive_json(self):
        payload = await self.executor.submit(self.comm.recv)
        return json.loads(payload)


class NoAsyncCommunicator:
    def __init__(self, comm: CommunicatorBase):
        self.comm = comm

    def __enter__(self):
        result = asyncio.run(self.comm.__aenter__())
        return self

    def __exit__(self, *args, **kwargs):
        result = asyncio.run(self.comm.__aexit__(*args, **kwargs))
        return self

    def accept(self) -> None:
        return asyncio.run(self.comm.accept())

    def close(self):
        return asyncio.run(self.comm.close())

    def is_closed(self):
        return self.comm.is_closed

    def send_bytes(self, data) -> None:
        return asyncio.run(self.comm.send_bytes(data))

    def send_json(self, data) -> None:
        return asyncio.run(self.comm.send_json(data))

    def receive_bytes(self):
        return asyncio.run(self.comm.receive_bytes())

    def receive_json(self):
        return asyncio.run(self.comm.receive_json())

    def send(self, msg: str, data=None, info=None):
        coro = CommunicatorBase.send(self.comm, msg, data=data, info=info)
        return asyncio.run(coro)

    def wait(self, msg: str):
        coro = CommunicatorBase.wait(self.comm, msg)
        return asyncio.run(coro)

    def request(self, msg: str, data=None, info: dict = None):
        coro = CommunicatorBase.request(self.comm, msg, data=data, info=info)
        return asyncio.run(coro)
