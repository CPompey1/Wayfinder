import asyncio
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import Canvas
import ttkbootstrap as ttkint
from PIL import ImageTk, Image, ImageOps
import json

from BeaconManager import BeaconManager
from MPU.run_mpu import MpuClass
from tra_localization import localization

FONT = "Calibri 26 bold"
FONT_SERVICES = "Calibri 15"

def flatten(list_of_list):
    if isinstance(list_of_list, list):
        fin_list = []
        for el in list_of_list:
            fin_list.extend(flatten(el))
        return fin_list
    else:
        return [list_of_list]
	
class tkinterApp(tk.Tk):
	def __init__(self, *args, **kwargs): 
		tk.Tk.__init__(self, *args, **kwargs)
		#init classes
		self.beaconManager = BeaconManager()
		self.mpu = MpuClass()
		self.started = False

		#self.geometry("%dx%d" % (self.winfo_screenwidth(), self.winfo_screenheight()))
		self.geometry("768x1024")
		# Container
		container = tk.Frame(self) 
		self.title("Wayfinder")
		container.pack(side = "top", fill = "both", expand = True) 
		container.grid_rowconfigure(0, weight = 1)
		container.grid_columnconfigure(0, weight = 1)
		container.grid_rowconfigure(1, weight = 1)
		container.grid_columnconfigure(1, weight = 1)
		container.grid_rowconfigure(2, weight = 1)
		container.grid_columnconfigure(2, weight = 1)
		container.grid_rowconfigure(3, weight = 1)
		container.grid_columnconfigure(3, weight = 1)


		# initializing frames to an empty array
		self.frames = {} 
		self.json_file_dict: dict = json.load(open("services.json"))
		self.nodes: dict = json.load(open("node.json"))
		self.service_array = list(self.json_file_dict["service_group"][0].keys())
		self.dest_list = list(self.nodes["destinations"])
        #print(self.dest_list)
		all_services = []
		for i in range(len(self.service_array)):
			floor_array = self.json_file_dict["service_group"][0][self.service_array[i]][0]
			all_services.append(flatten(list(floor_array.values())))
		all_services = flatten(all_services)
        # Filter not None
		self.all_valid_serv = list(filter(None,all_services))
        # Order alphabetically
		self.all_valid_serv = sorted(self.all_valid_serv)
        # Default stairs selection
		self.stairs = BooleanVar(value=True)
		self.selected = False
		self.sel_service = "All services"
		self.sel_room = "Second Floor Elevator"
		# iterating through a tuple consisting
		# of the different page layouts
		for F in (StartPage, ServicesSearch, NavigationPage, DeveloperMode):

			frame = F(container, self)

			# initializing frame of that object from
			# startpage, page1, page2 respectively with 
			# for loop
			self.frames[F] = frame 

			frame.grid(row = 0, column = 0, columnspan=4, sticky ="nsew")

		self.show_frame(StartPage)
		


	# to display the current frame passed as
	# parameter
	def show_frame(self, cont):
		frame = self.frames[cont]
		frame.tkraise()

	async def enable_navigation(self, cont):
		frame = self.frames[cont]
		frame.tkraise()
		# if not self.started:
			
		# 	self.started = True
		# 	self.localization_thread = asyncio.create_task(localization())
		# 	self.initialize_task = asyncio.create_task(self.beaconManager.initialize_scanning())
		# 	self.create_task = (self.mpu.run_mpu())

		# 	await self.localization_thread
		# 	await self.initialize_task
		# 	await self.create_task


# first window frame startpage

class StartPage(tk.Frame):
	def __init__(self, parent, controller): 
		self.controller = controller
		
		tk.Frame.__init__(self, parent)
		title_label = Label(self, text= "Welcome to Lockwood Wayfinder!", font=FONT)
		title_label.pack(pady=10)
		img = ImageTk.PhotoImage(Image.open("lockwood_main.jpg"))
		panel = Label(self, image=img)
		panel.image = img
		panel.pack(pady=10)
		start_frame = Frame(self, bg="white")
		start_button = ttk.Button(master=start_frame, text= "Start Navigating", command = lambda : controller.enable_navigation(ServicesSearch))
		start_button.pack(pady=10)
		dev_mode_button = ttk.Button(master=start_frame, text= "Developer Mode", command = lambda : controller.show_frame(DeveloperMode))
		dev_mode_button.pack(pady=10)
		start_frame.pack()

class ServicesSearch(tk.Frame):
	
	def __init__(self, parent, controller: tkinterApp):
		self.controller = controller
		tk.Frame.__init__(self, parent)
		self.services_lb = tk.Listbox(self, height = len(controller.service_array)+1, width = 10, font=FONT, name='service_list')
		# Include an "all services" category with all reachable services
		self.services_lb.insert(tk.END, "All services")
		for item in controller.service_array:
			self.services_lb.insert(tk.END, item)
		self.services_lb.grid(column=0, row=0, sticky='nw', padx=0, pady=2)
		self.services_lb.bind('<<ListboxSelect>>', self.onselect)
		self.services_lb.select_set(0)
		self.room_lb = Listbox(self, font=FONT_SERVICES, width = 60, name='room_list', selectmode="SINGLE")
		for room in controller.all_valid_serv:
			self.room_lb.insert(tk.END, room)
		self.room_lb.grid(column=1, columnspan=4, row=0, sticky='nwse', padx=0, pady=2)
		self.room_lb.bind('<Double-1>', self.service_confirmation)
		self.selected = False
		back_butt = ttk.Button(self, text= "Back", command = lambda : controller.show_frame(StartPage))
		back_butt.grid(column=0, row=2,sticky="nw", padx=10, pady = 6)
		frame = tk.Frame(self)
		frame.grid(row = 2, column = 1, sticky="nwes",  padx=10, pady = 6)
		s_or_el = ttk.Label(frame, text ="Stairs/Elevator Preference: ", font = FONT_SERVICES).pack()
		R1 = Radiobutton(frame, text="Stairs", variable=self.controller.stairs, value=True).pack()
		R2 = Radiobutton(frame, text="Elevator", variable=self.controller.stairs, value=False).pack()
		self.controller.sel_service = "All services"	
		self.controller.sel_room = "Second Floor Elevator" 

	def onselect(self, evt: Event):
		if not evt.widget.curselection():
			return
		# Note here that Tkinter passes an event object to onselect()
		w = evt.widget.curselection()[0] - 1 # Number from 0 to n number of services categories to exclude "ALL" category
		self.controller.sel_service = str(self.services_lb.get(self.services_lb.curselection()))
		floor_array = {}
		print(self.controller.sel_service)
		# Side menu depending on selected service
		floor_array = self.controller.json_file_dict["service_group"][0][self.controller.service_array[w]][0]
		list_services = flatten(list(floor_array.values()))
		# Listbox for rooms
		self.room_lb = Listbox(self, font=FONT_SERVICES, name='room_list', selectmode="SINGLE")
		if w == -1:
			for room in self.controller.all_valid_serv:
				self.room_lb.insert(tk.END, room)
		else:
			floor_array = self.controller.json_file_dict["service_group"][0][self.controller.service_array[w]][0]
			list_services = flatten(list(floor_array.values()))
			for room in list_services:
				self.room_lb.insert(tk.END, room)
		self.room_lb.grid(column=1, columnspan=4, row=0, sticky='nwse', padx=0, pady=2)
		self.room_lb.bind('<Double-1>', self.service_confirmation)
		self.grid_columnconfigure(1, weight=5)
		#page1.state('zoomed')
		self.bind("<Escape>", lambda e: self.quit())
		# Listbox for services

	def service_confirmation(self, args: Event):
		if not args.widget.curselection():
			return
		if not self.controller.selected:
			self.controller.selected = True
			idx = args.widget.curselection()[0]
			if self.controller.sel_service != "All services":
				floor_services_flat= flatten(list(self.controller.json_file_dict["service_group"][0][self.controller.sel_service][0].values()))
			    # Getting rid of None values from json fileù
				serv_not_none = list(filter(None,floor_services_flat))
				self.controller.sel_room  = serv_not_none[idx]
			else:
			    # If selected from the "All services" list
				self.controller.sel_room = self.controller.all_valid_serv[idx]
			print(self.controller.sel_service)
			mess= "Selected service: \""
			mess = mess + str(self.controller.sel_room)
			mess = mess + "\". \nWould you like to proceed?"
			selection = messagebox.askyesno(title="Service confirmation", message=mess, parent=self)
			if selection:
				#self.start_navigation(sel_service)
				self.controller.show_frame(NavigationPage)
			else:
				self.controller.selected = False



# third window frame page2
class NavigationPage(tk.Frame): 
	def __init__(self, parent, controller):
		self.controller = controller
		tk.Frame.__init__(self, parent)
		mess = "Goal: "+ self.controller.sel_room
		nav_label = Label(self, text= "Wayfinder Navigation", font=FONT).pack()
		service_label = Label(self, text= mess, font=FONT_SERVICES).pack()
	

		# button to show frame 2 with text
		# layout2
		button1 = ttk.Button(self, text ="Page 1",
							command = self.reset_service)
	
		# putting the button in its place by 
		# using grid
		button1.pack()

	def reset_service(self):
		self.controller.selected = False
		self.controller.show_frame(ServicesSearch)

class DeveloperMode(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)


# Driver Code
app = tkinterApp()
app.mainloop()
