import json
import notice
from . import commons

async def process_request(requestor, processor_func):
    req_buff = { "conn": requestor[0], "addr": requestor[1] }

    req = {
        "req_conn": req_buff["conn"],
        "req_data": (req_buff["conn"].recv(2048)).decode()
    }
    try:
        inst_req_data = json.loads(req["req_data"])
        req["req_name"] = commons.assert_referable(
            inst_req_data, "req_name",
            None, None
        )
        test_req = await commons.assert_func_call(processor_func, req)
        if not test_req:
            notice.gen_ntc('warn', 'mini', "Received non-existing command. Request ignored.")
    except BaseException as someErr:
        notice.gen_ntc(
            'warn', 'mini', 
            "Non-JSON data or invalid function  given to JSON request processor. Request ignored."
        )
        print(someErr)


async def acknowledge(req, processor_func):
    print("Server received a connection!")
    req["req_conn"].send(json.dumps({"message": "ack"}).encode())
    print(req)
    await processor_func(req)

async def goodbye(req, processor_func):
    print("Server received a goodbye!")
    req["req_conn"].send(json.dumps({"message": "bye"}).encode())
    req["req_conn"].close()
    await processor_func("A connection was terminated")