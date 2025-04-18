import asyncio
import socket

import notice

from . import actions
from . import setup

class CACertGenerator:
    def __init__(self):
        self.cert_data = dict()
        self.serv_config = None
        self.server = None
        self.run_loop = None
        self.alive = False
        self.actions = dict()
        self.answers = dict()

    async def live(self, predefs=None):
        """Server initialization function."""
        
        if(predefs):
            self.cert_data = {
                "is_set": True,
                "host": {
                    "addr": predefs["host"]["addr"],
                    "port": predefs["host"]["port"],
                    "path": predefs["host"]["path"]
                },
                "cert_metadata": {
                    "auth": {
                        "cname": predefs["cert_metadata"]["auth"]["cname"],
                        "org_name": predefs["cert_metadata"]["auth"]["org_name"],
                        "org_unit_name": predefs["cert_metadata"]["auth"]["org_unit"]
                    }
                }
            }
        await setup.setup(self.cert_data, self.actions, self.answers)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.cert_data["host"]["addr"], self.cert_data["host"]["port"]))
        self.server.listen()
        
        notice.gen_ntc(
            "success",
            "title",
            "Certification Authority server now live, listening on {0}:{1}".format(
                self.cert_data["host"]["addr"], self.cert_data["host"]["port"]
            )
        )
        self.alive = True

        while self.alive:
            raw_req = self.server.accept()
            await actions.requestor.process_request(raw_req, self.answer)
            raw_req[0].send(b"Server acknowledges you")
            # Requestor's process_request should convert the request into the following format:
            # { "req_name": <str>, "req_conn": <socket.socket>, "req_data": <dict> }
    
    async def answer(self, req):
        """Server response function.
        
        This function is called when the server receives a request. It is imperative
        that all responses are handled as coroutines, as this is where the server
        will receive many requests, and it is important that the server can handle
        them without blocking.

        """
        print(req)
        """req_clean = await actions.commons.assert_referable(
            req, "req_name", { "function": None, "data": None }
        )
        if(req_clean["req_name"] in self.answers):
            action_ref = self.actions[self.answers[req["req_name"]]]
            await action_ref(req["req_conn"], req["req_data"])"
        """