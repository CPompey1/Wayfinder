from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import Canvas
import ttkbootstrap as ttkint
from PIL import ImageTk, Image, ImageOps
import json, time, threading, asyncio
from BFS import BFS
from MPU.run_mpu import MpuClass
from globals import *
from globals import SIMULATION,sharedData
from BeaconManager import BeaconManager
if not SIMULATION: from MPU.run_mpu import runMpu
from globals import EMITTER_LOC_DICT
from tra_localization import tra_localization

from BeaconManager import BeaconManager
from MPU.run_mpu import MpuClass
from tra_localization import localization

FONT = "Calibri 26 bold"
FONT_SERVICES = "Calibri 15"
FONT_BUTTON =  "Calibri 12"

class App:
	async def exec(self):
		loop = asyncio.get_event_loop()
		self.window = tkinterApp(loop)
		
		await self.window.frames[StartPage].start_page_layout()
		print("Broke the while loop")
		page_num = 6
		while True:
			if(self.window.flags[0] and not page_num == 0):
				page_num = 0
				self.window.show_frame(StartPage)#disgusting
			elif(self.window.flags[1] and not page_num == 1):
				page_num = 1
				self.window.show_frame(ServicesSearch)#disgusting
			elif(self.window.flags[2] and not page_num == 2):
				page_num = 2
				self.window.show_frame(NavigationPage)
				await self.window.frames[NavigationPage].paint()#absolutely disgusting
			elif(self.window.flags[3] and not page_num == 3):				#disgusting
				page_num = 3
				self.window.show_frame(PasswordCheck)
			elif(self.window.flags[4] and not page_num == 4):
				page_num = 4
				self.window.show_frame(DeveloperMode)
				if(self.window.check_beacons_range):
					self.window.frames[DeveloperMode].check_beacons()
				self.window.check_beacons_range = False

			self.window.update()
			await asyncio.sleep(.1)

# Helper function to flatten a list of lists. Returns a list
def flatten(list_of_list):
    if isinstance(list_of_list, list):
        fin_list = []
        for el in list_of_list:
            fin_list.extend(flatten(el))
        return fin_list
    else:
        return [list_of_list]
	
# Helper function for draw_path
def grid2Pixel(inp,floor):
	match(floor):
		case 0:
			return [(inp[0] * PIXELS_PER_GRID_FLOOR_B_X) + ELEVATOR_PIXEL_X_FLOOR_B + (PIXELS_PER_GRID_FLOOR_B_X / 2), ELEVATOR_PIXEL_Y_FLOOR_B - (inp[1] * PIXELS_PER_GRID_FLOOR_B_Y) - (PIXELS_PER_GRID_FLOOR_B_Y / 2)]
		case 1:
			return [(inp[0] * PIXELS_PER_GRID_FLOOR_1_X) + ELEVATOR_PIXEL_X_FLOOR_1 + (PIXELS_PER_GRID_FLOOR_1_X / 2), ELEVATOR_PIXEL_Y_FLOOR_1 - (inp[1] * PIXELS_PER_GRID_FLOOR_1_Y) - (PIXELS_PER_GRID_FLOOR_1_Y / 2)]
		case 2:
			return [(inp[0] * PIXELS_PER_GRID_FLOOR_2_X) + ELEVATOR_PIXEL_X_FLOOR_2 + (PIXELS_PER_GRID_FLOOR_2_X / 2), ELEVATOR_PIXEL_Y_FLOOR_2 - (inp[1] * PIXELS_PER_GRID_FLOOR_2_Y) - (PIXELS_PER_GRID_FLOOR_2_Y / 2)]
		case 3:
			return [(inp[0] * PIXELS_PER_GRID_FLOOR_3_X) + ELEVATOR_PIXEL_X_FLOOR_3 + (PIXELS_PER_GRID_FLOOR_3_X / 2), ELEVATOR_PIXEL_Y_FLOOR_3 - (inp[1] * PIXELS_PER_GRID_FLOOR_3_Y) - (PIXELS_PER_GRID_FLOOR_3_Y / 2)]
		case 4:
			return [(inp[0] * PIXELS_PER_GRID_FLOOR_4_X) + ELEVATOR_PIXEL_X_FLOOR_4 + (PIXELS_PER_GRID_FLOOR_4_X / 2), ELEVATOR_PIXEL_Y_FLOOR_4 - (inp[1] * PIXELS_PER_GRID_FLOOR_4_Y) - (PIXELS_PER_GRID_FLOOR_4_Y / 2)]
		case 5:
			return [(inp[0] * PIXELS_PER_GRID_FLOOR_5_X) + ELEVATOR_PIXEL_X_FLOOR_5 + (PIXELS_PER_GRID_FLOOR_5_X / 2), ELEVATOR_PIXEL_Y_FLOOR_5 - (inp[1] * PIXELS_PER_GRID_FLOOR_5_Y) - (PIXELS_PER_GRID_FLOOR_5_Y / 2)]


# Wayfinder wi	
class tkinterApp(tk.Tk):
	def __init__(self, loop): 
		tk.Tk.__init__(self)
		# Starting values of some of the flags used in different UI pages
		self.stairs = BooleanVar(value=True)	# Defaults that the user is taking stairs
		self.started = False					# Used to keep track of the threads start
		self.check_beacons_range = False		# Used to detect the beacons in DeveloperMode
		self.selected = False					# Used in SelectServices to decide whether or not a service was selected, and confirmed
		self.enter = False						# Used in PasswordCheck to verify if the user entered the password or not
		self.sel_room = StringVar()				# Placeholder for the selected room 
		self.sel_service = "All services"		# Defaults to the "All services" list, where all the rooms are listed alphabetically
		self.loop = loop						# Event loop, has to be passed to all frames
		self.flags = [True, False, False, False, False]	# Start at StartPage, everything else is False
		self.ck_bool_dict = {}					# Dictionary for DeveloperMode checkboxes boolean variables
		self.ck_button_dict = {}				# Dictionary for DeveloperMode checkboxes

		self.beaconManager = BeaconManager()
		self.update_beacons_thread =  self.loop.create_task(self.beaconManager.update_beacons())
		# self.loop.run_until_complete(self.beaconManager.update_beacons())
		# self.loop.create_task(self.beaconManager.update_beacons())
		self.mpu = MpuClass()
		self.bfs = BFS()
		self.navigation_thread = None

		# Current Geometry of the page. CHANGE THIS TO SWITCH TO FULLSCREEN
		self.geometry("768x1024")
		#self.attributes('-fullscreen', True)

		# Creating the Wayfinder window
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

		# Reading json files to create services lists for the ServicesSearch page
		self.json_file_dict: dict = json.load(open("services.json"))
		self.beacons_dict: dict = json.load(open("node.json"))
		self.service_array = list(self.json_file_dict["service_group"][0].keys())
		all_services = []
		for i in range(len(self.service_array)):
			floor_array = self.json_file_dict["service_group"][0][self.service_array[i]][0]
			all_services.append(flatten(list(floor_array.values())))
		all_services = flatten(all_services)
        # Filter not None. Not required, but just in case :).
		self.all_valid_serv = list(filter(None,all_services))
        # Order alphabetically all reachable rooms
		self.all_valid_serv = sorted(self.all_valid_serv)

		# Create all frames (UI pages), and pass the eventloop to all of them
		self.frames = {}
		for F in (StartPage, ServicesSearch, NavigationPage, PasswordCheck, DeveloperMode):
			frame = F(container, self, self.loop)
			self.frames[F] = frame 
			frame.grid(row = 0, column = 0, columnspan=4, sticky ="nsew")
		self.show_frame(StartPage)			# Display starting page

		self.localization_thread = None		# Placeholder for loacalization thread
		self.mpu_thread = None				# Placeholder for mpu thread
		
		# Change the protocol of the window. When the user closes the window, all threads close, and EVERYTHING should be closed/stopped
		self.protocol("WM_DELETE_WINDOW", lambda : self.close())
		self.bind("<Escape>", lambda e: self.close())			# Binds the ESC key to the window closure. Useful in fullscreen mode

	# All threads close, and EVERYTHING should be closed/stopped
	def close(self):
		sharedData.closing = True
		if self.mpu_thread is not None:	
			self.mpu_thread.join()
		if self.localization_thread is not None:
			self.localization_thread.join()
		if self.loop is not None:
			self.loop.stop()
		if self.navigation_thread != None:
			self.navigation_thread.join()
			self.beaconManager.close()
		self.destroy()

	# Display the current frame. Frame class is passed as a parameter
	def show_frame(self, frame_class):
		frame = self.frames[frame_class]
		frame.tkraise()

		# Set flags so that only one page is displayed at a time. Need this in the while loop in the App class,
		# to call the correct function, based on the displayed frame
		self.flags = [frame_class == StartPage, frame_class == ServicesSearch, frame_class == NavigationPage, frame_class == PasswordCheck, frame_class == DeveloperMode]

	def enable_navigation(self):
		# Turn ServicesSearch flag on, everything else off.
		self.flags = [False, True, False, False, False]

		# Start threads for beacons detection and mpu 
		if not self.started:
			self.started = True
			self.localization_thread = threading.Thread(target=localization,args=(self.beaconManager,))
			self.mpu_tread = threading.Thread(target=self.mpu.runMpu)

			self.localization_thread.start()
			self.mpu_tread.start()
			print("started threads")


# Home page, with buttons to choose Developer Mode or Start Navigation
class StartPage(tk.Frame):
	def __init__(self, parent, controller: tkinterApp, loop): 
		# Set event loop and controller parent
		self.controller = controller
		self.loop = loop
		asyncio.set_event_loop(self.loop)
		tk.Frame.__init__(self, parent)

	# Layout of start page
	async def start_page_layout(self):
		# Insert welcome label
		title_label = Label(self, text= "Welcome to Lockwood Wayfinder!", font=FONT)
		title_label.pack(pady=10)
		# Insert picture of library
		img = ImageTk.PhotoImage(Image.open("lockwood_main.jpg"))
		panel = Label(self, image=img)
		panel.image = img
		panel.pack(pady=10)
		start_frame = Frame(self, bg="white")
		# Button to select service
		start_button = ttk.Button(master=start_frame, text= "Start Navigating", command = lambda : self.controller.enable_navigation())
		start_button.pack(pady=10)
		# Button for enter password for developer mode
		dev_mode_button = ttk.Button(master=start_frame, text= "Developer Mode", command = lambda: self.controller.show_frame(PasswordCheck))
		dev_mode_button.pack(pady=10)
		start_frame.pack()
		
class ServicesSearch(tk.Frame):
	def __init__(self, parent, controller: tkinterApp, loop):
		# Set event loop and controller parent
		self.controller = controller
		self.loop = loop
		asyncio.set_event_loop(self.loop)
		tk.Frame.__init__(self, parent)
		self.page_frame = tk.Frame(self)
		self.listbox_frame = tk.Frame(self.page_frame)
		# Listbox for type of services
		self.services_lb = tk.Listbox(self.listbox_frame, height = len(controller.service_array)+1, width = 10, font=FONT, name='service_list')
		# Include an "all services" category with all reachable services
		self.services_lb.insert(tk.END, "All services")
		for item in controller.service_array:
			self.services_lb.insert(tk.END, item)
		self.services_lb.grid(column=0, row=0, sticky='news', padx=0, pady=2)
		self.services_lb.bind('<<ListboxSelect>>', self.onselect)		# Show correspondent lists of room 
		self.services_lb.select_set(0)
		# Listbox for all rooms in the selected type of service
		self.room_lb = Listbox(self.listbox_frame, font=FONT_SERVICES, width = 60, name='room_list', selectmode="SINGLE")
		for room in controller.all_valid_serv:
			self.room_lb.insert(tk.END, room)
		self.room_lb.grid(column=1, columnspan=4, row=0, sticky='nwse', padx=0, pady=2)
		self.room_lb.bind('<Double-1>', self.service_confirmation)		# Ask for confirmation on selected service 
		self.listbox_frame.pack()
		# Create frame under listboxes
		bottom_frame = tk.Frame(self.page_frame)
		bottom_frame.grid_columnconfigure(0, weight=5, uniform="a")
		back_butt = ttk.Button(bottom_frame, text= "Back", command = lambda : self.controller.show_frame(StartPage))
		back_butt.grid(column=0, row=0, padx=10, pady = 6, sticky="w")
		# Create radio buttons to selected stairs or elevator as preference
		s_or_el = ttk.Label(bottom_frame, text ="Stairs/Elevator Preference: ", font = FONT_SERVICES).grid(column=1, row=0, padx=10, pady = 6)
		R1 = Radiobutton(bottom_frame, text="Stairs", variable=self.controller.stairs, value=True).grid(column=2, row=0, padx=10, pady = 6)
		R2 = Radiobutton(bottom_frame, text="Elevator", variable=self.controller.stairs, value=False).grid(column=3, row=0, padx=10, pady = 6)
		bottom_frame.pack()
		self.page_frame.pack()

	def onselect(self, evt: Event):
		if not evt.widget.curselection():
			return
		# Note here that Tkinter passes an event object to onselect()
		w = evt.widget.curselection()[0] - 1 # Number from 0 to n number of services categories to exclude "ALL" category
		self.controller.sel_service = str(self.services_lb.get(self.services_lb.curselection()))
		floor_array = {}
		# print(self.controller.sel_service)
		# Side menu depending on selected service
		floor_array = self.controller.json_file_dict["service_group"][0][self.controller.service_array[w]][0]
		list_services = flatten(list(floor_array.values()))
		# Listbox for rooms based on the selected service
		self.room_lb = Listbox(self.listbox_frame, font=FONT_SERVICES, width = 60, name='room_list', selectmode="SINGLE")
		if w == -1:		# All services are selected in this case
			for room in self.controller.all_valid_serv:
				self.room_lb.insert(tk.END, room)
		else:			# Else create a listbox with the correct services category room
			floor_array = self.controller.json_file_dict["service_group"][0][self.controller.service_array[w]][0]
			list_services = flatten(list(floor_array.values()))
			for room in list_services:
				self.room_lb.insert(tk.END, room)
		self.room_lb.grid(column=1, columnspan=4, row=0, sticky='nwse', padx=0, pady=2)
		self.room_lb.bind('<Double-1>', self.service_confirmation)
		self.grid_columnconfigure(1, weight=5)

	def service_confirmation(self, args: Event):
		if not args.widget.curselection():
			return
		if not self.controller.selected:
			self.controller.selected = True
			idx = args.widget.curselection()[0]
			if self.controller.sel_service != "All services":
				floor_services_flat= flatten(list(self.controller.json_file_dict["service_group"][0][self.controller.sel_service][0].values()))
			    # Getting rid of None values from json file
				serv_not_none = list(filter(None,floor_services_flat))
				self.controller.sel_room.set(serv_not_none[idx])
			else:
			    # If selected from the "All services" list
				self.controller.sel_room.set(self.controller.all_valid_serv[idx])
			# Create a MessageBox for confirmation of service
			mess= "Selected service: \""
			mess = mess + self.controller.sel_room.get()
			mess = mess + "\". \nWould you like to proceed?"
			selection = messagebox.askyesno(title="Service confirmation", message=mess, parent=self)
			if selection:	# If user confirms, start navigation
				self.controller.show_frame(NavigationPage)
				self.controller.selected = True
			else:			# Otherwise, reset selected flag and return to the ServiceSearch page
				self.controller.selected = False



# Third window for actual navigation to goal
class NavigationPage(tk.Frame): 
	def __init__(self, parent, controller: tkinterApp, loop):
		# Set event loop and controller parent
		self.loop = loop
		asyncio.set_event_loop(self.loop)
		self.controller = controller
		tk.Frame.__init__(self, parent)

		# Add label with selected service to reach
		mess = "Goal: "+ str(controller.sel_room.get())
		nav_label = Label(self, text= "Wayfinder Navigation", font=FONT).pack()
		service_label = Label(self, textvariable= self.controller.sel_room, font=FONT_SERVICES).pack()
		# Back button
		back_sel_service = ttk.Button(self, text ="Back", command = self.reset_service)
		back_sel_service.pack(pady=5)
		# Create Canvas to draw the path to goal in
		w = self.winfo_screenwidth()
		h = self.winfo_screenheight()
		self.screen = Canvas(master=self, width=w, height=h)
		self.screen.pack(anchor="center")

	def reset_service(self):
		self.controller.selected = False
		self.controller.show_frame(ServicesSearch)

	#draws the path made from BFS onto the corresponding map image
	async def paint(self):
		#need to grab user destination and preference
		dest_id = self.controller.sel_room.get()
		preference = "stairs" if self.controller.stairs.get() else "elevator"
		#get the user location from the navigation thread and convert to grid coordinates
		user_location_feet = (0,0,-1)
		#user_location_feet = (50,-30,2)
		while(user_location_feet == (0,0,-1)):
			user_location_feet = sharedData.get_estimated_location()
			await asyncio.sleep(0.1)

		user_node = self.controller.bfs.feet_to_node_units(user_location_feet[0], user_location_feet[1])

		#compute shortest path
		end_location = self.controller.bfs.find_destination_by_id(dest_id, (user_node[0], user_node[1], round(user_location_feet[2])), self.controller.bfs.endpoints)
		nodePath = self.controller.bfs.find_path((user_location_feet[0], user_location_feet[1], round(user_location_feet[2])), dest_id, self.controller.bfs.nodes, self.controller.bfs.graph, self.controller.bfs.endpoints, preference)
		locations = {}
		
		list_of_paths = [[]]
		stair_count = 0
		#turn path into a list of start and end points for drawing
		for i in range(len(nodePath) - 1):
			if(self.controller.bfs.nodes[nodePath[i]]["location"][2] == self.controller.bfs.nodes[nodePath[i+1]]["location"][2]):
				list_of_paths[stair_count].append([self.controller.bfs.nodes[nodePath[i]]["location"], self.controller.bfs.nodes[nodePath[i+1]]["location"]])
			else:
				list_of_paths.append([])
				stair_count = stair_count + 1
			locations[nodePath[i]] = self.controller.bfs.nodes[nodePath[i]]["location"]

		if(len(list_of_paths[0]) != 0):
			list_of_paths[0].insert(0,[(user_node[0],user_node[1],user_location_feet[2]),list_of_paths[0][0][0]])
		else:
			list_of_paths.pop(0)

		#continuously redraw the path with the given path information and user location
		await self.repaint(list_of_paths, user_node, end_location)
	

	async def repaint(self, list_of_paths, user_position, end):
		
		#user_location = [50,-30,2]
		user_location = [0,0,-1]
		stair_count = 0

		current_user_pos = (user_position[0], user_position[1], 2)
		previous_user_pos = (user_position[0], user_position[1], 2)
		while True:
			#get user position and orientation from navigation and mpu threads
			orientation = sharedData.get_orientation()
			user_location = sharedData.get_estimated_location()
			#convert user position to a grid location
			current_user_pos = (self.controller.bfs.feet_to_node_units(user_location[0], user_location[1])[0], self.controller.bfs.feet_to_node_units(user_location[0], user_location[1])[1], round(user_location[2]))
			#current_user_pos = (current_user_pos[0] - 1, current_user_pos[1] + 1, list_of_paths[stair_count][0][0][2] * 100)
			#draw the BFS path for the current floor
			self.draw_path(list_of_paths, stair_count)
			
			#draw the user position and orientation on top of the map and BFS path
			img_floor = Image.open("IconCircle.png")
			img = img_floor.resize((25,25), Image.Resampling.LANCZOS).rotate(orientation)
			img_tk = ImageTk.PhotoImage(img)
			sample = grid2Pixel(current_user_pos[0:2],current_user_pos[2])
			self.screen.create_image(sample[0],sample[1], image= img_tk, anchor= "nw")

			#POSSIBLE LATER
				#DIRECTION OF MOVEMENT FROM IMU AND COMPARE IT TO DIRECTION OF MOVEMENT OF NAVIGATION
				#IF THEY ARE WITHIN +- 45 DEGREES, ACCEPTABLE
				#|---|---|---|
				#| o | o | o |  IF MOVEMENT FROM IMU IS POSITIVE UP, THEN THREE GRID COORDINATES ARE VALID
				#|---|---|---|
				#| x | H | x |
				#|---|---|---|
				#| x | x | x |
				#|---|---|---|
			
				#|---|---|---|
				#| o | o | X |  IF MOVEMENT FROM IMU IS DIAGONAL UP AND LEFT, THEN THREE GRID COORDINATES ARE VALID
				#|---|---|---|
				#| o | H | x |
				#|---|---|---|
				#| x | x | x |
				#|---|---|---|
			changed = False
			if (current_user_pos[2] != previous_user_pos[2]):
				previous_user_pos = current_user_pos
				for i in range(0,len(list_of_paths),1):
					if(not changed and len(list_of_paths[i]) > 0 and current_user_pos[2] == list_of_paths[i][0][0][2]):
						stair_count = i
						changed = True

			elif current_user_pos != previous_user_pos:

				previous_user_pos = current_user_pos

				found_node_in_path = False
				removedCount = 0
				for i in range(len(list_of_paths[stair_count])):
					#if the current user position exists in the path, remove the node from the path
					if (not found_node_in_path) and (abs(current_user_pos[0] - list_of_paths[stair_count][i - removedCount][1][0]) <= 1) and (abs(current_user_pos[1] - list_of_paths[stair_count][i - removedCount][1][1]) <= 1) and (current_user_pos[2] == list_of_paths[stair_count][i - removedCount][1][2]):
						end = len(list_of_paths[stair_count])
						for j in range(0,i+1,1):
							list_of_paths[stair_count].pop(0)
							removedCount = removedCount + 1
						found_node_in_path = True
				if(len(list_of_paths[stair_count]) == 0):
					stair_count = stair_count + 1
					if(stair_count == len(list_of_paths)):
						return
				#if the current user position was not in the path, check to see if they reached another node and add it
				if not found_node_in_path:
					for i in self.controller.bfs.nodes:
						if current_user_pos == self.controller.bfs.nodes[i]["location"]:
							list_of_paths[stair_count].insert(0, [self.controller.bfs.nodes[i]["location"],list_of_paths[stair_count][0][0]])

			self.update()
			await asyncio.sleep(1)


	def draw_path(self, list_of_paths, stair_count):
		#clear the screen by redrawing thr background image
		img_floor = Image.open("flr" + str(int(list_of_paths[stair_count][0][0][2])) + "_larger.jpg")
		img_floor = ImageOps.exif_transpose(img_floor)
		width, height = int(img_floor.width / 2), int(img_floor.height / 2) 
		img = img_floor.resize((width,height), Image.Resampling.LANCZOS)#.rotate(-90)
		self.screen.configure(background="white", width=img.width, height=height)
		img_tk = ImageTk.PhotoImage(img)
		self.screen.image = img_tk
		self.screen.create_image(0,0, image= img_tk, anchor= "nw")
		self.update()
		
		for i in range(0,len(list_of_paths[stair_count]),1):
			self.screen.create_line(grid2Pixel(list_of_paths[stair_count][i][0][0:2],list_of_paths[stair_count][i][0][2])[0],
							grid2Pixel(list_of_paths[stair_count][i][0][0:2],list_of_paths[stair_count][i][0][2])[1],
							grid2Pixel(list_of_paths[stair_count][i][1][0:2],list_of_paths[stair_count][i][1][2])[0],
							grid2Pixel(list_of_paths[stair_count][i][1][0:2],list_of_paths[stair_count][i][1][2])[1],
							fill="blue", width = 3)


# Page for Password insertion for Developer Mode 
class PasswordCheck(tk.Frame):
	def __init__(self, parent, controller: tkinterApp, loop):
		# Set event loop and controller parent
		self.loop = loop
		asyncio.set_event_loop(self.loop)
		tk.Frame.__init__(self, parent)
		self.controller = controller

		# Create field for passcode
		passcode_frame = Frame(self, bg="white")
		self.passcode = tk.StringVar()
		self.passcode.set("")
		self.controller.enter= False      # True when Enter is pressed
		# Label that is displayed when a passcode is inserted for wrong passcode
		self.right_wrong_label = tk.Label(self, text = "")

		self.entry_label = tk.Label(self, text="Enter Passcode:").pack()
		# Passcode entry that updates during insertion with "*"
		self.passcode_entry = tk.Entry(self, textvariable=self.passcode, show='*', font=FONT_BUTTON).pack()

		# Create number keyboard
		self.keypad_buttons = [	'1', '2', '3',
								'4', '5', '6',
								'7', '8', '9',]
		row_num = 2
		col_num = 0
		for key in self.keypad_buttons:
			button = tk.Button(passcode_frame, text=key, font=FONT_BUTTON, width=10, height=4, command=lambda key=key: self.update_passcode(key))
			button.grid(row=row_num, column=col_num, padx=5, pady=5)
			col_num += 1
			if col_num > 2:
				col_num = 0
				row_num += 1
		# Add clear, 0 and Home button on the next line
		self.clear_button = tk.Button(passcode_frame, text="Clear", font=FONT_BUTTON, width=10, height=4, command=self.clear_passcode)
		self.clear_button.grid(row=row_num, column=0, padx=5, pady=5)
		zero_button = tk.Button(passcode_frame, text='0', font=FONT_BUTTON, width=10, height=4, command=lambda key=key: self.update_passcode('0'))
		zero_button.grid(row=row_num, column=1, padx=5, pady=5)
		self.home_button = tk.Button(passcode_frame, text="Home", font=FONT_BUTTON, width=10, height=4, command=self.home)
		self.home_button.grid(row=row_num, column=2, padx=5, pady=5)
		passcode_frame.pack()
		# Add enter button 
		self.enter_butt = tk.Button(self, text= "Enter", font=FONT_BUTTON, width=34, height=3, command = self.enter_passcode).pack(pady=5)

	# Clear passcode and return to home page if Home button is pressed
	def home(self):
		self.clear_passcode()
		self.controller.show_frame(StartPage)

	# When number key is pressed, update passcode with the pressed key appended as a string char
	def update_passcode(self, key):
		if not self.controller.enter:
			self.right_wrong_label.configure(text="")
			self.passcode.set(self.passcode.get() + key)
	
	# Reset passcode if clear is pressed
	def clear_passcode(self):
		self.passcode.set("")
		self.controller.enter= False
	
	# When Enter is pressed, check for passcode correctness
	# Display string for wrong passcode and reset the passcode entry in case
	# Switch to DeveloperMode page if passcode is correct 
	def enter_passcode(self):
		if self.passcode.get() == str(3054):
			self.controller.show_frame(DeveloperMode)
			self.controller.check_beacons_range = True
			self.controller.enter= True
		else:
			self.right_wrong_label.configure(text="Wrong passcode!")
		self.right_wrong_label.pack()
		self.passcode.set("")

class DeveloperMode(tk.Frame):
	def __init__(self, parent, controller: tkinterApp, loop):
		# Set event loop and controller parent
		tk.Frame.__init__(self, parent)
		self.loop = loop
		asyncio.set_event_loop(self.loop)
		self.controller = controller

		self.controller.check_beacons_range = False
		# Add back button to go to HomeScreen
		back_butt = ttk.Button(self, text= "Home", command = self.home).pack()
		# Create frame with all Checkboxes next to all possible beacons
		self.check_frame = Frame(self)
		self.controller.ck_bool_dict = {}
		self.controller.ck_button_dict = {}
		self.beacons_keys = list(EMITTER_LOC_DICT.keys())
		row_num = 0
		col_num = 0
		self.check_frame.grid_rowconfigure(0, weight = 1)
		self.check_frame.grid_columnconfigure(0, weight = 1)
		self.already_checked = {}
		for beacons_index in range(int(len(self.beacons_keys))):
			beacon_id = str(self.beacons_keys[beacons_index])
			ck_val = tk.IntVar()  	# Defaults to 0
			self.controller.ck_bool_dict[beacon_id]= ck_val
			ck = ttk.Checkbutton(master=self.check_frame,text=beacon_id, onvalue = 1, offvalue = 0, variable=self.controller.ck_bool_dict[beacon_id])
			ck.grid(row=row_num, column=col_num, padx=5, pady=5)
			col_num += 1
			if col_num > 3:
				col_num = 0
				row_num += 1
			self.controller.ck_button_dict[beacon_id] = ck
		self.check_frame.pack()

	# Check beacond based on proximity. If the beacon is detected, check its corresponding checkbox. Beacons checkboxes checked only once
	def check_beacons(self):
		if(self.controller.check_beacons_range):
			for beacon_key in self.beacons_keys:
				if beacon_key in self.controller.beaconManager.beacons and not beacon_key in self.already_checked.keys():
					self.controller.ck_bool_dict[beacon_key].set(1)
					self.already_checked[beacon_key] = True
	
	# Return to StartPage when back button is pressed
	def home(self):
		self.controller.enter = False
		self.controller.check_beacons_range = False
		self.controller.show_frame(StartPage)

# Main function			
asyncio.run(App().exec())