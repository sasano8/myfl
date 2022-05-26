import json
import asyncio

# if TYPE_CHECKING:
from fastapi import WebSocket
from starlette.websockets import WebSocketState

from .abc import CommunicatorBase


class WebsocketCommunicator(CommunicatorBase):
    def __init__(self, websocket: WebSocket):
        super().__init__()

        if not isinstance(websocket, WebSocket):
            raise TypeError(f"{websocket}")

        self.comm = websocket

    async def accept(self) -> None:
        await self.comm.accept()

    async def close(self):
        await self.comm.close()

    def is_closed(self):
        return self.comm.application_state == WebSocketState.DISCONNECTED

    async def send_bytes(self, data) -> None:
        await self.comm.send_bytes(data)

    async def send_json(self, data) -> None:
        await self.comm.send_json(data)

    async def receive_bytes(self):
        return await self.comm.receive_bytes()

    async def receive_json(self):
        return await self.comm.receive_json()


class StandaloneCommunicator(CommunicatorBase):
    def __init__(self):
        super().__init__()

        from collections import deque

        self.buf = deque()
        self._is_closed = False

    async def accept(self) -> None:
        ...

    async def close(self) -> None:
        ...

    def is_closed(self):
        return self._is_closed

    async def send_bytes(self, data) -> None:
        if not isinstance(data, bytes):
            raise TypeError()
        self.buf.append(data)

    async def send_json(self, data) -> None:
        self.buf.append(json.dumps(data))

    async def receive_bytes(self):
        buff = self.buff
        while not buff:
            await asyncio.sleep(0.05)

        data = self.buf.popleft()

        if isinstance(data, str):
            return data.encode("utf-8")
        elif isinstance(data, bytes):
            return data
        else:
            raise TypeError()

    async def receive_json(self):
        buff = self.buff
        while not buff:
            await asyncio.sleep(0.05)

        data = self.buf.popleft()
        return json.load(data)


class MultiprocessCommunicator(StandaloneCommunicator):
    def __init__(self):
        super().__init__()

        raise NotImplementedError()


class DistrebutedCommunicator(StandaloneCommunicator):
    def __init__(self):
        super().__init__()

        raise NotImplementedError()


def create_connection(comm=None):
    obj = None
    if comm is None:
        obj = StandaloneCommunicator()
    elif isinstance(comm, WebSocket):
        obj = WebsocketCommunicator(comm)
    elif isinstance(comm, CommunicatorBase):
        obj = comm
    # elif isinstance(comm, ?):
    #     return MultiprocessCommunicator(comm)
    # elif isinstance(comm, ?):
    #     return DistrebutedCommunicator(comm)
    else:
        raise TypeError()

    return obj
