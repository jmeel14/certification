from asyncio import iscoroutinefunction
from os import path
from collections.abc import Callable
import notice

async def assert_func_call(func:Callable, *data):
    """Assert a function  call, and handle it whether coroutine or not.

    This function assumes that a function is given, and will attempt to
    call it using given data, and if it is a coroutine, it will await it.

    Args:
        func (function): The function to call.
        data (any): The data to pass to the function.
    
    Returns:
        any: The result of the function call.
    
    Raises:
        AssertionError: If field 'function' is not a function.
    """
    if not callable(func) and not iscoroutinefunction(func):
        notice.gen_ntc('critical', 'mini', "Call attempted to non-callable " + str(func))
        return None
    return await func(*data) if iscoroutinefunction(func) else func(*data)

def assert_referable(src:dict, ref, cause:Callable, *args):
    """Assert a key exists in a dict, and if not, then try to cause it.
    
    This will check for the existence of a key in the given dict, and if
    it cannot find it, it will attempt to create a new key value, using
    a given function with arguments. cause can be left blank to make a
    literal assignment.
    
    Returns:
        any: Value of the given key.
    
    Raises:
        AssignFailure: If any error occurs with the given types for args src,
        ref, and cause, or if the given arg cause is malfunctioning.
    """
    if not ref in src:
        try:
            src[ref] = cause(*args)
        except KeyError as AssignFailure:
            raise AssignFailure
    return src[ref]