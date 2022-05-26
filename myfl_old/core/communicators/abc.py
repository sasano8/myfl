import asyncio
from typing import TypedDict, Union, Tuple, Any


class ResultMsg(TypedDict):
    is_error: bool
    info: dict


class CommunicatorBase:
    def __init__(self):
        self.events: list = None

    def as_no_async(self) -> "NoAsyncCommunicator":
        return NoAsyncCommunicator(self)

    async def __aenter__(self) -> "CommunicatorBase":
        await self.accept()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.close()

    async def accept(self):
        raise NotImplementedError()

    async def close(self):
        raise NotImplementedError()

    async def send_bytes(self, data):
        raise NotImplementedError()

    async def send_json(self, data):
        raise NotImplementedError()

    async def receive_bytes(self):
        raise NotImplementedError()

    async def receive_json(self):
        raise NotImplementedError()

    def is_closed(self):
        raise NotImplementedError()

    async def wait_disconnected(self, interval: float = 0.1):
        while not self.is_closed():
            await asyncio.sleep(interval)

    async def send(self, msg: str, data=None, info: Any = None):
        if isinstance(data, bytes):
            obj = {"type": "bytes", "msg": msg, "info": info}
            await self.send_json(obj)
            await self.send_bytes(data)
        else:
            obj = {"type": "json", "msg": msg, "info": info, "data": data}
            await self.send_json(obj)

    async def wait(self, msg: str, callback=None):
        data = await self.receive_json()

        if "msg" not in data:
            raise RuntimeError("require msg")

        if data["msg"] != msg:
            raise RuntimeError(f"msg mismatch. expected: {msg} actual: {data['msg']}")

        typ = data.get("type", None)
        info = data.get("info", None)

        if typ == "json":
            result = info, data["data"]
        elif typ == "bytes":
            result = info, await self.receive_bytes()
        elif typ is None:
            result = info, None
        else:
            raise TypeError(f"Unkown msg type: {typ}")

        if callback:
            if "is_async":
                return await callback(*result)
            else:
                raise NotImplementedError()
        else:
            return result

    async def request(self, msg: str, data=None, info: dict = None):
        await self.send(msg, data, info)
        return await self.wait(msg)

    def add_events(self, events: Union[list, dict]):
        if self.events is not None:
            raise RuntimeError()
        else:
            self.events = {}

        if isinstance(events, list):
            events = {x.__name__: x for x in events}

        if not isinstance(events, dict):
            raise TypeError()

        if not self.events:
            self.events = events.copy()
        else:
            self.events = {**self.events, **events}


class NoAsyncCommunicator:
    def __init__(self, comm: "CommunicatorBase"):
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
