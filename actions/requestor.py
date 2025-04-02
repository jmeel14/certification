import json
from . import commons

async def filter_for(str_target, str_body):
    """Filter a string for a target.
    
    This function filters a string for a target, and returns the
    result.

    Args:
        str_target (str): The target to filter for.
        str_body (str): The string to filter.
    
    Returns:
        str: The result of the filter.
    """
    print(str_body)
    re_pre = ".{0,}" + "({})".format(str_target) + ".{0,}"
    re_res = commons.regx_search(re_pre, str_body)
    return re_res.group(0) if re_res else None

async def process_request(requestor, processor_func):
    req_buff = { "conn": requestor[0], "addr": requestor[1] }

    req = {
        "req_conn": req_buff["conn"],
        "req_data": (req_buff["conn"].recv(4096)).decode()
    }
    print(await filter_for("req_name", req["req_data"]))
    await commons.assert_referable(req, "req_name", {
        "function": filter_for, "data": ("req_name", req["req_data"])
    })
    await commons.assert_func_call(processor_func, req)

async def acknowledge(req, processor_func):
    print("Server received a connection!")
    req.send(json.dumps({"message": "ack"}).encode())
    await processor_func(req)

async def goodbye(req):
    print("Server received a goodbye!")
    req.send(json.dumps({"message": "bye"}).encode())
    req.close()