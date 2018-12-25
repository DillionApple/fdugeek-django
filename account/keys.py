__private_key_file = open("rsa-keys", "rb")
__public_key_file = open("rsa-keys.pub", "rb")

PRIVATE_KEY = __private_key_file.read()
PUBLIC_KEY = __public_key_file.read()
