import asyncio
import socket

import actions

class CACertGenerator:
    def __init__(self, data_dict):
        self.cert_data = data_dict
        self.serv_config = None
        self.server = None
        self.run_loop = None
        self.alive = False
        self.actions = dict()
        self.answers = dict()
    
    async def build_action(self, action_data):
        """ Build an action used by the server.

            This function builds an action used by the server, and
            adds it to the server's action list.

            Args:
                action_data (dict): The data to pass to the function. Expected keys:
                    act_name (str): The name of the action.
                    act_key (str): The key to check.
                    act_func (function): The function to call to generate the key.
        """
        action_dict = await actions.commons.assert_referable(action_data, "act_name", {
            "function": None, "data": None
        })
        self.actions[action_dict["act_name"]] = action_dict["act_func"]
    
    async def setup(self):
        """Server setup function."""
        actions_list = [
            ["write_priv_key", actions.keys.write_priv_key],
            ["write_pub_key", actions.keys.write_pub_key],
            ["write_cert", actions.certs.write_cert],
            ["gen_cert", actions.certs.gen_cert]
        ]
        for action in actions_list:
            await self.build_action({"act_name": action[0], "act_func": action[1]})
        
        await self.actions["gen_cert"](self.cert_data)
    
    async def live(self, sv_data):
        """Server initialization function."""
        await self.setup()

        self.server = socket.socket()
        self.server.bind(sv_data)
        self.server.listen()
        print("Certification Authority server now live, listening on {0}:{1}".format(sv_data[0], sv_data[1]))
        self.alive = True

        while self.alive:
            raw_req = self.server.accept()
            await actions.requestor.process_request(raw_req, self.answer)
    
    async def answer(self, req_data):
        """Server response function."""
        if(req_data["request"] in self.answers):
            await self.actions[self.answers[req_data["request"]]](req_data)


LOCAL_CA = CACertGenerator({
    "cert_metadata": {
        "auth": {
            "cname": "Lol",
            "org_name": "Lol", "org_unit_name": "Lol"
        },
        "req": {
            "cname": "NUL",
            "org_name": "Lol", "org_unit_name": "Lol"
        }
    },
    "key_data": { "key_owner": "Lol", "key_pass": "password1234" }
})

SETUP_TEXT = ["""
Welcome to the Certification Authority setup wizard.\n\n\
\
This wizard will guide you through the process of setting up the\n\
Certification Authority, which is used to sign certificates for \n\
any secure web server.\n
Please enter the address that you would like to bind the server to. 
This should be an IP address.
""",
"""
Please enter the port that you would like to bind the server to.
"""
]

LOCAL_CA.run_loop = asyncio.get_event_loop()
LOCAL_CA.run_loop.run_until_complete(
    LOCAL_CA.live((
        input(SETUP_TEXT[0]), int(input(SETUP_TEXT[1]))
    ))
)