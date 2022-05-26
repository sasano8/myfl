from myfl.core.communicators import StandaloneCommunicator
from myfl.core.federators import Federator, ClientFederatorBase


class ClientBase:
    def login(self):
        raise NotImplementedError()

    def logout(self):
        raise NotImplementedError()


class StandaloneClient(ClientBase):
    def __init__(self, cwd):
        self.comm = StandaloneCommunicator()
        self.comm.add_events([self.on_connect, self.on_ready, self.on_success])

    async def run(self):
        server = Federator(self.comm, mode="server")

        async with server:
            await server.run()

    async def _run_client(self):
        comm = self.comm
        await comm.send("s1_send_identifer", "mac_address")
        await comm.wait("s2_recieve_identifier_and_send_job_config")
        await comm.wait("s4_recieve_ok_and_send_model")
        await comm.wait("s6_revieve_model_diff_and_send_model")
        await comm.send("s7_revieve_model_and_send_ok")

    async def on_connect_to_server(self, val):
        await self.comm.send("on_connect")

    async def on_connect(self, val):
        await self.comm.send("on_ready_to_server")

    async def on_ready_to_server(self, val):
        await self.comm.send("on_ready")

    async def on_ready(self, val):
        ...

    async def on_success(self, val):
        ...

    async def on_error(self, val):
        ...

    async def on_complete(self, result: bool):
        ...


class RemoteClient(ClientBase):
    def __init__(self, host):
        ...
