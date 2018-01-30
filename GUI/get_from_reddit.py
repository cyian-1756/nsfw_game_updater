import tkinter as tk
import tkinter.ttk as ttk

from reddit_scraper import RedditScraper
from constants import *

class GetFromRedditGUI(tk.Toplevel):
	def __init__(self, master=None):
		super(GetFromRedditGUI, self).__init__()
		self.geometry("800x600")
		self.master = master
		self.title = "Get data from Reddit"
		self.subreddit = tk.StringVar()
		self.submission_number = tk.StringVar()

		self.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.init_layout()

	def init_layout(self):
		colwidth = 20
		sub_choice = ttk.Combobox(self, textvariable=self.subreddit, values=('lewdgames', 'NSFWGaming'), state='readonly', width=colwidth)
		sub_choice.current(0)
		sub_choice.grid(row=0, column=0)
		tk.Spinbox(self, textvariable=self.submission_number, from_=10, to=100, increment=10, width=colwidth).grid(row=1, column=0)
		self.listbox = tk.Listbox(self, width=colwidth)
		self.listbox.grid(row=2, column=0)
		self.listbox.bind('<Double-1>', self.onListboxClic)
		self.text_display = tk.Text(self)
		self.text_display.grid(row=0, column=1, rowspan=4)

		tk.Button(self, text="Update", command=self.look_for_submissions).grid(row=3, column=0)
		pass

	def onListboxClic(self, event):
		title = self.listbox.get(self.listbox.curselection())
		for sub in self.subs:
			if title == sub.title:
				to_print = \
				"""
				Title : {}
				Text : {}
				URL : {}
				""".format(sub.title, sub.selftext, sub.url)
		self.text_display.insert(tk.INSERT, to_print)

	def look_for_submissions(self):
		scraper = RedditScraper(self.subreddit.get())
		self.subs = scraper.get_releases(int(self.submission_number.get()))
		for sub in self.subs:
			self.listbox.insert(tk.END, sub.title)
	def on_closing(self):
		self.master.reddit_gui = None
		self.destroy()
