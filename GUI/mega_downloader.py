import re
import json
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Util import Counter
import os
import random
import binascii
import requests
import shutil
import tempfile
import base64
import struct
from threading import Thread, Lock, Condition, Event
import platform

from constants import *
from utils import *
from exceptions import *


def aes_cbc_encrypt(data, key):
	aes_cipher = AES.new(key, AES.MODE_CBC, '\0' * 16)
	return aes_cipher.encrypt(data)


def aes_cbc_decrypt(data, key):
	aes_cipher = AES.new(key, AES.MODE_CBC, '\0' * 16)
	return aes_cipher.decrypt(data)


def aes_cbc_encrypt_a32(data, key):
	return str_to_a32(aes_cbc_encrypt(a32_to_str(data), a32_to_str(key)))


def aes_cbc_decrypt_a32(data, key):
	return str_to_a32(aes_cbc_decrypt(a32_to_str(data), a32_to_str(key)))


def stringhash(str, aeskey):
	s32 = str_to_a32(str)
	h32 = [0, 0, 0, 0]
	for i in range(len(s32)):
		h32[i % 4] ^= s32[i]
	for r in range(0x4000):
		h32 = aes_cbc_encrypt_a32(h32, aeskey)
	return a32_to_base64((h32[0], h32[2]))


def prepare_key(arr):
	pkey = [0x93C467E3, 0x7DB0C7A4, 0xD1BE3F81, 0x0152CB56]
	for r in range(0x10000):
		for j in range(0, len(arr), 4):
			key = [0, 0, 0, 0]
			for i in range(4):
				if i + j < len(arr):
					key[i] = arr[i + j]
			pkey = aes_cbc_encrypt_a32(pkey, key)
	return pkey


def encrypt_key(a, key):
	return sum(
		(aes_cbc_encrypt_a32(a[i:i + 4], key)
			for i in range(0, len(a), 4)), ())


def decrypt_key(a, key):
	return sum(
		(aes_cbc_decrypt_a32(a[i:i + 4], key)
			for i in range(0, len(a), 4)), ())


def encrypt_attr(attr, key):
	attr = 'MEGA' + json.dumps(attr)
	if len(attr) % 16:
		attr += '\0' * (16 - len(attr) % 16)
	return aes_cbc_encrypt(attr, a32_to_str(key))


def decrypt_attr(attr, key):
	k = a32_to_str(key)
	attr = aes_cbc_decrypt(attr, k)
	attr = attr.split(b'\0', 1)[0]
	attr = attr.decode()
	return json.loads(attr[4:]) if attr[:6] == 'MEGA{"' else False


def a32_to_str(a):
	return struct.pack('>%dI' % len(a), *a)


def str_to_a32(b):
	if len(b) % 4:
		# pad to multiple of 4
		b += '\0' * (4 - len(b) % 4)
	return struct.unpack('>%dI' % (len(b) / 4), b)


def mpi_to_int(s):
	return int(binascii.hexlify(s[2:]), 16)


def base64_url_decode(data):
	data += '=='[(2 - len(data) * 3) % 4:]
	for search, replace in (('-', '+'), ('_', '/'), (',', '')):
		data = data.replace(search, replace)
	return base64.b64decode(data)


def base64_to_a32(s):
	return str_to_a32(base64_url_decode(s))


def base64_url_encode(data):
	data = base64.b64encode(data)
	for search, replace in (('+', '-'), ('/', '_'), ('=', '')):
		data = data.replace(search, replace)
	return data


def a32_to_base64(a):
	return base64_url_encode(a32_to_str(a))


def get_chunks(size):
	p = 0
	s = 0x20000
	while p+s < size:
		yield(p, s)
		p += s
		if s < 0x100000:
			s += 0x20000
	yield(p, size-p)


# more general functions
def make_id(length):
	text = ''
	possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
	for i in range(length):
		text += random.choice(possible)
	return text


class MegaDownloader(Thread):
	def __init__(self, url, dest_path, callback):
		Thread.__init__(self)

		self.callback = callback
		self.progress = 0
		self.path = dest_path
		if not self.path.endswith("/") and not self.path.endswith("\\"):
			if platform.system().lower()=="windows":
				self.path += "\\"
			else:
				self.path+="/"
		self.url = url

		self.schema = 'https'
		self.domain = 'mega.co.nz'
		self.timeout = 160  # max time (secs) to wait for resp from api requests
		self.sid = None
		self.sequence_num = random.randint(0, 0xFFFFFFFF)
		self.request_id = make_id(10)

		self.paused = False
		self.pause_cond = Condition(Lock())
		self.stop_event = Event()
		pass

	def _api_request(self, data):
		params = {'id': self.sequence_num}
		self.sequence_num += 1

		if self.sid:
			params.update({'sid': self.sid})

		#ensure input data is a list
		if not isinstance(data, list):
			data = [data]

		req = requests.post(
			'{0}://g.api.{1}/cs'.format(self.schema, self.domain),
			params=params,
			data=json.dumps(data),
			timeout=self.timeout)
		json_resp = json.loads(req.text)

		#if numeric error code response
		if isinstance(json_resp, int):
			raise RequestError(json_resp)
		return json_resp[0]

	def _parse_url(self, url):
		#parse file id and key from url
		if '!' in url:
			match = re.findall(r'/#!(.*)', url)
			path = match[0]
			return path
		else:
			raise RequestError('Url key missing')

	def run(self):
		while not self.stop_event.isSet( ):
			path = self._parse_url(self.url).split('!')
			file_id = path[0]
			file_key = path[1]
			file_key = base64_to_a32(file_key)
			file_data = self._api_request({'a': 'g', 'g': 1, 'p': file_id})
			k = (file_key[0] ^ file_key[4], file_key[1] ^ file_key[5],
				 file_key[2] ^ file_key[6], file_key[3] ^ file_key[7])
			iv = file_key[4:6] + (0, 0)
			meta_mac = file_key[6:8]

			# Seems to happens sometime... When  this occurs, files are
			# inaccessible also in the official also in the official web app.
			# Strangely, files can come back later.
			if 'g' not in file_data:
				raise RequestError('File not accessible anymore')
			file_url = file_data['g']
			file_size = file_data['s']
			attribs = base64_url_decode(file_data['at'])
			attribs = decrypt_attr(attribs, k)
			file_name = attribs['n']

			input_file = requests.get(file_url, stream=True).raw

			dest_path = self.path

			temp_output_file = tempfile.NamedTemporaryFile(mode='w+b', prefix='megapy_', delete=False)

			k_str = a32_to_str(k)
			counter = Counter.new(
				128, initial_value=((iv[0] << 32) + iv[1]) << 64)
			aes = AES.new(k_str, AES.MODE_CTR, counter=counter)

			mac_str = '\0' * 16
			mac_encryptor = AES.new(k_str, AES.MODE_CBC, mac_str)
			iv_str = a32_to_str([iv[0], iv[1], iv[0], iv[1]])

			for chunk_start, chunk_size in get_chunks(file_size):
				with lock:
					with self.pause_cond:
						while self.paused:
							self.pause_cond.wait()
						chunk = input_file.read(chunk_size)
						chunk = aes.decrypt(chunk)
						temp_output_file.write(chunk)

						encryptor = AES.new(k_str, AES.MODE_CBC, iv_str)
						for i in range(0, len(chunk)-16, 16):
							block = chunk[i:i + 16]
							encryptor.encrypt(block)

						#fix for files under 16 bytes failing
						if file_size > 16:
							i += 16
						else:
							i = 0

						block = chunk[i:i + 16]
						if len(block) % 16:
							block += b'\0' * (16 - (len(block) % 16))
						mac_str = mac_encryptor.encrypt(encryptor.encrypt(block))

						file_info = os.stat(temp_output_file.name)
						self.progress = int(int(file_info.st_size)/int(file_size)*100)

			file_mac = str_to_a32(mac_str)

			temp_output_file.close()

			# check mac integrity
			if (file_mac[0] ^ file_mac[1], file_mac[2] ^ file_mac[3]) != meta_mac:
				raise ValueError('Mismatched mac')

			shutil.move(temp_output_file.name, dest_path + file_name)
			self.callback(file_name, self.path)

	def pause(self):
		self.paused = True
		# If in sleep, we acquire immediately, otherwise we wait for thread
		# to release condition. In race, worker will still see self.paused
		# and begin waiting until it's set back to False
		self.pause_cond.acquire()

	#should just resume the thread
	def resume(self):
		self.paused = False
		# Notify so thread will wake after lock released
		self.pause_cond.notify()
		# Now release the lock
		self.pause_cond.release()

	def stop(self):
		self.stop_event.set()
		self.progress = 0
		#os.remove(self.path+self.name)
		self.daemon = False
