from . import commons
from . import keys

from cryptography.x509 import CertificateBuilder
from cryptography.x509 import Name as x509Name
from cryptography.x509 import NameAttribute as x509NameAttr
from cryptography.x509.oid import NameOID
from cryptography.x509 import BasicConstraints
from cryptography.x509 import Certificate
from cryptography.hazmat.backends import default_backend
import uuid
import datetime

async def write_cert(cert_data):
    """Write a certificate to a file.
    
    This function generates a certificate, and then writes it to a file.
    It is expected that the data passed to this function is a
    dictionary, which contains the following keys:
    cert_file: The certificate's file name.
    cert_metadata: The certificate's metadata. This is a dictionary which
        contains the following keys:
            auth: The certificate's authority metadata. This is a dictionary
            req: The certificate's requestor metadata. This is a dictionary
    priv_key: The certificate's key.
    
    Args:
        write_cert_data (dict): The data to pass to the function.
    
    Returns:
        <cryptography.x509.Certificate>
    
    Raises:
        AssertionError: If the data received is not in the required format.
    """
    cert_container = await commons.assert_referable(cert_data, "cert_metadata", {
        "function": None, "data": None
    })
    cert_metadata = cert_container["cert_metadata"]
    cert_prototype = CertificateBuilder(
        subject_name=x509Name([
            x509NameAttr(NameOID.COMMON_NAME, cert_metadata["req"]["cname"]),
            x509NameAttr(NameOID.ORGANIZATION_NAME, cert_metadata["req"]["org_name"]),
            x509NameAttr(NameOID.ORGANIZATIONAL_UNIT_NAME, cert_metadata["req"]["org_unit_name"])
        ]),
        issuer_name=x509Name([
            x509NameAttr(NameOID.COMMON_NAME, cert_metadata["auth"]["cname"]),
            x509NameAttr(NameOID.ORGANIZATION_NAME, cert_metadata["auth"]["org_name"]),
            x509NameAttr(NameOID.ORGANIZATIONAL_UNIT_NAME, cert_metadata["auth"]["org_unit_name"])
        ]),
        not_valid_before=datetime.datetime.today() - datetime.timedelta(days=1),
        not_valid_after=datetime.datetime.today() + datetime.timedelta(weeks=50),
        serial_number=int(uuid.uuid4()),
        public_key=cert_container["key_data"]["pub_key"]["key_code"]
    )
    cert_prototype.add_extension(BasicConstraints(ca=True, path_length=None), critical=True)

    cert_res = cert_prototype.sign(
        private_key = cert_data["key_data"]["priv_key"]["key_code"],
        algorithm = commons.hashes.SHA256(),
        backend = default_backend()
    )
    if(not isinstance(cert_res, Certificate)):
        raise TypeError("Certificate generation failed.")
    return cert_res

async def gen_cert(cert_data):
    cert_key_container = (await commons.assert_referable(cert_data, "key_data", {
        "function": None, "data": None
    }))
    cert_key_data = await commons.assert_referable(cert_key_container["key_data"], "priv_key", {
        "function": keys.write_priv_key, "data": cert_key_container["key_data"]
    })
    await commons.assert_referable(cert_key_data, "pub_key", {
        "function": keys.write_pub_key, "data": cert_key_data
    })

    await commons.assert_referable(cert_data, "cert", {
        "function": write_cert, "data": cert_key_container
    })
    prep_filename = commons.path.normpath(cert_key_data["key_owner"] + "_cert.crt")
    with open(prep_filename, "wb") as cert_write_file:
        cert_write_file.write(cert_data["cert"].public_bytes(
            encoding=commons.serialization.Encoding.PEM
        ))
    return cert_data

async def sign_cert(csr_data):
    print(csr_data)