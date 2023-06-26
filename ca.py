import asyncio
import socket

import actions
import setup

class CACertGenerator:
    def __init__(self):
        self.cert_data = dict()
        self.serv_config = None
        self.server = None
        self.run_loop = None
        self.alive = False
        self.actions = dict()
        self.answers = dict()
    
    async def live(self):
        """Server initialization function."""
        await setup.setup(self.cert_data, self.actions, self.answers)

        self.server = socket.socket()
        self.server.bind((self.cert_data["host"]["addr"], self.cert_data["host"]["port"]))
        self.server.listen()
        print("Certification Authority server now live, listening on {0}:{1}".format(
            self.cert_data["host"]["addr"], self.cert_data["host"]["port"]
        ))
        self.alive = True

        while self.alive:
            raw_req = self.server.accept()
            await actions.requestor.process_request(raw_req, self.answer)
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
        req_clean = await actions.commons.assert_referable(
            req, "req_name", { "function": None, "data": None }
        )
        if(req_clean["req_name"] in self.answers):
            action_ref = self.actions[self.answers[req["req_name"]]]
            await action_ref(req["req_conn"], req["req_data"])

LOCAL_CA = CACertGenerator()

LOCAL_CA.run_loop = asyncio.get_event_loop()
LOCAL_CA.run_loop.run_until_complete(
    LOCAL_CA.live()
)