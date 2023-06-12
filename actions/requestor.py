import json
from asyncio import iscoroutinefunction

async def process_request(requestor, processor_func):
    req_buff = { "conn": requestor[0], "addr": requestor[1] }

    req_data = req_buff["conn"].recv(5)
    req_data_str = req_data.decode()
    req_cleaned = req_data_str
    print(req_cleaned)

    if(iscoroutinefunction(processor_func)):
        await processor_func(req_cleaned)
    else:
        processor_func(req_cleaned)

async def acknowledge(requestor, processor_func):
    print("Server received a connection!")
    req_buff = { "conn": requestor[0], "addr": requestor[1] }
    req_buff["conn"].send(json.dumps({"message": "ack"}).encode())
    await processor_func(req_buff["conn"].recv(3))
    req_buff["conn"].close()