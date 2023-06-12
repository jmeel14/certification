from cryptography.hazmat.primitives import serialization, hashes
from os import path
from asyncio import iscoroutinefunction

async def assert_referable(referable, ref_key, cause):
    """Assert a referable key, and generate it if it doesn't exist.
    
    This function assumes that a key exists in a dictionary, and if it doesn't, it will generate it.
    
    Args:
        referable (dict): The dictionary to check.
        ref_key (str): The key to check.
        cause (dict): The cause of the key not existing. This is
            a dictionary with two keys: "function" and "data".
            "function" is the function to call to generate the key
            and "data" is the data to pass to the function.
    
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
    if(cause["function"]):
        if(iscoroutinefunction(cause["function"])):
            referable[ref_key] = await cause["function"](cause["data"])
        else:
            referable[ref_key] = cause["function"](cause["data"])
    return referable