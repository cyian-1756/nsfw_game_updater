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
		self.downloadpath_var.set(DOWNLOAD_PATH)
		self.installationpath_var = tk.StringVar()
		self.installationpath_var.set(INSTALLATION_PATH)
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
		global DOWNLOAD_PATH
		global INSTALLATION_PATH

		INSTALLATION_PATH = self.installationpath_var.get()
		DOWNLOAD_PATH = self.downloadpath_var.get()

		self.master.update_treeview()
		self.onCancelButton()
	def onCancelButton(self):
		self.master.options_gui = None
		self.destroy()

	def loopCheck(self):
		self.after(20, self.loopCheck)
		pass
	pass
