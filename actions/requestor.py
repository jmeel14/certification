import json
import notice
from . import commons

async def process_request(self, requestor, processor_func):
    req_buff = { "conn": requestor[0], "addr": requestor[1] }

    req = {
        "req_conn": req_buff["conn"],
        "req_data": (req_buff["conn"].recv(2048)).decode()
    }
    try:
        commons.assert_referable(
            req, "req_name",
            lambda any: any, json.loads(req["req_data"])
        )
        await commons.assert_func_call(self, processor_func, req)
    except:
        notice.gen_ntc(
            'warn', 'mini', 
            "Non-JSON data given to JSON request processor. Request ignored."
        )

async def acknowledge(self, req, processor_func):
    print("Server received a connection!")
    req.send(json.dumps({"message": "ack"}).encode())
    await processor_func(self, req)

async def goodbye(self, req, processor_func):
    print("Server received a goodbye!")
    req.send(json.dumps({"message": "bye"}).encode())
    req.close()
    await processor_func(self)