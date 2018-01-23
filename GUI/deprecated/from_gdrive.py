import requests

def download_file_from_google_drive(id, destination):
	def get_confirm_token(response):
		for key, value in response.cookies.items():
			if key.startswith('download_warning'):
				return value

		return None

	def save_response_content(response, destination):
		CHUNK_SIZE = 32768

		with open(destination, "wb") as f:
			for i, chunk in enumerate(response.iter_content(CHUNK_SIZE)):
				if chunk: # filter out keep-alive new chunks
					print(i)
					f.write(chunk)

	URL = "https://docs.google.com/uc?export=download"

	session = requests.Session()

	response = session.get(URL, params = { 'id' : id }, stream = True)
	token = get_confirm_token(response)

	if token:
		params = { 'id' : id, 'confirm' : token }
		response = session.get(URL, params = params, stream = True)

	save_response_content(response, destination)


if __name__ == "__main__":
	import sys
	import os
	# TAKE ID FROM SHAREABLE LINK
	file_id = '1FbVqdKZbUjNN3JATadDrhxV3wIy0gi3J'
	# DESTINATION FILE ON YOUR DISK
	destination = os.getcwd()+"/x.zip"
	download_file_from_google_drive(file_id, destination)
