"""加密工具"""

import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5


def rsa_encrypt(password: str, modulus_b64: str, exponent_b64: str) -> str:
    """使用 RSA 公钥加密密码"""
    modulus_hex = base64.b64decode(modulus_b64).hex()
    exponent_hex = base64.b64decode(exponent_b64).hex()
    n = int(modulus_hex, 16)
    e = int(exponent_hex, 16)
    key = RSA.construct((n, e))
    cipher = PKCS1_v1_5.new(key)
    encrypted = cipher.encrypt(password.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")


def ef(text: str) -> str:
    """滑块验证码轨迹加密 - Base64(UTF-8)"""
    return base64.b64encode(text.encode("utf-8")).decode("utf-8")
