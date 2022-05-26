from .communicators import CommunicatorBase


class Federator:
    def __init__(self, comm: CommunicatorBase, mode: str):
        self.comm = comm
        self.mode = mode
        self.closed = False

    async def __aenter__(self):
        await self.comm.accept()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.comm.close()

    def is_server(self):
        return self.mode == "server"

    def is_client(self):
        return self.mode == "client"

    async def run(self):
        await self.comm.wait_disconnected(interval=0.1)

        # if self.mode == "client":
        #     await self.s1_send_identifer()
        #     await self.s3_recieve_job_config_and_send_ok()
        #     await self.s5_revieve_model_and_send_model_diff()  # train on client
        #     await self.s7_revieve_model_and_send_ok()
        # elif self.mode == "server":
        #     await self.s2_recieve_identifier_and_send_job_config()
        #     await self.s4_recieve_ok_and_send_model()  # train on server
        #     await self.s6_revieve_model_diff_and_send_model()  # aggregate/transfer
        #     await self.s8_revieve_ok()
        # else:
        #     raise Exception()

    async def s1_send_identifer(self):
        await self.comm.send(
            "s1_send_identifer", "mac_address"
        )  # device or server host?
        # await self.comm.send_json({"msg": "mac_address"})  # device or server host?

    async def s2_recieve_identifier_and_send_job_config(self):
        identifier = await self.comm.wait("s1_send_identifer")
        msg = {"msg": "job_config"}
        await self.comm.send_json("s2_recieve_identifier_and_send_job_config", msg)

    async def s3_recieve_job_config_and_send_ok(self):
        result = await self.comm.wait("s2_recieve_identifier_and_send_job_config")
        msg = {"msg": "ok"}
        await self.comm.send_json("s3_recieve_job_config_and_send_ok", msg)

    async def s4_recieve_ok_and_send_model(self):
        result = await self.comm.wait("s3_recieve_job_config_and_send_ok")
        msg = {"msg": "send_binary_model"}
        await self.comm.send("s4_recieve_ok_and_send_model", msg)

    async def s5_revieve_model_and_send_model_diff(self):
        msg = await self.comm.wait("s4_recieve_ok_and_send_model")
        await self.comm.send(
            "s5_revieve_model_and_send_model_diff", {"msg": "global_parameter"}
        )

    async def s6_revieve_model_diff_and_send_model(self):
        msg = await self.comm.wait("s5_revieve_model_and_send_model_diff")
        await self.comm.send(
            "s6_revieve_model_diff_and_send_model", {"msg": "aggrated_model"}
        )

    async def s7_revieve_model_and_send_ok(self):
        msg = await self.comm.wait("s6_revieve_model_diff_and_send_model")
        await self.comm.send("s7_revieve_model_and_send_ok", {"msg": "ok"})

    async def s8_revieve_ok(self):
        msg = await self.comm.wait("s7_revieve_model_and_send_ok")
