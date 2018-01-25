from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Util import Counter

import base64
import binascii
import json
import os
import random
import struct
import sys
import urllib

sid = ''
seqno = random.randint(0, 0xFFFFFFFF)

master_key = ''
rsa_priv_key = ''

def base64urldecode(data):
  data += '=='[(2 - len(data) * 3) % 4:]
  for search, replace in (('-', '+'), ('_', '/'), (',', '')):
    data = data.replace(search, replace)
  return base64.b64decode(data)

def base64urlencode(data):
  data = base64.b64encode(data)
  for search, replace in (('+', '-'), ('/', '_'), ('=', '')):
    data = data.replace(search, replace)
  return data

def a32_to_str(a):
  return struct.pack('>%dI' % len(a), *a)

def a32_to_base64(a):
  return base64urlencode(a32_to_str(a))

def str_to_a32(b):
  if len(b) % 4: # Add padding, we need a string with a length multiple of 4
    b += '\0' * (4 - len(b) % 4)
  return struct.unpack('>%dI' % (len(b) / 4), b)

def base64_to_a32(s):
  return str_to_a32(base64urldecode(s))

def aes_cbc_encrypt(data, key):
  encryptor = AES.new(key, AES.MODE_CBC, '\0' * 16)
  return encryptor.encrypt(data)

def aes_cbc_decrypt(data, key):
  decryptor = AES.new(key, AES.MODE_CBC, '\0' * 16)
  return decryptor.decrypt(data)

def aes_cbc_encrypt_a32(data, key):
  return str_to_a32(aes_cbc_encrypt(a32_to_str(data), a32_to_str(key)))

def aes_cbc_decrypt_a32(data, key):
  return str_to_a32(aes_cbc_decrypt(a32_to_str(data), a32_to_str(key)))

def stringhash(s, aeskey):
  s32 = str_to_a32(s)
  h32 = [0, 0, 0, 0]
  for i in xrange(len(s32)):
    h32[i % 4] ^= s32[i]
  for _ in xrange(0x4000):
    h32 = aes_cbc_encrypt_a32(h32, aeskey)
  return a32_to_base64((h32[0], h32[2]))

def prepare_key(a):
  pkey = [0x93C467E3, 0x7DB0C7A4, 0xD1BE3F81, 0x0152CB56]
  for _ in xrange(0x10000):
    for j in xrange(0, len(a), 4):
      key = [0, 0, 0, 0]
      for i in xrange(4):
        if i + j < len(a):
          key[i] = a[i + j]
      pkey = aes_cbc_encrypt_a32(pkey, key)
  return pkey

def encrypt_key(a, key):
  return sum((aes_cbc_encrypt_a32(a[i:i+4], key) for i in xrange(0, len(a), 4)), ())

def decrypt_key(a, key):
  return sum((aes_cbc_decrypt_a32(a[i:i+4], key) for i in xrange(0, len(a), 4)), ())

def mpi2int(s):
  return int(binascii.hexlify(s[2:]), 16)

def api_req(req):
  global seqno
  url = 'https://g.api.mega.co.nz/cs?id=%d%s' % (seqno, '&sid=%s' % sid if sid else '')
  seqno += 1
  return json.loads(post(url, json.dumps([req])))[0]

def post(url, data):
  return urllib.urlopen(url, data).read()

def login(email, password):
  global sid, master_key, rsa_priv_key
  password_aes = prepare_key(str_to_a32(password))
  uh = stringhash(email.lower(), password_aes)
  res = api_req({'a': 'us', 'user': email, 'uh': uh})

  enc_master_key = base64_to_a32(res['k'])
  master_key = decrypt_key(enc_master_key, password_aes)
  if 'tsid' in res:
    tsid = base64urldecode(res['tsid'])
    if a32_to_str(encrypt_key(str_to_a32(tsid[:16]), master_key)) == tsid[-16:]:
      sid = res['tsid']
  elif 'csid' in res:
    enc_rsa_priv_key = base64_to_a32(res['privk'])
    rsa_priv_key = decrypt_key(enc_rsa_priv_key, master_key)

    privk = a32_to_str(rsa_priv_key)
    rsa_priv_key = [0, 0, 0, 0]

    for i in xrange(4):
      l = ((ord(privk[0]) * 256 + ord(privk[1]) + 7) / 8) + 2;
      rsa_priv_key[i] = mpi2int(privk[:l])
      privk = privk[l:]

    enc_sid = mpi2int(base64urldecode(res['csid']))
    decrypter = RSA.construct((rsa_priv_key[0] * rsa_priv_key[1], 0L, rsa_priv_key[2], rsa_priv_key[0], rsa_priv_key[1]))
    sid = '%x' % decrypter.key._decrypt(enc_sid)
    sid = binascii.unhexlify('0' + sid if len(sid) % 2 else sid)
    sid = base64urlencode(sid[:43])

def enc_attr(attr, key):
  attr = 'MEGA' + json.dumps(attr)
  if len(attr) % 16:
    attr += '\0' * (16 - len(attr) % 16)
  return aes_cbc_encrypt(attr, a32_to_str(key))

def dec_attr(attr, key):
  attr = aes_cbc_decrypt(attr, a32_to_str(key)).rstrip('\0')
  return json.loads(attr[4:]) if attr[:6] == 'MEGA{"' else False

def get_chunks(size):
  chunks = {}
  p = pp = 0
  i = 1

  while i <= 8 and p < size - i * 0x20000:
    chunks[p] = i * 0x20000;
    pp = p
    p += chunks[p]
    i += 1

  while p < size:
    chunks[p] = 0x100000;
    pp = p
    p += chunks[p]

  chunks[pp] = size - pp
  if not chunks[pp]:
    del chunks[pp]

  return chunks

def uploadfile(filename):
  infile = open(filename, 'rb')
  size = os.path.getsize(filename)
  ul_url = api_req({'a': 'u', 's': size})['p']

  ul_key = [random.randint(0, 0xFFFFFFFF) for _ in xrange(6)]
  encryptor = AES.new(a32_to_str(ul_key[:4]), AES.MODE_CTR, counter = Counter.new(128, initial_value = ((ul_key[4] << 32) + ul_key[5]) << 64))

  file_mac = [0, 0, 0, 0]
  for chunk_start, chunk_size in sorted(get_chunks(size).items()):
    chunk = infile.read(chunk_size)

    chunk_mac = [ul_key[4], ul_key[5], ul_key[4], ul_key[5]]
    for i in xrange(0, len(chunk), 16):
      block = chunk[i:i+16]
      if len(block) % 16:
        block += '\0' * (16 - len(block) % 16)
      block = str_to_a32(block)
      chunk_mac = [chunk_mac[0] ^ block[0], chunk_mac[1] ^ block[1], chunk_mac[2] ^ block[2], chunk_mac[3] ^ block[3]]
      chunk_mac = aes_cbc_encrypt_a32(chunk_mac, ul_key[:4])

    file_mac = [file_mac[0] ^ chunk_mac[0], file_mac[1] ^ chunk_mac[1], file_mac[2] ^ chunk_mac[2], file_mac[3] ^ chunk_mac[3]]
    file_mac = aes_cbc_encrypt_a32(file_mac, ul_key[:4])

    chunk = encryptor.encrypt(chunk)
    outfile = urllib.urlopen(ul_url + "/" + str(chunk_start), chunk)
    completion_handle = outfile.read()
    outfile.close()

  infile.close()

  meta_mac = (file_mac[0] ^ file_mac[1], file_mac[2] ^ file_mac[3])

  attributes = {'n': os.path.basename(filename)}
  enc_attributes = enc_attr(attributes, ul_key[:4])
  key = [ul_key[0] ^ ul_key[4], ul_key[1] ^ ul_key[5], ul_key[2] ^ meta_mac[0], ul_key[3] ^ meta_mac[1], ul_key[4], ul_key[5], meta_mac[0], meta_mac[1]]
  print api_req({'a': 'p', 't': root_id, 'n': [{'h': completion_handle, 't': 0, 'a': base64urlencode(enc_attributes), 'k': a32_to_base64(encrypt_key(key, master_key))}]})

def downloadfile(file, attributes, k, iv, meta_mac):
  dl_url = api_req({'a': 'g', 'g': 1, 'n': file['h']})['g']

  infile = urllib.urlopen(dl_url)
  outfile = open(attributes['n'], 'wb')
  decryptor = AES.new(a32_to_str(k), AES.MODE_CTR, counter = Counter.new(128, initial_value = ((iv[0] << 32) + iv[1]) << 64))

  file_mac = [0, 0, 0, 0]
  for chunk_start, chunk_size in sorted(get_chunks(file['s']).items()):
    chunk = infile.read(chunk_size)
    chunk = decryptor.decrypt(chunk)
    outfile.write(chunk)

    chunk_mac = [iv[0], iv[1], iv[0], iv[1]]
    for i in xrange(0, len(chunk), 16):
      block = chunk[i:i+16]
      if len(block) % 16:
        block += '\0' * (16 - (len(block) % 16))
      block = str_to_a32(block)
      chunk_mac = [chunk_mac[0] ^ block[0], chunk_mac[1] ^ block[1], chunk_mac[2] ^ block[2], chunk_mac[3] ^ block[3]]
      chunk_mac = aes_cbc_encrypt_a32(chunk_mac, k)

    file_mac = [file_mac[0] ^ chunk_mac[0], file_mac[1] ^ chunk_mac[1], file_mac[2] ^ chunk_mac[2], file_mac[3] ^ chunk_mac[3]]
    file_mac = aes_cbc_encrypt_a32(file_mac, k)

  outfile.close()
  infile.close()

  if (file_mac[0] ^ file_mac[1], file_mac[2] ^ file_mac[3]) != meta_mac:
    print "MAC mismatch"

def getfiles():
  global root_id, inbox_id, trashbin_id

  files = api_req({'a': 'f', 'c': 1})
  for file in files['f']:
    if file['t'] == 0 or file['t'] == 1:
      key = file['k'][file['k'].index(':') + 1:]
      key = decrypt_key(base64_to_a32(key), master_key)
      if file['t'] == 0:
        k = (key[0] ^ key[4], key[1] ^ key[5], key[2] ^ key[6], key[3] ^ key[7])
        iv = key[4:6] + (0, 0)
        meta_mac = key[6:8]
      else:
        k = key
      attributes = base64urldecode(file['a'])
      attributes = dec_attr(attributes, k)
      print attributes['n']

      if file['h'] == '0wFEFCTa':
        downloadfile(file, attributes, k, iv, meta_mac)
    elif file['t'] == 2:
      root_id = file['h']
    elif file['t'] == 3:
      inbox_id = file['h']
    elif file['t'] == 4:
      trashbin_id = file['h']
def getfile(file_id, file_key):
  key = base64_to_a32(file_key)
  k = (key[0] ^ key[4], key[1] ^ key[5], key[2] ^ key[6], key[3] ^ key[7])
  iv = key[4:6] + (0, 0)
  meta_mac = key[6:8]

  file = api_req({'a': 'g', 'g': 1, 'p': file_id})
  dl_url = file['g']
  size = file['s']
  attributes = base64urldecode(file['at'])
  attributes = dec_attr(attributes, k)

  print "Downloading %s (size: %d), url = %s" % (attributes['n'], size, dl_url)

  infile = urllib.urlopen(dl_url)
  outfile = open(attributes['n'], 'wb')
  decryptor = AES.new(a32_to_str(k), AES.MODE_CTR, counter = Counter.new(128, initial_value = ((iv[0] << 32) + iv[1]) << 64))

  file_mac = [0, 0, 0, 0]
  for chunk_start, chunk_size in sorted(get_chunks(file['s']).items()):
    chunk = infile.read(chunk_size)
    chunk = decryptor.decrypt(chunk)
    outfile.write(chunk)

    chunk_mac = [iv[0], iv[1], iv[0], iv[1]]
    for i in xrange(0, len(chunk), 16):
      block = chunk[i:i+16]
      if len(block) % 16:
        block += '\0' * (16 - (len(block) % 16))
      block = str_to_a32(block)
      chunk_mac = [chunk_mac[0] ^ block[0], chunk_mac[1] ^ block[1], chunk_mac[2] ^ block[2], chunk_mac[3] ^ block[3]]
      chunk_mac = aes_cbc_encrypt_a32(chunk_mac, k)

    file_mac = [file_mac[0] ^ chunk_mac[0], file_mac[1] ^ chunk_mac[1], file_mac[2] ^ chunk_mac[2], file_mac[3] ^ chunk_mac[3]]
    file_mac = aes_cbc_encrypt_a32(file_mac, k)

  outfile.close()
  infile.close()

  if (file_mac[0] ^ file_mac[1], file_mac[2] ^ file_mac[3]) != meta_mac:
    print "MAC mismatch"
  else:
    print "MAC OK"
getfile('RtQFAZZQ', 'OH8OnHm0VFw-9IzkYQa7VUdsjMp1G7hucXEk7QIZWvE')
