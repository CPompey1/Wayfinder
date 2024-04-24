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
from BeaconManager import BeaconManager
if not SIMULATION: from MPU.run_mpu import runMpu
from globals import EMITTER_LOC_DICT
from tra_localization import tra_localization
from globals import *

from BeaconManager import BeaconManager
from MPU.run_mpu import MpuClass
from tra_localization import localization

FONT = "Calibri 26 bold"
FONT_SERVICES = "Calibri 15"

class App:
	async def exec(self):
		self.window = tkinterApp(asyncio.get_event_loop())
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
				self.window.frames[NavigationPage].paint()#aabsolutely disgusting
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
		#what's the course password?
		#Yeah, that's right. It works
  
		#initialize_task = asyncio.create_task(self.window.beaconManager.initialize_scanning())
		#await initialize_task

def flatten(list_of_list):
    if isinstance(list_of_list, list):
        fin_list = []
        for el in list_of_list:
            fin_list.extend(flatten(el))
        return fin_list
    else:
        return [list_of_list]
	
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


	
class tkinterApp(tk.Tk):
	def __init__(self, loop): 
		tk.Tk.__init__(self)
		print("HEREEEE")
		#init classes
		self.loop = loop
		self.check_beacons_range = False
		self.flags = [True, False, False, False, False]

		self.beaconManager = BeaconManager()
		self.loop.create_task(self.beaconManager.update_beacons())
		self.mpu = MpuClass()
		self.bfs = BFS()
		self.navigation_thread = None
		self.started = False
		# self.event_loop = asyncio.get_event_loop()
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


		# initializing frames to an empty dictionary
		self.frames = {}
		self.json_file_dict: dict = json.load(open("services.json"))
		self.beacons_dict: dict = json.load(open("node.json"))
		self.service_array = list(self.json_file_dict["service_group"][0].keys())
		self.beacons_list = list(self.beacons_dict["beacons"])
		self.dest_list = list(self.beacons_dict["destinations"])
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
		self.enter = False
		self.sel_room = StringVar()
		self.sel_service = "All services"
		self.ck_bool = []
		self.ck_button = []
		# iterating through a tuple consisting
		# of the different page layouts
		for F in (StartPage, ServicesSearch, NavigationPage, PasswordCheck, DeveloperMode):
			frame = F(container, self)

			# initializing frame of that object from
			# startpage, page1, page2 respectively with 
			# for loop
			self.frames[F] = frame 

			frame.grid(row = 0, column = 0, columnspan=4, sticky ="nsew")
		self.show_frame(StartPage)
		
	
		# while True:
		# 	container.update()
		# 	await asyncio.sleep(.1)
			



	# to display the current frame passed as
	# parameter
	def show_frame(self, cont):
		frame = self.frames[cont]
		frame.tkraise()
		self.flags = [cont == StartPage, cont == ServicesSearch, cont == NavigationPage, cont == PasswordCheck, cont == DeveloperMode]

	def enable_navigation(self, cont):
		self.flags = [False, True, False, False, False]
		
		#frame = self.frames[cont]
		# frame.tkraise()
		# if not self.started:
		if not self.started:
			self.started = True
			# self.loop.create_task
			# (target=self.beaconManager.initialize_scanning)
			# self.loop.create_task(self.beaconManager.update_beacons())
			# self.initialize_task_thread = asyncio.run(self.beaconManager.initialize_scanning())
			self.localization_thread = threading.Thread(target=localization,args=(self.beaconManager,))
			# self.initialize_task_thread = asyncio.create_task(self.beaconManager.initialize_scanning())
			self.mpu_tread = threading.Thread(target=self.mpu.runMpu)

			self.localization_thread.start()
			
			# self.initialize_task_thread.start()
			self.mpu_tread.start()

			print("started threads")
		# 	self.started = Tru
		# 	self.localization_thread = asyncio.create_task(localization())
		# 	self.create_task = (self.mpu.run_mpu())

		# 	await self.localization_thread
			# await self.initialize_task
		# 	await self.create_task


# first window frame startpage

class StartPage(tk.Frame):
	def __init__(self, parent, controller: tkinterApp): 
		self.controller = controller
		
		tk.Frame.__init__(self, parent)
		#self.start_page_layout()


	async def start_page_layout(self):
		title_label = Label(self, text= "Welcome to Lockwood Wayfinder!", font=FONT)
		title_label.pack(pady=10)
		img = ImageTk.PhotoImage(Image.open("lockwood_main.jpg"))
		panel = Label(self, image=img)
		panel.image = img
		panel.pack(pady=10)
		start_frame = Frame(self, bg="white")
		start_button = ttk.Button(master=start_frame, text= "Start Navigating", command = lambda : self.controller.enable_navigation(ServicesSearch))
		start_button.pack(pady=10)
		dev_mode_button = ttk.Button(master=start_frame, text= "Developer Mode", command = lambda: self.controller.show_frame(PasswordCheck)
		)
		dev_mode_button.pack(pady=10)
		start_frame.pack()
		#start_page = asyncio.create_task(self.update_start())
	#	await start_page
		await self.update_start()

	async def update_start(self):
		while self.controller.flags[0]:
			print("Here")
			self.update()
			await asyncio.sleep(.1)
		
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
		back_butt = ttk.Button(self, text= "Back", command = lambda : self.controller.show_frame(StartPage))
		back_butt.grid(column=0, row=2,sticky="nw", padx=10, pady = 6)
		frame = tk.Frame(self)
		frame.grid(row = 2, column = 1, sticky="nwes",  padx=10, pady = 6)
		s_or_el = ttk.Label(frame, text ="Stairs/Elevator Preference: ", font = FONT_SERVICES).pack()
		R1 = Radiobutton(frame, text="Stairs", variable=self.controller.stairs, value=True).pack()
		R2 = Radiobutton(frame, text="Elevator", variable=self.controller.stairs, value=False).pack()
		self.controller.sel_service = "All services"

		

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
				self.controller.sel_room.set(serv_not_none[idx])
			else:
			    # If selected from the "All services" list
				self.controller.sel_room.set(self.controller.all_valid_serv[idx])
			mess= "Selected service: \""
			mess = mess + self.controller.sel_room.get()
			mess = mess + "\". \nWould you like to proceed?"
			selection = messagebox.askyesno(title="Service confirmation", message=mess, parent=self)
			if selection:
				#self.start_navigation(sel_service)
				self.controller.show_frame(NavigationPage)
				self.controller.selected = True
			else:
				self.controller.selected = False



# third window frame page2
class NavigationPage(tk.Frame): 
	def __init__(self, parent, controller: tkinterApp):
		self.controller = controller
		tk.Frame.__init__(self, parent)
		mess = "Goal: "+ str(controller.sel_room.get())
		nav_label = Label(self, text= "Wayfinder Navigation", font=FONT).pack()
		service_label = Label(self, textvariable= self.controller.sel_room, font=FONT_SERVICES).pack()
		back_sel_service = ttk.Button(self, text ="Back", command = self.reset_service)
		back_sel_service.pack(pady=5)
		
		w = self.winfo_screenwidth()
		h = self.winfo_screenheight()
		self.screen = Canvas(master=self, width=w, height=h)
		self.screen.pack(anchor="center")


		

	def paint(self):
		# Code for drawing
		dest_id = "Basement Bathroom"
		preference = "stairs"
		user_location_feet = (-6, 78, 0)
		user_node = self.controller.bfs.feet_to_node_units(user_location_feet[0], user_location_feet[1])
		
		# Here the data coming from the beacon 
		start = [130,0]

		# Destination comes from JSON file and user selection
		#eleveator pixel origin (130,400)
		goal = [130, 403]
		
		end_location = self.controller.bfs.find_destination_by_id(dest_id, self.controller.bfs.endpoints)
		nearest_node_id = self.controller.bfs.find_nearest_node_feet(user_location_feet, self.controller.bfs.nodes)
		nodePath = self.controller.bfs.find_path(user_location_feet, dest_id, self.controller.bfs.nodes, self.controller.bfs.graph, self.controller.bfs.endpoints, preference)
		locations = {}
		# for node in self.bfs.nodes.keys():
		#     if node in nodePath:
		#         locations[node] = self.bfs.nodes[node]["location"]
		
		start = []
		goal = []
		for i in range(len(nodePath)):
			if i < len(nodePath) - 1:
				start.append(nodePath[i])
				goal.append(nodePath[i+1])
			locations[nodePath[i]] = self.controller.bfs.nodes[nodePath[i]]["location"]

		self.repaint(start, goal, user_node, end_location)
			


	def reset_service(self):
		self.controller.selected = False
		self.controller.show_frame(ServicesSearch)
	
	def repaint(self, start, goal, user_position, end):
    
		before_stairs = []
		after_stairs = []
		node_path = []
		dest_id = "Third Floot Bathroom_a" ##stub data
		user_location = [0,0,0]
		user_grid_location = [0,0,0]
		#SEPARATE START AND GOAL INTO BEFORE STAIRS AND AFTER STAIRS
		#BEFORE_STAIRS = lines_before_stairs(start,goal)
		#AFTER_STAIRS = lines_after_stairs(start,goal)
		startingFloor = self.controller.bfs.nodes[start[0]]["location"][2]
		twoFloors = False
		for i in range(len(start)):
			#if floors are different
			if self.controller.bfs.nodes[start[i]]["location"][2] != self.controller.bfs.nodes[goal[i]]["location"][2] and not twoFloors:
				before_stairs = after_stairs
				after_stairs = []
				#after_stairs.append(nodeId)
				twoFloors = True
			else:
				after_stairs.append([self.controller.bfs.nodes[start[i]]["location"],self.controller.bfs.nodes[goal[i]]["location"]])

		if len(after_stairs) != 0:
			after_stairs.append([after_stairs[len(after_stairs) - 1][1],end])
		else:
			after_stairs.append([self.controller.bfs.nodes[goal[len(goal) - 1]]["location"],end])

		if twoFloors:
			before_stairs.insert(0,[(user_position[0], user_position[1], startingFloor), before_stairs[0][0]])
		else:
			after_stairs.insert(0,[(user_position[0], user_position[1], startingFloor), after_stairs[0][0]])

        #NEED USER POSITION = NEAREST_NODE_ID
        # nearest_node = self.bfs.find_nearest_node_feet()
        # nearest_node_location = self.bfs.nodes[nearest_node]["location"]
        # floor = nearest_node_location[2]

		self.draw_path(before_stairs, after_stairs)
		while True:
			dest_id = "Third Floot Bathroom_a" ##stub data
			
			#GET USER ORIENTATION FROM IMU (SHARED DATA)
				#orientation = sharedData.get_orientation()
			
			#GET DIRECTION OF MOVEMENT FROM IMU (INCOMPLETE RIGHT NOW)

			#GET USER LOCATION FROM NAVIGATION (SHARED DATA)
			#user_location = sharedData.get_estimated_location()
			user_location = [0,0,0]


			#CONVERT USER POSITION TO GRID SPACE
			user_location_grid_tra = (self.controller.bfs.feet_to_node_units(user_location[0], user_location[1])[0], self.controller.bfs.feet_to_node_units(user_location[0], user_location[1])[1], user_location[2])
			user_location_grid_bfs = user_grid_location

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

            

            #IF USERPOSITION != CURRENT USER POSITION
			if user_location_grid_bfs != user_location_grid_tra:
				#USERPOSITION = CURRENT USER POSITION
				b = FALSE
				user_grid_location = user_location_grid_tra
				#IF BEFORE STAIRS IS NOT EMPTY
				if len(before_stairs) > 0:
					#PATH OF NODES = BEFORE STAIRS
					node_path = before_stairs
					b = TRUE
				else:
					#PATH OF NODES = AFTER STAIRS       #AFTER STAIRS SHOULD ONLY START AFTER REACHING THE NEXT FLOOR
					node_path = after_stairs
				#LOOP THROUGH PATH OF NODES AND CHECK AGAINST POSITIONS
				
				found_node_in_path = False
				for i in range(len(node_path)):
					#IF CURRENT USER POSITION EXISTS IN PATH
					if user_grid_location == node_path[i]:
						#REMOVE THE NODE FROM THE PATH (START AND GOAL VARIABLES LEN - 1)
						for j in range(0,i+1,1):
							if b:
								before_stairs.pop()
							else:
								after_stairs.pop()
						found_node_in_path = True
				
				#ELSE IF CURRENT USER POSITION EXISTS IN LIST OF ALL NODES IN THE CURRENT FLOOR
				if not found_node_in_path:
					for i in self.controller.bfs.nodes:
						if user_grid_location == self.controller.bfs.nodes[i]["location"]:
							if b:
								before_stairs.insert(0, [self.controller.bfs.nodes[i]["location"],before_stairs[0][0]])
							else:
								after_stairs.insert(0, [self.controller.bfs.nodes[i]["location"],after_stairs[0][0]])

                    #ADD NODE TO THE PATH WITH (LEN(GOAL) - 1) INTO LEN(START) AND NEW NODE INTO LEN(GOAL)
                    
                #THEN, REDRAW
            

            #POSSIBLE LATER
                #IF THE USER IMAGE HAS A DIRECTION IT CAN FACE
                    #REDRAW WHEN IMU ORIENTATION CHANGES BY INCREMENTS OF 15 DEGREES
                    #THIS MEANS ONLY REDRAW WHEN IMU ORIENTATION CLOSEST ANGLE IS A DIFFERENT MULTIPLE OF 15 DEGREES


            #hey

			self.update()
			time.sleep(2)

	def draw_path(self, before_stairs, after_stairs):
		#screen = Canvas(page, width= 600, height=550, background="black")
		# screen.pack(anchor='nw', fill='both', expand=1)

		# NEED TO CLEAR THE SCREEN HERE FIRST
		if(len(before_stairs) != 0):
			img_floor = Image.open("flr" + str(before_stairs[0][0][2]) + "_larger.jpg")
		else:  
			img_floor = Image.open("flr" + str(after_stairs[0][0][2]) + "_larger.jpg")
		img_floor = ImageOps.exif_transpose(img_floor)
		width, height = int(img_floor.width / 2), int(img_floor.height / 2) 
		img = img_floor.resize((width,height), Image.Resampling.LANCZOS)#.rotate(-90)
		self.screen.configure(background="white", width=img.width, height=height)
		img_tk = ImageTk.PhotoImage(img)
		self.screen.image = img_tk
		#img_floor = img_floor.resize((500,500), Image.ANTIALIAS)
		# Play with position
		self.screen.create_image(0,0, image= img_tk, anchor= "nw")
		#screen.create_line(start[0],start[1],goal[0], goal[1], fill="red", width = 3)
		self.update()
		
		if len(before_stairs) != 0:
			for i in range(0,len(before_stairs),1):
				self.screen.create_line(grid2Pixel(before_stairs[i][0][0:2],before_stairs[i][0][2])[0],
								grid2Pixel(before_stairs[i][0][0:2],before_stairs[i][0][2])[1],
								grid2Pixel(before_stairs[i][1][0:2],before_stairs[i][1][2])[0],
								grid2Pixel(before_stairs[i][1][0:2],before_stairs[i][1][2])[1],
								fill="blue", width = 3)
		else:
			for i in range(0,len(after_stairs),1):
				self.screen.create_line(grid2Pixel(after_stairs[i][0][0:2],after_stairs[i][0][2])[0],
								grid2Pixel(after_stairs[i][0][0:2],after_stairs[i][0][2])[1],
								grid2Pixel(after_stairs[i][1][0:2],after_stairs[i][1][2])[0],
								grid2Pixel(after_stairs[i][1][0:2],after_stairs[i][1][2])[1],
								fill="blue", width = 3)

		# Destination comes from JSON file and user selection
		#eleveator pixel origin (130,403)
		#goal1 = [150, 400]

		#screen.create_line(start1[0],start1[1],goal1[0], goal1[1], fill="red", width = 3)
		#line_start = grid2Pixel([0,0],1)
		#line_stop = grid2Pixel([2,2],1)
		#screen.create_line(line_start[0],line_start[1],line_stop[0],line_stop[1], fill="green", width = 3)

class PasswordCheck(tk.Frame):
	def __init__(self, parent, controller: tkinterApp):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		passcode_frame = Frame(self, bg="white")
		self.passcode = tk.StringVar()
		self.passcode.set("")
		self.controller.enter= False      # True when Enter is pressed
		self.right_wrong_label = tk.Label(self, text = "")

		self.entry_label = tk.Label(self, text="Enter Passcode:").pack()
		#self.entry_label.grid(row=0, column=0, columnspan=3)

		self.passcode_entry = tk.Entry(self, textvariable=self.passcode, show='*', font=("Arial", 14)).pack()
		#self.passcode_entry.grid(row=0, column=0, columnspan=3, pady=10)

		self.keypad_buttons = [
			'1', '2', '3',
			'4', '5', '6',
			'7', '8', '9',
		]

		row_num = 2
		col_num = 0
		for key in self.keypad_buttons:
			button = tk.Button(passcode_frame, text=key, width=5, height=2, command=lambda key=key: self.update_passcode(key))
			button.grid(row=row_num, column=col_num, padx=5, pady=5)
			col_num += 1
			if col_num > 2:
				col_num = 0
				row_num += 1


		self.clear_button = tk.Button(passcode_frame, text="Clear", width=5, height=2, command=self.clear_passcode)
		self.clear_button.grid(row=row_num, column=0, padx=5, pady=5)
		zero_button = tk.Button(passcode_frame, text='0', width=5, height=2, command=lambda key=key: self.update_passcode('0'))
		zero_button.grid(row=row_num, column=1, padx=5, pady=5)
		self.enter_button = tk.Button(passcode_frame, text="Enter", width=5, height=2, command=self.enter_passcode)
		self.enter_button.grid(row=row_num, column=2, padx=5, pady=5)
		passcode_frame.pack()
	
	def update_passcode(self, key):
		if not self.controller.enter:
			self.right_wrong_label.configure(text="")
			self.passcode.set(self.passcode.get() + key)

	def clear_passcode(self):
		self.passcode.set("")
		self.controller.enter= False

	def enter_passcode(self):
		#print("Passcode entered:", self.passcode.get())
		if self.passcode.get() == str(3054):
			#self.right_wrong_label.configure(text="Right passcode!")
			self.controller.show_frame(DeveloperMode)
			self.controller.check_beacons_range = True
			#print("ajhwjd" + self.contr)
			self.controller.enter= True
		else:
			self.right_wrong_label.configure(text="Wrong passcode!")
		#self.right_wrong_label.grid(row=6, column=0, columnspan=4, padx=5, pady=5)
		self.right_wrong_label.pack()
		self.passcode.set("")

class DeveloperMode(tk.Frame):
	def __init__(self, parent, controller: tkinterApp):

		tk.Frame.__init__(self, parent)
		self.controller = controller
		self.controller.check_beacons_range = False
		back_butt = ttk.Button(self, text= "Home", command = self.home).pack()
		self.check_frame = Frame(self)

	def check_beacons(self):
		print("YESSS")
		if(self.controller.check_beacons_range):
			self.check_frame = Frame(self)
			self.controller.ck_bool = []
			self.controller.ck_button= []
			for beacons_index in range(len(self.controller.beacons_list)):
				beacon_id = "Beacon #" + str(beacons_index)
				ck_val = BooleanVar()
				self.controller.ck_bool.append(ck_val)
				ck = ttk.Checkbutton(master=self.check_frame,text=beacon_id, variable=self.controller.ck_bool[beacons_index])
				ck.config(state=DISABLED)
				ck.pack(padx=5, pady=5)
				self.controller.ck_button.append(ck)
			self.controller.ck_bool[0].set(TRUE)
			self.controller.ck_button[0].invoke()
			self.controller.ck_bool[1].set(TRUE)
			self.controller.ck_button[1].invoke()
			self.check_frame.pack()
	
	def home(self):
		self.controller.enter = False
		self.controller.check_beacons_range = False
		self.check_frame.destroy()
		self.controller.show_frame(StartPage)


# Driver Code
# app = tkinterApp()
# app.mainloop()

asyncio.run(App().exec())
