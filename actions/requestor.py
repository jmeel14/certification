import json
from . import commons
from asyncio import iscoroutinefunction

async def process_request(requestor, processor_func):
    req_buff = { "conn": requestor[0], "addr": requestor[1] }

    req_data = {
        "request": (req_buff["conn"].recv(5)).decode(),
        "req_conn": req_buff["conn"]
    }

    await commons.assert_func_call(processor_func, req_data)

async def acknowledge(req, processor_func):
    print("Server received a connection!")
    req.send(json.dumps({"message": "ack"}).encode())
    await processor_func(req)
    req.close()