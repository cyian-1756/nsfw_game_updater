import tkinter as tk
import tkinter.ttk as ttk

from reddit_scraper import RedditScraper
from constants import *
from functions import *

class GetFromRedditGUI(tk.Toplevel):
	def __init__(self, master=None):
		super(GetFromRedditGUI, self).__init__()
		self.master = master
		self.title = "Get data from Reddit"
		self.subreddit = tk.StringVar()
		self.submission_number = tk.StringVar()
		self.init_layout()

	def init_layout(self):
		colwidth = 20
		sub_choice = ttk.Combobox(self, textvariable=self.subreddit, values=('lewdgames', 'NSFWGaming'), state='readonly', width=colwidth)
		sub_choice.current(0)
		sub_choice.grid(row=0, column=0)
		tk.Spinbox(self, textvariable=self.submission_number, from_=10, to=100, increment=10, width=colwidth).grid(row=1, column=0)
		self.listbox = tk.Listbox(self, width=colwidth)

		tk.Button(self, text="Update", command=self.look_for_submissions)
		pass

	def look_for_submissions(self):
		scraper = RedditScraper(self.subreddit.get())
		subs = scraper.get_releases(int(self.submission_number.get()))
		for sub in subs:
			self.listbox.insert(tk.END, sub.title)
