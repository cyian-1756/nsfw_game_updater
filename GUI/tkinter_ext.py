import tkinter as tk
import tkinter.ttk as ttk

class EntryWithPlaceholder(tk.Entry):
	def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', **kwargs):
		super().__init__(master, **kwargs)

		self.placeholder = placeholder
		self.placeholder_color = color
		self.default_fg_color = self['fg']

		self.bind("<FocusIn>", self.foc_in)
		self.bind("<FocusOut>", self.foc_out)

		self.put_placeholder()

	def put_placeholder(self):
		self.insert(0, self.placeholder)
		self['fg'] = self.placeholder_color

	def foc_in(self, *args):
		if self['fg'] == self.placeholder_color:
			self.delete('0', 'end')
			self['fg'] = self.default_fg_color

	def foc_out(self, *args):
		if not self.get():
			self.put_placeholder()

try:
	from Tkinter import PhotoImage, Frame, Label, Widget
	from Tkconstants import *
except ImportError:
	from tkinter import PhotoImage, Frame, Label, Widget
	from tkinter.constants import *

class CollapsibleFrame(Frame):
	def __init__(self, master, text=None, borderwidth=2, width=0, height=16, interior_padx=0, interior_pady=8, background=None, caption_separation=4, caption_font=None, caption_builder=None, icon_x=5):
		Frame.__init__(self, master)
		if background is None:
			background = self.cget("background")

		self.configure(background=background)

		self._is_opened = False

		self._interior_padx = interior_padx
		self._interior_pady = interior_pady

		self._iconOpen = PhotoImage(data="R0lGODlhEAAQAKIAAP///9TQyICAgEBAQAAAAAAAAAAAAAAAACwAAAAAEAAQAAADNhi63BMgyinFAy0HC3Xj2EJoIEOM32WeaSeeqFK+say+2azUi+5ttx/QJeQIjshkcsBsOp/MBAA7")
		self._iconClose = PhotoImage(data="R0lGODlhEAAQAKIAAP///9TQyICAgEBAQAAAAAAAAAAAAAAAACwAAAAAEAAQAAADMxi63BMgyinFAy0HC3XjmLeA4ngpRKoSZoeuDLmo38mwtVvKu93rIo5gSCwWB8ikcolMAAA7")

		height_of_icon = max(self._iconOpen.height(), self._iconClose.height())
		width_of_icon = max(self._iconOpen.width(), self._iconClose.width())

		containerFrame_pady = (height_of_icon//2) +1

		self._height = height
		self._width = width

		self._containerFrame = Frame(self, borderwidth=borderwidth, width=width, height=height, relief=RIDGE, background=background)
		self._containerFrame.pack(expand=True, fill=X, pady=(containerFrame_pady,0))

		self.interior = Frame(self._containerFrame, background=background)

		self._collapseButton = Label(self, borderwidth=0, image=self._iconOpen, relief=RAISED)
		self._collapseButton.place(in_= self._containerFrame, x=icon_x, y=-(height_of_icon//2), anchor=N+W, bordermode="ignore")
		self._collapseButton.bind("<Button-1>", lambda event: self.toggle())

		if caption_builder is None:
			self._captionLabel = Label(self, anchor=W, borderwidth=1, text=text)
			if caption_font is not None:
				self._captionLabel.configure(font=caption_font)
		else:
			self._captionLabel = caption_builder(self)

			if not isinstance(self._captionLabel, Widget):
				raise Exception("'caption_builder' doesn't return a tkinter widget")

		self.after(0, lambda: self._place_caption(caption_separation, icon_x, width_of_icon))

	def update_width(self, width=None):
		# Update could be devil
		# http://wiki.tcl.tk/1255
		self.after(0, lambda width=width:self._update_width(width))

	def _place_caption(self, caption_separation, icon_x, width_of_icon):
		self.update()
		x = caption_separation + icon_x + width_of_icon
		y = -(self._captionLabel.winfo_reqheight()//2)

		self._captionLabel.place(in_= self._containerFrame, x=x, y=y, anchor=N+W, bordermode="ignore")

	def _update_width(self, width):
		self.update()
		if width is None:
			width=self.interior.winfo_reqwidth()

		if isinstance(self._interior_pady, (list, tuple)):
			width += self._interior_pady[0] + self._interior_pady[1]
		else:
			width += 2*self._interior_pady

		width = max(self._width, width)

		self._containerFrame.configure(width=width)

	def open(self):
		self._collapseButton.configure(image=self._iconClose)

		self._containerFrame.configure(height=self.interior.winfo_reqheight())
		self.interior.pack(expand=True, fill=X, padx=self._interior_padx, pady =self._interior_pady)

		self._is_opened = True

	def close(self):
		self.interior.pack_forget()
		self._containerFrame.configure(height=self._height)
		self._collapseButton.configure(image=self._iconOpen)

		self._is_opened = False

	def toggle(self):
		if self._is_opened:
			self.close()
		else:
			self.open()

if __name__ == "__main__":
	try:
		from Tkinter import Tk, Button
	except ImportError:
		from tkinter import Tk, Button

	root = Tk()
	root.wm_geometry("400x300+0+0")

	cf1 = CollapsibleFrame(root, text ="Frame1", interior_padx=6)
	cf1.pack()

	for i in range(3):
		Button(cf1.interior, text="button %s"%i).grid(row=i, column=0)

	cf1.update_width()
	root.mainloop()

class Tooltip(tk.Toplevel):
	"""Tooltip to display when the mouse stays long enough on an item."""
	def __init__(self, parent, **kwargs):
		"""
		Create Tooltip.
		Options:
			* parent: parent window
			* background: background color
			* foreground: foreground color
			* image: PhotoImage/BitmapImage to display in the tooltip
			* text: text (str) to display in the tooltip
			* compound: relative orientation of the graphic relative to the text
			* alpha: opacity of the tooltip (0 for transparent, 1 for opaque),
					 the text is affected too, so 0 would mean an invisible tooltip
		"""
		tk.Toplevel.__init__(self, parent)
		self.transient(parent)
		self.attributes('-type', 'tooltip')
		self.attributes('-alpha', kwargs.get('alpha', 0.8))
		self.overrideredirect(True)
		self.configure(padx=kwargs.get('padx', 4))
		self.configure(pady=kwargs.get('pady', 4))

		self.style = ttk.Style(self)
		if 'background' in kwargs:
			bg = kwargs['background']
			self.configure(background=bg)
			self.style.configure('tooltip.TLabel', background=bg)
		if 'foreground' in kwargs:
			self.style.configure('tooltip.TLabel', foreground=kwargs['foreground'])

		self.im = kwargs.get('image', None)
		self.label = ttk.Label(self, text=kwargs.get('text', ''), image=self.im,
							   style='tooltip.TLabel',
							   compound=kwargs.get('compound', 'left'))
		self.label.pack()

	def configure(self, **kwargs):
		if 'text' in kwargs:
			self.label.configure(text=kwargs.pop('text'))
		if 'image' in kwargs:
			self.label.configure(image=kwargs.pop('image'))
		if 'background' in kwargs:
			self.style.configure('tooltip.TLabel', background=kwargs['background'])
		if 'foreground' in kwargs:
			fg = kwargs.pop('foreground')
			self.style.configure('tooltip.TLabel', foreground=fg)
		if 'alpha' in kwargs:
			self.attributes('-alpha', kwargs.pop('alpha'))
		tk.Toplevel.configure(self, **kwargs)


class TooltipTreeWrapper:
	"""Tooltip wrapper for a Treeview."""
	def __init__(self, tree, delay=1500, **kwargs):
		"""
		Create a Tooltip wrapper for the Treeview tree.
		This wrapper enables the creation of tooltips for tree's items with all
		the bindings to make them appear/disappear.
		Options:
			* tree: wrapped Treeview
			* delay: hover delay before displaying the tooltip (ms)
			* all keyword arguments of a Tooltip
		"""
		self.tree = tree
		self.delay = delay
		self._timer_id = ''
		self.tooltip_text = {}
		self.tooltip = Tooltip(tree, **kwargs)
		self.tooltip.withdraw()
		self.current_item = None

		self.tree.bind('<Motion>', self._on_motion)
		self.tree.bind('<Leave>', lambda e: self.tree.after_cancel(self._timer_id))

	def add_tooltip(self, item, text):
		"""Add a tooltip with given text to the item."""
		self.tooltip_text[item] = text

	def _on_motion(self, event):
		"""Withdraw tooltip on mouse motion and cancel its appearance."""
		if self.tooltip.winfo_ismapped():
			x, y = self.tree.winfo_pointerxy()
			if self.tree.winfo_containing(x, y) != self.tooltip:
				if self.tree.identify_row(y - self.tree.winfo_rooty()):
					self.tooltip.withdraw()
					self.current_item = None
		else:
			self.tree.after_cancel(self._timer_id)
			self._timer_id = self.tree.after(self.delay, self.display_tooltip)

	def display_tooltip(self):
		"""Display the tooltip corresponding to the hovered item."""
		item = self.tree.identify_row(self.tree.winfo_pointery() - self.tree.winfo_rooty())
		text = self.tooltip_text.get(item, '')
		self.current_item = item
		if text:
			self.tooltip.configure(text=text)
			self.tooltip.deiconify()
			x = self.tree.winfo_pointerx() + 14
			y = self.tree.winfo_rooty() + self.tree.bbox(item)[1] + self.tree.bbox(item)[3]
			self.tooltip.geometry('+%i+%i' % (x, y))
