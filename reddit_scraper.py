import praw

class RedditScraper():
	def __init__(self, subreddit):
		self.subreddit = subreddit
		self.reddit = praw.Reddit(client_id='1E0_pu_23NGHtQ', user_agent='NSFW Game Manager', client_secret=None)

	def get_releases(self, limit=10):
		releases = []
		for submission in reddit.subreddit(self.subreddit).hot(limit=limit):
			if "release" in [s.lower() for s in submission.flair.choices()]:
				releases.append(submission)
		return releases

	def from_submission_to_json(self, submission):
		"""
		variables to look for, and template for formatting
		----------
		json_to_add = {\
		"game": self.game.get(), \
		"public_build": self.public_build.get(),\
		"setting":self.setting.get(),\
		"developer": self.developer.get(),\
		"engine": self.engine.get(),\
		"visual_style":self.visual_style.get(),\
		"genre":self.genre.get(),\
		"animation":self.animation.get(),\
		"latest_version":self.latest_version.get(),\
		"download_link_windows": check_url(self.dl_windows.get()),\
		"download_link_mac": check_url(self.dl_mac.get()),\
		"download_link_linux": check_url(self.dl_linux.get()),\
		"download_link_android": check_url(self.dl_android.get()),\
		"graphtreon": self.graphtreon.get()}
		"""
		pass
