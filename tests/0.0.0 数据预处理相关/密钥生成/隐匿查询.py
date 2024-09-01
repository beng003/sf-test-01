from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os


def generate_oprf_key_with_crypto(file_path: str):
    # 使用32字节的安全随机数
    oprf_key = HKDF(algorithm=hashes.SHA256(),
                    length=32,
                    salt=None,
                    info=b"OPRF key generation",
                    backend=default_backend()).derive(os.urandom(32))

    # 将密钥写入文件
    with open(file_path, 'wb') as f:
        f.write(oprf_key)

    print(f"OPRF私钥已生成并保存到 {file_path}")


# 保存到绝对路径
generate_oprf_key_with_crypto(
    "/mnt/users/beng003/sf-test/scr/data/configuration/alice_oprf_key.bin")


def load_oprf_key(file_path: str) -> bytes:
    with open(file_path, 'rb') as f:
        oprf_key = f.read()
    return oprf_key


# 读取密钥
oprf_key = load_oprf_key(
    "/mnt/users/beng003/sf-test/scr/data/configuration/alice_oprf_key.bin")
print(f"读取的 OPRF 私钥: {oprf_key}")
