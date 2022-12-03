import getpass
from Crypto.Cipher import AES
import base64
import sys

# this version only works on python 3.0+
# using pip install pycrypto to install crypto module
# the block size for the cipher object; must be 16, 24, or 32 for AES
BLOCK_SIZE = 32
PADDING = ' '  #
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

def encrpytKey(Password, Key):
    # encrypt with AES, encode with base64
    EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
    cipher = AES.new(pad(Password))
    # encode the key
    encoded = EncodeAES(cipher, Key)
    return encoded

msg_text = sys.argv[1]
password = sys.argv[2] # enter password without echo

encoded = encrpytKey(password, msg_text)
print ( 'Encrypted string:', encoded )

f=open('/map_validation_files/storageKey.txt','wb')
f.write(encoded)
f.close()