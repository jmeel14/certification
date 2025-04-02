import asyncio
import socket

import notice

from . import actions
from . import setup

TEST_RESP = b"""
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
    <head>
        <title>Sample page</title>
        <script>
            setTimeout(()=>{
                document.querySelector("button").addEventListener("mousedown", ()=>{
                    console.log("Issuing communication attempt with server...");
                    let instXHR = new XMLHttpRequest();
                    instXHR.open('POST', './', true);
                    instXHR.setRequestHeader('Content-Type', 'text/json');
                    instXHR.send(new Blob(['idk_what_this_is'], {'msg': "Nooooootiiicccce meeeeeeeeeee"}), (res)=>{
                        console.log("Server responded with:");
                        console.log(res);
                    });
                });
            }, 50)
        </script>
    </head>
    <body>
        <textarea placeholder="Insert things to say here"></textarea>
        <button>Click me!</button>
    </body>
</html>
"""

class CACertGenerator:
    def __init__(self):
        self.cert_data = dict()
        self.serv_config = None
        self.server = None
        self.run_loop = None
        self.alive = False
        self.actions = dict()
        self.answers = dict()
    
    def set_ready(self, predefs=None):
        self.run_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.run_loop)
        self.run_loop.run_until_complete(self.live(predefs))
    
    async def live(self, predefs=None):
        """Server initialization function."""
        
        if(predefs):
            self.cert_data = {
                "is_set": True,
                "host": {
                    "addr": predefs["host"]["addr"],
                    "port": predefs["host"]["port"],
                    "public_html": predefs["host"]["public_html"]
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
            raw_req[0].send(TEST_RESP)
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