from cryptography.hazmat.primitives import serialization, hashes
from os import path
from asyncio import iscoroutinefunction
from re import search as regx_search

async def assert_func_call(func, *data):
    """Assert a function  call, and handle it whether coroutine or not.

    This function assumes that a function is given, and will attempt to
    call it using given data, and if it is a coroutine, it will await it.

    Args:
        func (function): The function to call.
        data (any): The data to pass to the function.
    
    Returns:
        any: The result of the function call.
    
    Raises:
        AssertionError: If the function is not a function.
    """
    if(func):
        if(not callable(func)):
            raise AssertionError("Function treatment on non-function type.")
        if(iscoroutinefunction(func)):
            return await func(*data)
        else:
            return func(*data)
    else:
        return data

async def assert_referable(referable, ref_key, cause):
    """Assert a referable key, and generate it if it doesn't exist.
    
    This function assumes that a key exists in a dictionary, and if it doesn't,
    it will generate it.
    
    Args:
        referable (dict): The dictionary to check.
        ref_key (str): The key to check.
        cause (dict): The cause that will create the key if it doesn't exist. It
            should have the following keys:
                function: The function to call to generate the key.
                data: The data to pass to the function.
    
    Returns:
        referable: The original dictionary, with the key asserted.
    
    Raises:
        AssertionError: If the key doesn't exist, and the cause is
            a dictionary but doesn't have "function", and no "data" either.
    """
    if(not ref_key in referable):
        if(not cause["function"]):
            if(cause["data"]):
                referable[ref_key] = cause["data"]
            else:
                assert_err_str = [
                    "Cannot assert", " {}".format(ref_key),
                    " without a cause function, and auto-generation",
                    " is undesirable here!"
                ]
                raise AssertionError(
                    "".join(assert_err_str)
                )
    referable[ref_key] = await assert_func_call(cause["function"], cause["data"])

    return referable