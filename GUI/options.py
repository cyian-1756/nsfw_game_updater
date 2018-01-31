#-*- encoding:utf8 -*-
#!/usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askdirectory
from constants import *

class OptionGUI(tk.Toplevel):
	def __init__(self, master = None):
		super(OptionGUI, self).__init__()
		self.master = master
		self.title = "Options"
		self.downloadpath_var = tk.StringVar()
		self.downloadpath_var.set(master.download_path)
		self.installationpath_var = tk.StringVar()
		self.installationpath_var.set(master.installation_path)
		self.chunksize_var = tk.StringVar()
		self.chunksize_var.set(str(master.chunksize))
		self.use_pending_var = tk.IntVar()
		self.use_pending_var.set(int(master.use_pending_db))
		self.config()
		pass

	def config(self):
		folderimg = tk.BitmapImage(data=FOLDER_ICON.split('-')[0], maskdata=FOLDER_ICON.split('-')[1], background="white")

		self.downloadpath_entry = tk.Entry(self, textvariable=self.downloadpath_var)
		self.downloadpath_entry.grid(column=1, row=1)
		self.downloadpath_button = tk.Button(self, command=self.onFilepathButton, image=folderimg, width=16, height=16)
		self.downloadpath_button.image = folderimg
		self.downloadpath_button.grid(row=1, column=2)
		tk.Label(self, text="Download Path :").grid(row=1, column=0)

		self.installationpath_entry = tk.Entry(self, textvariable=self.installationpath_var)
		self.installationpath_entry.grid(row=2, column=1)
		self.installationpath_button = tk.Button(self, command=self.onInstallpathButton, image=folderimg, width=16, height=16)
		self.installationpath_button.image = folderimg
		self.installationpath_button.grid(row=2, column=2)
		tk.Label(self, text="Installation Path :").grid(row=2, column=0)

		tk.Spinbox(self, textvariable=self.chunksize_var, from_=256, to=4096, increment=256).grid(row=3, column=1)
		tk.Label(self, text="RAM used to download :").grid(row=3, column=0)
		tk.Label(self, text="MB").grid(row=3, column=2)

		tk.Checkbutton(self, variable=self.use_pending_var).grid(row=4, column=1)
		tk.Label(self, text="Use Pending Database :").grid(row=4, column=0)

		self.ok_button = tk.Button(self, text="Save", command=self.onOkButton)
		self.cancel_button = tk.Button(self, text="Cancel", command=self.onCancelButton)
		self.ok_button.grid(column=0, row=6)
		self.cancel_button.grid(column=1, row=6)
		self.loopCheck()
		pass

	def onFilepathButton(self):
		directory = askdirectory()
		self.downloadpath_var.set(directory)
		pass

	def onInstallpathButton(self):
		directory = askdirectory()
		self.installationpath_var.set(directory)
		pass

	def onOkButton(self):
		self.master.installation_path = self.installationpath_var.get()
		self.master.download_path = self.downloadpath_var.get()
		self.master.chunksize = int(self.chunksize_var.get())*1000000
		self.master.use_pending_db = self.use_pending_var.get()==1

		self.master.update_treeview()
		self.onCancelButton()
	def onCancelButton(self):
		self.master.options_gui = None
		self.destroy()

	def loopCheck(self):
		self.after(20, self.loopCheck)
		pass
	pass
