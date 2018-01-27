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
from errors import ValidationError, RequestError
from crypto import *
import tempfile


class Mega(object):
	def __init__(self, options=None):
		self.schema = 'https'
		self.domain = 'mega.co.nz'
		self.timeout = 160  # max time (secs) to wait for resp from api requests
		self.sid = None
		self.sequence_num = random.randint(0, 0xFFFFFFFF)
		self.request_id = make_id(10)

		if options is None:
			options = {}
		self.options = options

	def login(self, email=None, password=None):
		if email:
			self._login_user(email, password)
		else:
			self.login_anonymous()
		return self

	def _login_user(self, email, password):
		password_aes = prepare_key(str_to_a32(password))
		uh = stringhash(email, password_aes)
		resp = self._api_request({'a': 'us', 'user': email, 'uh': uh})
		#if numeric error code response
		if isinstance(resp, int):
			raise RequestError(resp)
		self._login_process(resp, password_aes)

	def login_anonymous(self):
		master_key = [random.randint(0, 0xFFFFFFFF)] * 4
		password_key = [random.randint(0, 0xFFFFFFFF)] * 4
		session_self_challenge = [random.randint(0, 0xFFFFFFFF)] * 4

		user = self._api_request({
			'a': 'up',
			'k': a32_to_base64(encrypt_key(master_key, password_key)),
			'ts': base64_url_encode(a32_to_str(session_self_challenge) +
									a32_to_str(encrypt_key(session_self_challenge, master_key)))
		})

		resp = self._api_request({'a': 'us', 'user': user})
		#if numeric error code response
		if isinstance(resp, int):
			raise RequestError(resp)
		self._login_process(resp, password_key)

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

	def _process_file(self, file, shared_keys):
		"""
		Process a file
		"""
		if file['t'] == 0 or file['t'] == 1:
			keys = dict(keypart.split(':', 1) for keypart in file['k'].split('/') if ':' in keypart)
			uid = file['u']
			key = None
			# my objects
			if uid in keys:
				key = decrypt_key(base64_to_a32(keys[uid]), self.master_key)
			# shared folders
			elif 'su' in file and 'sk' in file and ':' in file['k']:
				shared_key = decrypt_key(base64_to_a32(file['sk']), self.master_key)
				key = decrypt_key(base64_to_a32(keys[file['h']]), shared_key)
				if file['su'] not in shared_keys:
					shared_keys[file['su']] = {}
				shared_keys[file['su']][file['h']] = shared_key
			# shared files
			elif file['u'] and file['u'] in shared_keys:
				for hkey in shared_keys[file['u']]:
					shared_key = shared_keys[file['u']][hkey]
					if hkey in keys:
						key = keys[hkey]
						key = decrypt_key(base64_to_a32(key), shared_key)
						break
			if key is not None:
				# file
				if file['t'] == 0:
					k = (key[0] ^ key[4], key[1] ^ key[5], key[2] ^ key[6],
						 key[3] ^ key[7])
					file['iv'] = key[4:6] + (0, 0)
					file['meta_mac'] = key[6:8]
				# folder
				else:
					k = key
				file['key'] = key
				file['k'] = k
				attributes = base64_url_decode(file['a'])
				attributes = decrypt_attr(attributes, k)
				file['a'] = attributes
			# other => wrong object
			elif file['k'] == '':
				file['a'] = False
		elif file['t'] == 2:
			self.root_id = file['h']
			file['a'] = {'n': 'Cloud Drive'}
		elif file['t'] == 3:
			self.inbox_id = file['h']
			file['a'] = {'n': 'Inbox'}
		elif file['t'] == 4:
			self.trashbin_id = file['h']
			file['a'] = {'n': 'Rubbish Bin'}
		return file

	def _init_shared_keys(self, files, shared_keys):
		"""
		Init shared key not associated with a user.
		Seems to happen when a folder is shared,
		some files are exchanged and then the
		folder is un-shared.
		Keys are stored in files['s'] and files['ok']
		"""
		ok_dict = {}
		for ok_item in files['ok']:
			shared_key = decrypt_key(base64_to_a32(ok_item['k']), self.master_key)
			ok_dict[ok_item['h']] = shared_key
		for s_item in files['s']:
			if s_item['u'] not in shared_keys:
				shared_keys[s_item['u']] = {}
			if s_item['h'] in ok_dict:
				shared_keys[s_item['u']][s_item['h']] = ok_dict[s_item['h']]

	##########################################################################
	# GET

	def find_path_descriptor(self, path):
		"""
		Find descriptor of folder inside a path. i.e.: folder1/folder2/folder3
		Params:
			path, string like folder1/folder2/folder3
		Return:
			Descriptor (str) of folder3 if exists, None otherwise
		"""
		paths = path.split('/')

		files = self.get_files()
		parent_desc = self.root_id
		found = False
		for foldername in paths:
			if foldername != '':
				for file in files.iteritems():
					if file[1]['a'] and file[1]['t'] and \
							file[1]['a']['n'] == foldername:
						if parent_desc == file[1]['p']:
							parent_desc = file[0]
							found = True
				if found:
					found = False
				else:
					return None
		return parent_desc

	def find(self, filename):
		"""
		Return file object from given filename
		"""
		files = self.get_files()
		for file in files.items():
			if file[1]['a'] and file[1]['a']['n'] == filename:
				return file

	def get_files(self):
		"""
		Get all files in account
		"""
		files = self._api_request({'a': 'f', 'c': 1})
		files_dict = {}
		shared_keys = {}
		self._init_shared_keys(files, shared_keys)
		for file in files['f']:
			processed_file = self._process_file(file, shared_keys)
			#ensure each file has a name before returning
			if processed_file['a']:
				files_dict[file['h']] = processed_file
		return files_dict

	def get_link(self, file):
		"""
		Get a file public link from given file object
		"""
		file = file[1]
		if 'h' in file and 'k' in file:
			public_handle = self._api_request({'a': 'l', 'n': file['h']})
			if public_handle == -11:
				raise RequestError("Can't get a public link from that file (is this a shared file?)")
			decrypted_key = a32_to_base64(file['key'])
			return '{0}://{1}/#!{2}!{3}'.format(self.schema,
												self.domain,
												public_handle,
												decrypted_key)
		else:
			raise ValidationError('File id and key must be present')

	def get_node_by_type(self, type):
		"""
		Get a node by it's numeric type id, e.g:
		0: file
		1: dir
		2: special: root cloud drive
		3: special: inbox
		4: special trash bin
		"""
		nodes = self.get_files()
		for node in nodes.items():
			if node[1]['t'] == type:
				return node

	def get_files_in_node(self, target):
		"""
		Get all files in a given target, e.g. 4=trash
		"""
		if type(target) == int:
			# convert special nodes (e.g. trash)
			node_id = self.get_node_by_type(target)
		else:
			node_id = [target]

		files = self._api_request({'a': 'f', 'c': 1})
		files_dict = {}
		shared_keys = {}
		self._init_shared_keys(files, shared_keys)
		for file in files['f']:
			processed_file = self._process_file(file, shared_keys)
			if processed_file['a'] and processed_file['p'] == node_id[0]:
				files_dict[file['h']] = processed_file
		return files_dict

	def get_id_from_public_handle(self, public_handle):
		#get node data
		node_data = self._api_request({'a': 'f', 'f': 1, 'p': public_handle})
		node_id = self.get_id_from_obj(node_data)
		return node_id

	def get_id_from_obj(self, node_data):
		"""
		Get node id from a file object
		"""
		node_id = None

		for i in node_data['f']:
			if i['h'] is not u'':
				node_id = i['h']
		return node_id

	##########################################################################
	# DOWNLOAD
	def download(self, file, dest_path=None, dest_filename=None):
		"""
		Download a file by it's file object
		"""
		self._download_file(None, None, file=file[1], dest_path=dest_path, dest_filename=dest_filename, is_public=False)

	def download_url(self, url, dest_path=None, dest_filename=None):
		"""
		Download a file by it's public url
		"""
		path = self._parse_url(url).split('!')
		file_id = path[0]
		file_key = path[1]
		self._download_file(file_id, file_key, dest_path, dest_filename, is_public=True)

	def _download_file(self, file_handle, file_key, dest_path=None, dest_filename=None, is_public=False, file=None):
		file_key = base64_to_a32(file_key)
		file_data = self._api_request({'a': 'g', 'g': 1, 'p': file_handle})
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
		file_name = "mega.zip"
		attribs = base64_url_decode(file_data['at'])
		attribs = decrypt_attr(attribs, k)

		if dest_filename is not None:
			file_name = dest_filename
		else:
			file_name = attribs['n']

		input_file = requests.get(file_url, stream=True).raw

		if dest_path is None:
			dest_path = ''
		else:
			dest_path += '/'

		temp_output_file = tempfile.NamedTemporaryFile(mode='w+b', prefix='megapy_', delete=False)

		k_str = a32_to_str(k)
		counter = Counter.new(
			128, initial_value=((iv[0] << 32) + iv[1]) << 64)
		aes = AES.new(k_str, AES.MODE_CTR, counter=counter)

		mac_str = '\0' * 16
		mac_encryptor = AES.new(k_str, AES.MODE_CBC, mac_str)
		iv_str = a32_to_str([iv[0], iv[1], iv[0], iv[1]])

		for chunk_start, chunk_size in get_chunks(file_size):
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
			print('{0} of {1} downloaded'.format(file_info.st_size, file_size))

		file_mac = str_to_a32(mac_str)

		temp_output_file.close()

		# check mac integrity
		if (file_mac[0] ^ file_mac[1], file_mac[2] ^ file_mac[3]) != meta_mac:
			raise ValueError('Mismatched mac')

		shutil.move(temp_output_file.name, dest_path + file_name)

	def get_public_url_info(self, url):
		"""
		Get size and name from a public url, dict returned
		"""
		file_handle, file_key = self._parse_url(url).split('!')
		return self.get_public_file_info(file_handle, file_key)

	def import_public_url(self, url, dest_node=None, dest_name=None):
		"""
		Import the public url into user account
		"""
		file_handle, file_key = self._parse_url(url).split('!')
		return self.import_public_file(file_handle, file_key, dest_node=dest_node, dest_name=dest_name)

	def get_public_file_info(self, file_handle, file_key):
		"""
		Get size and name of a public file
		"""
		data = self._api_request({
			'a': 'g',
			'p': file_handle,
			'ssm': 1})

		#if numeric error code response
		if isinstance(data, int):
			raise RequestError(data)

		if 'at' not in data or 's' not in data:
			raise ValueError("Unexpected result", data)

		key = base64_to_a32(file_key)
		k = (key[0] ^ key[4], key[1] ^ key[5], key[2] ^ key[6], key[3] ^ key[7])

		size = data['s']
		unencrypted_attrs = decrypt_attr(base64_url_decode(data['at']), k)
		if not unencrypted_attrs:
			return None

		result = {
			'size': size,
			'name': unencrypted_attrs['n']}

		return result

	def import_public_file(self, file_handle, file_key, dest_node=None, dest_name=None):
		"""
		Import the public file into user account
		"""

		# Providing dest_node spare an API call to retrieve it.
		if dest_node is None:
			# Get '/Cloud Drive' folder no dest node specified
			dest_node = self.get_node_by_type(2)[1]

		# Providing dest_name spares an API call to retrieve it.
		if dest_name is None:
			pl_info = self.get_public_file_info(file_handle, file_key)
			dest_name = pl_info['name']

		key = base64_to_a32(file_key)
		k = (key[0] ^ key[4], key[1] ^ key[5], key[2] ^ key[6], key[3] ^ key[7])

		encrypted_key = a32_to_base64(encrypt_key(key, self.master_key))
		encrypted_name = base64_url_encode(encrypt_attr({'n': dest_name}, k))

		data = self._api_request({
			'a': 'p',
			't': dest_node['h'],
			'n': [{
				'ph': file_handle,
				't': 0,
				'a': encrypted_name,
				'k': encrypted_key}]})

		#return API msg
		return data

m = Mega()
m.download_url("https://mega.nz/#!JhNjiJBY!sqGixSadreGl7NIsl2DWfrzMl9RY_uOYGPnmV-dzBSg", dest_path="D:\\")
