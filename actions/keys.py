from . import commons
from cryptography.hazmat.backends import openssl

async def write_priv_key(key_data):
    """Write a key to a file.
    
    This function generates a key, and then writes it to a file.
    It is expected that the data passed to this function is a
    dictionary, which contains the following keys:
    key_file: The key's file name.
    key_pass: The key's password.
    
    Args:
        write_key_data (dict): The data to pass to the function.
    
    Returns:
        <cryptography.hazmat.backends.openssl.rsa._RSAPrivateKey>
    
    Raises:
        AssertionError: If the data received is not in the required format.
    """

    inst_key = openssl.backend.generate_rsa_private_key(
        public_exponent=65537, key_size=1024
    )
    if(not isinstance(inst_key, openssl.rsa._RSAPrivateKey)):
        raise AssertionError("Key generation failed.")
    prep_filename = commons.path.normpath(key_data["key_owner"] + "_priv.key")
    with open(prep_filename, "wb") as key_write_file:
        key_write_file.write(inst_key.private_bytes(
            encoding=commons.serialization.Encoding.PEM,
            format=commons.serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=commons.serialization.BestAvailableEncryption(
                key_data["key_pass"].encode()
            )
        ))
    return { "key_file": prep_filename, "key_code": inst_key,  }

async def write_pub_key(key_data):
    """Write a key to a file.
    
    This function generates a key, and then writes it to a file.
    It is expected that the data passed to this function is a
    dictionary, which contains the following keys:
    key_file: The key's file name.
    key_pass: The key's password.
    
    Args:
        write_key_data (dict): The data to pass to the function.
    
    Returns:
        <cryptography.hazmat.backends.openssl.rsa._RSAPrivateKey>
    
    Raises:
        AssertionError: If the data received is not in the required format.
        AssertionError: If the key generation failed.
    """
    key_obj = await commons.assert_referable(key_data, "priv_key", {
        "function": write_priv_key, "data": key_data
    })
    inst_key = key_obj["priv_key"]["key_code"].public_key()
    if(not isinstance(inst_key, openssl.rsa._RSAPublicKey)):
        raise AssertionError("Public key generation failed.")
    prep_filename = commons.path.normpath(key_data["key_owner"] + "_pub.key")
    with open(prep_filename, "wb") as key_write_file:
        key_write_file.write(inst_key.public_bytes(
            encoding=commons.serialization.Encoding.PEM,
            format=commons.serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    return { "key_file": prep_filename, "key_code": inst_key }