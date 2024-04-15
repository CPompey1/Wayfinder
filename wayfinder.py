import time
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import Canvas
import ttkbootstrap as ttkint
from PIL import ImageTk, Image, ImageOps
import json
import threading
import asyncio
from BFS import BFS
# from MPU.run_mpu import MpuClass
from MPU.run_mpu import MpuClass
from globals import *
from BeaconManager import BeaconManager
if not SIMULATION: from MPU.run_mpu import runMpu
from globals import EMITTER_LOC_DICT
from tra_localization import tra_localization
from globals import *

FONT = "Calibri 26 bold"
FONT_SERVICES = "Calibri 15"
SCREEN_DIMENSION = "768x1024"



class Wayfinder_UI():
    global service_array
    def __init__(self, file):
    # MAIN PAGE FOR WELCOME
    # Change this based on display dimensions
        super().__init__()
        #initliize beacon manager and threads
        self.beaconManager = BeaconManager()
        # self.manager.initialize_scanning()
        # self.bfs = BFS()
        # self.navigation_thread = None
        self.mpu = MpuClass()
        # if not SIMULATION: 
            
        #     self.mpu_thread = threading.Thread(target=runMpu, daemon=True)
        #     self.mpu_thread.start()
        # else:
        #     self.mpu_thread = threading.Thread(target=sim_mpu, daemon=True)
        #     self.mpu_thread.start()
        
        self.json_file_dict: dict = file
        self.service_array = list(self.json_file_dict["service_group"][0].keys())
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
        self.stairs = True
        self.master = Tk()
        self.master.title('Wayfinder')
        #self.master.focus_set()
        self.master.geometry("%dx%d" % (self.master.winfo_screenwidth(), self.master.winfo_screenheight()))
        #self.master.state('zoomed')
        #self.master.geometry(self.SCREEN_DIMENSION)
        self.sel_service = "Second Floor Elevator"

        self.master.bind("<Escape>", lambda e: self.master.quit())
        self.master = self.master
        
        # title_label = Label(master= self.master, text= "Welcome to Lockwood Wayfinder!", font=FONT).pack()
        # img = ImageTk.PhotoImage(Image.open("lockwood_main.jpg"))
        # panel = Label(self.master, image=img)
        # panel.pack()
        # start_frame = Frame(master=self.master, bg="white")
        # start_button = ttk.Button(master=start_frame, text= "Start Navigating", command = self.stairs_or_el)
        # start_button.pack(side = 'left')
        # start_frame.pack(pady=10)
        # dev_mode_frame = Frame(master=self.master, bg="white")
        # dev_mode_button = ttk.Button(master=dev_mode_frame, text= "Developer Mode", command = self.developer_mode)
        # dev_mode_button.pack(side = 'left')
        # dev_mode_frame.pack(pady=10)
        # self.selected = False
        # self.master.mainloop()
    async def start(self):
        

        
        title_label = Label(master= self.master, text= "Welcome to Lockwood Wayfinder!", font=FONT).pack()
        img = ImageTk.PhotoImage(Image.open("lockwood_main.jpg"))
        panel = Label(self.master, image=img)
        panel.pack()
        start_frame = Frame(master=self.master, bg="white")
        start_button = ttk.Button(master=start_frame, text= "Start Navigating", command = self.stairs_or_el)
        start_button.pack(side = 'left')
        start_frame.pack(pady=10)
        dev_mode_frame = Frame(master=self.master, bg="white")
        dev_mode_button = ttk.Button(master=dev_mode_frame, text= "Developer Mode", command = self.developer_mode)
        dev_mode_button.pack(side = 'left')
        dev_mode_frame.pack(pady=10)
        self.selected = False

        self.start_thread1_button = tk.Button(self, text="Start Thread 1", command=self.start_thread1)
        self.start_thread1_button.pack()

        
        # while True:
        #     self.master.update()
        #     await asyncio.sleep(.1)
        self.master.mainloop()
    # SECOND PAGE FOR SERVICE SELECTION
    # https://www.youtube.com/watch?v=wFyzmZVKPAw    useful video for multiple pages layout
            
    async def select_service(self):
        global services_lb
        global room_lb
        # Creating Treeview for all services
        def onselect(evt: Event):
            if not evt.widget.curselection():
                return
            # Note here that Tkinter passes an event object to onselect()
            w = evt.widget.curselection()[0] - 1 # Number from 0 to n number of services categories to exclude "ALL" category
            self.sel_service = str(services_lb.get(services_lb.curselection()))
            floor_array = {}
            # Side menu depending on selected service
            floor_array = self.json_file_dict["service_group"][0][self.service_array[w]][0]
            list_services = flatten(list(floor_array.values()))
            # Listbox for rooms
            room_lb = Listbox(self.master, font=FONT_SERVICES, name='room_list', selectmode="SINGLE")
            if w == -1:
                for room in self.all_valid_serv:
                    room_lb.insert(tk.END, room)
            else:
                floor_array = self.json_file_dict["service_group"][0][self.service_array[w]][0]
                list_services = flatten(list(floor_array.values()))
                for room in list_services:
                    room_lb.insert(tk.END, room)
            room_lb.grid(column=1, row=0, sticky='nwse', padx=0, pady=2)

            # Code for eventual scrollbar
            #lb_scroll = Scrollbar(room_lb, orient=VERTICAL)
            #lb_scroll.grid(column=2,sticky="ns")
            #room_lb.config(yscrollcommand=lb_scroll.set)
            #lb_scroll.config(command=room_lb.yview)
            # room_lb.delete(0,END)
            # for room in list_services:
            #     room_lb.insert(tk.END, room)
            room_lb.bind('<Double-1>', self.service_confirmation)
            self.master.mainloop()
                
        #print("Start button pressed")
        # Create new page
        page1 = Tk()
        page1.configure(background="white")
        #page1.geometry(self.SCREEN_DIMENSION)
        page1.geometry("%dx%d" % (page1.winfo_screenwidth(), page1.winfo_screenheight()))
        page1.title('Select Service')
        #page1.geometry(self.SCREEN_DIMENSION)
        # Escape sequence for fullscreen mode
        page1.focus_set()
        page1.grid_columnconfigure(1, weight=5)
        #page1.state('zoomed')
        page1.bind("<Escape>", lambda e: page1.quit())
        self.master.destroy()
        self.master = page1
        self.sel_service = "All services"

        # Listbox for services
        services_lb = tk.Listbox(page1, height = len(self.service_array)+1, width = 10, font=FONT, name='service_list')
        # Include an "all services" category with all reachable services
        services_lb.insert(tk.END, "All services")
        for item in self.service_array:
            services_lb.insert(tk.END, item)
        services_lb.grid(column=0, row=0, sticky='nw', padx=0, pady=2)
        services_lb.bind('<<ListboxSelect>>', onselect)
        services_lb.select_set(0)
        room_lb = Listbox(self.master, font=FONT_SERVICES, name='room_list', selectmode="SINGLE")
        for room in self.all_valid_serv:
            room_lb.insert(tk.END, room)
        room_lb.grid(column=1, row=0, sticky='nwse', padx=0, pady=2)
        room_lb.bind('<Double-1>', self.service_confirmation)
        self.master.mainloop()
<<<<<<< HEAD

    async def repaint(self,nav_page: Tk, start, goal, user_position, end):
    
        before_stairs = []
        after_stairs = []
        node_path = []
        dest_id = "Third Floot Bathroom_a" ##stub data
        user_location = [0,0,0]
        user_grid_location = [0,0,0]
        #SEPARATE START AND GOAL INTO BEFORE STAIRS AND AFTER STAIRS
        #BEFORE_STAIRS = lines_before_stairs(start,goal)
        #AFTER_STAIRS = lines_after_stairs(start,goal)
        startingFloor = self.bfs.nodes[start[0]]["location"][2]
        twoFloors = False
        for i in range(len(start)):
            #if floors are different
            if self.bfs.nodes[start[i]]["location"][2] != self.bfs.nodes[goal[i]]["location"][2] and not twoFloors:
                before_stairs = after_stairs
                after_stairs = []
                #after_stairs.append(nodeId)
                twoFloors = True
            else:
                after_stairs.append([self.bfs.nodes[start[i]]["location"],self.bfs.nodes[goal[i]]["location"]])

        if len(after_stairs) != 0:
            after_stairs.append([after_stairs[len(after_stairs) - 1][1],end])
        else:
            after_stairs.append([self.bfs.nodes[goal[len(goal) - 1]]["location"],end])

        if twoFloors:
            before_stairs.insert(0,[(user_position[0], user_position[1], startingFloor), before_stairs[0][0]])
        else:
            after_stairs.insert(0,[(user_position[0], user_position[1], startingFloor), after_stairs[0][0]])

        #NEED USER POSITION = NEAREST_NODE_ID
        # nearest_node = self.bfs.find_nearest_node_feet()
        # nearest_node_location = self.bfs.nodes[nearest_node]["location"]
        # floor = nearest_node_location[2]

        self.draw_path(nav_page, before_stairs, after_stairs)
        while True:
            dest_id = "Third Floot Bathroom_a" ##stub data
            
            #GET USER ORIENTATION FROM IMU (SHARED DATA)
            orientation = sharedData.get_orientation()
            
            #GET DIRECTION OF MOVEMENT FROM IMU (INCOMPLETE RIGHT NOW)

            #GET USER LOCATION FROM NAVIGATION (SHARED DATA)
            user_location = sharedData.get_estimated_location()


            #CONVERT USER POSITION TO GRID SPACE
            user_location_grid_tra = (self.bfs.feet_to_node_units(user_location[0], user_location[1])[0], self.bfs.feet_to_node_units(user_location[0], user_location[1])[1], user_location[2])
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
                    for i in self.bfs.nodes:
                        if user_grid_location == self.bfs.nodes[i]["location"]:
                            if b:
                                before_stairs.insert(0, [self.bfs.nodes[i]["location"],before_stairs[0][0]])
                            else:
                                after_stairs.insert(0, [self.bfs.nodes[i]["location"],after_stairs[0][0]])

                    #ADD NODE TO THE PATH WITH (LEN(GOAL) - 1) INTO LEN(START) AND NEW NODE INTO LEN(GOAL)
                    
                #THEN, REDRAW
            

            #POSSIBLE LATER
                #IF THE USER IMAGE HAS A DIRECTION IT CAN FACE
                    #REDRAW WHEN IMU ORIENTATION CHANGES BY INCREMENTS OF 15 DEGREES
                    #THIS MEANS ONLY REDRAW WHEN IMU ORIENTATION CLOSEST ANGLE IS A DIFFERENT MULTIPLE OF 15 DEGREES


            #hey

            nav_page.update()
            time.sleep(2)
  
    # THIRD PAGE FOR ACTUAL NAVIGATION
    # HERE THE CODE TO COMMUNICATE BETWEEN THE SELECTED SERVICE AND THE BLUETOOTH CODE
    async def start_navigation(self, goal: StringVar):
        #stubd data. Must be updated
        user_location_feet = (-6, 78, 0)
        user_node = self.bfs.feet_to_node_units(user_location_feet[0], user_location_feet[1])


        dest_id = "Basement Bathroom"
        preference = "stairs"

        self.master.destroy()
        nav_page = Tk()
        # self.navigation_thread = threading.Thread(target=runNavigation, args=(self.manager,))
        # self.navigation_thread.start()
        sharedData.start_navigation()
        # runNavigation(self.manager))s

=======
       
    # THIRD PAGE FOR ACTUAL NAVIGATION
    # HERE THE CODE TO COMMUNICATE BETWEEN THE SELECTED SERVICE AND THE BLUETOOTH CODE
    def start_navigation(self, goal: StringVar):
        self.master.destroy()
        nav_page = Tk()
>>>>>>> UI
        nav_page.title('Wayfinder')
        #nav_page.geometry(self.SCREEN_DIMENSION)
        nav_page.geometry("%dx%d" % (nav_page.winfo_screenwidth(), nav_page.winfo_screenheight()))
        self.master = nav_page
        mess = "Goal: "+ goal
        nav_label = Label(master= nav_page, text= "Wayfinder Navigation", font=FONT).pack()
        service_label = Label(master= nav_page, text= mess, font=FONT_SERVICES).pack()
        #nav_page.state('zoomed')
        #nav_page.focus_set()
        #label_mess = "Preview navigation to:"
        #label = ttk.Label(master= self.master, background= "White", text= label_mess, font=FONT)
        #label.pack()
        #label_ser = ttk.Label(master= self.master, background= "White", text= goal, font=FONT_SERVICES)
        #label_ser.pack()

        # Here the data coming from the beacon 
<<<<<<< HEAD
        start = [130,0]

        # Destination comes from JSON file and user selection
        #eleveator pixel origin (130,400)
        goal = [130, 403]
        
        end_location = self.bfs.find_destination_by_id(dest_id, self.bfs.endpoints)
        nearest_node_id = self.bfs.find_nearest_node_feet(user_location_feet, self.bfs.nodes)
        nodePath = self.bfs.find_path(user_location_feet, dest_id, self.bfs.nodes, self.bfs.graph, self.bfs.endpoints, preference)
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
            locations[nodePath[i]] = self.bfs.nodes[nodePath[i]]["location"]


        
        self.repaint(nav_page, start, goal, user_node, end_location)
        #draw_path(nav_page, start, goal)
        nav_page.mainloop()

    # DEVELOPER MODE TO CHECK ON EMITTERS FUNCTIONALITIES
    async def developer_mode(self):
        dev_page = Tk()
        dev_page.configure(background="white")
        dev_page.geometry("%dx%d" % (dev_page.winfo_screenwidth(), dev_page.winfo_screenheight()))
        dev_page.title('Insert Password for Developer Mode')
        #dev_page.state('zoomed')
        self.master.destroy()
        self.master = dev_page
        pass_frame = Frame(master=dev_page, bg="white")
        pass_frame.pack(side = TOP)
        input_text = StringVar()




        self.master.mainloop()

    # Pop-up message to select stairs over elevator
    async def stairs_or_el(self):
=======
        start = [0,0]
        goal = [40, 550]

        self.draw_path(nav_page, start, goal)

        nav_page.mainloop()
    
    # DEVELOPER MODE TO CHECK ON EMITTERS FUNCTIONALITIES
    def developer_mode(self):
        #self.input_text = StringVar()
        #self.input_text.set("")
        #dev_page = tk.Tk()
        #dev_page.configure(background="white")
        #dev_page.geometry("%dx%d" % (dev_page.winfo_screenwidth(), dev_page.winfo_screenheight()))
        #dev_page.title('Insert Password for Developer Mode')
        #dev_page.state('zoomed')
        self.master.destroy()
        passcode_entry = PasscodeEntry(self)
        self.master.mainloop()
        """ self.passcode_entry = tk.Entry(dev_page, textvariable=self.input_text, show='*', font=("Arial", 14))
        self.passcode_entry.grid(row=1, column=0, rowspan=2, columnspan=3, pady=10)
        #input_field = Entry(pass_frame, font = ('arial', 18, 'bold'), textvariable = self.input_text, justify = CENTER)
        #input_field.pack()
        #btns_frame = Frame(dev_page, width = dev_page.winfo_screenwidth(), bg = "grey")

        clear = Button(dev_page, text = "Clear", width=15, height = 5, command = lambda: self.btn_clear(),font='Calibri 12').grid(row = 3, column = 0)
        enter = Button(dev_page, text = "Enter", width=15, height = 5, command = lambda: self.btn_enter(),font='Calibri 12').grid(row = 3, column = 2)
        b1 = Button(dev_page, text='1', width=15, height = 5, command= lambda:   lambda: self.btn_click('1'),font='Calibri 12').grid(row = 0, column = 0)
        b2 = Button(dev_page, text='2', width=15, height = 5, command=  lambda: self.btn_click('2'),font='Calibri 12').grid(row = 0, column = 1)
        b3 = Button(dev_page, text='3', width=15, height = 5, command=  lambda: self.btn_click('3'), font='Calibri 12').grid(row = 0, column = 2)
        b4 = Button(dev_page, text='4', width=15, height = 5, command=  lambda: self.btn_click('4'), font='Calibri 12').grid(row = 1, column = 0)
        b5 = Button(dev_page, text='5', width=15, height = 5, command=  lambda: self.btn_click('5'), font='Calibri 12').grid(row = 1, column = 1)
        b6 = Button(dev_page, text='6', width=15, height = 5,  command=  lambda: self.btn_click('6'), font='Calibri 12').grid(row = 1, column = 2)
        b7 = Button(dev_page, text='7', width=15, height = 5, command=  lambda: self.btn_click('7'), font='Calibri 12').grid(row = 2, column = 0)
        b8 = Button(dev_page, text='8', width=15, height = 5,  command=  lambda: self.btn_click('8'),font='Calibri 12').grid(row = 2, column = 1)
        b9 = Button(dev_page, text='9', width=15, height = 5, command=  lambda: self.btn_click('9'),font='Calibri 12').grid(row = 2, column = 2)
        b0 = Button(dev_page, text='0', width=15, height = 5, command=  lambda: self.btn_click('0'),font='Calibri 12').grid(row = 3, column = 1)
        #dev_page.pack()

        self.master.mainloop() """

    # Pop-up message to select stairs over elevator
    def stairs_or_el(self):
>>>>>>> UI
        self.stairs = messagebox.askyesnocancel(title = "Preference", message="Stairs or Elevator? \nYes: Stairs, No: Elevator")
        if self.stairs is not None:
            self.select_service()

<<<<<<< HEAD
    async def service_confirmation(self, args: Event):
=======
    def service_confirmation(self, args: Event):
>>>>>>> UI
        if not args.widget.curselection():
            return
        if not self.selected:
            self.selected = True
            idx = args.widget.curselection()[0]
            if self.sel_service != "All services":
                floor_services_flat= flatten(list(self.json_file_dict["service_group"][0][self.sel_service][0].values()))
                # Getting rid of None values from json file
                serv_not_none = list(filter(None,floor_services_flat))
                sel_service = serv_not_none[idx]
            else:
                # If selected from the "All services" list
                sel_service = self.all_valid_serv[idx]
            print(sel_service)
            mess= "Selected service: \""
            mess = mess + str(sel_service)
            mess = mess + "\". \nWould you like to proceed?"
            selection = messagebox.askyesno(title="Service confirmation", message=mess, parent=self.master)
            if selection:
                self.start_navigation(sel_service)
            else:
                self.selected = False
<<<<<<< HEAD
    
    # Function that draws lines for directions to follow
    async def draw_path(self,page: Tk, before_stairs, after_stairs):
        #screen = Canvas(page, width= 600, height=550, background="black")
        # screen.pack(anchor='nw', fill='both', expand=1)

        # NEED TO CLEAR THE SCREEN HERE FIRST
=======
    def btn_clear(self):
        self.input_text.set("")

    def btn_click(self, item):
        self.input_text.set(self.input_text.get() + item)

    def btn_enter(self):
        # Write code for passcode check
        print(self.passcode_entry.get())



    # Function that draws lines for directions to follow
    def draw_path(page: Tk, start, goal):
        #screen = Canvas(page, width= 600, height=550, background="black")
        # screen.pack(anchor='nw', fill='both', expand=1)
        # https://www.youtube.com/watch?v=5V_cPy2dtTc
>>>>>>> UI

        w = page.winfo_screenwidth()
        h = page.winfo_screenheight()
        screen = Canvas(master=page, width=w, height=h)
        screen.pack(anchor="center")
<<<<<<< HEAD
        if(len(before_stairs) != 0):
            img_floor = Image.open("flr" + str(before_stairs[0][0][2]) + "_larger.jpg")
        else:  
            img_floor = Image.open("flr" + str(after_stairs[0][0][2]) + "_larger.jpg")
=======
        img_floor = Image.open("flr4.jpg")
>>>>>>> UI
        img_floor = ImageOps.exif_transpose(img_floor)
        width, height = int(img_floor.width / 2), int(img_floor.height / 2) 
        img = img_floor.resize((width,height), Image.Resampling.LANCZOS)#.rotate(-90)
        screen.configure(background="white", width=img.width, height=height)
        img_tk = ImageTk.PhotoImage(img)
        screen.image = img_tk
        #img_floor = img_floor.resize((500,500), Image.ANTIALIAS)
        # Play with position
        screen.create_image(0,0, image= img_tk, anchor= "nw")
        #screen.create_line(start[0],start[1],goal[0], goal[1], fill="red", width = 3)
<<<<<<< HEAD
        page.update()
        
        if len(before_stairs) != 0:
            for i in range(0,len(before_stairs),1):
                screen.create_line(grid2Pixel(before_stairs[i][0][0:2],before_stairs[i][0][2])[0],
                               grid2Pixel(before_stairs[i][0][0:2],before_stairs[i][0][2])[1],
                               grid2Pixel(before_stairs[i][1][0:2],before_stairs[i][1][2])[0],
                               grid2Pixel(before_stairs[i][1][0:2],before_stairs[i][1][2])[1],
                               fill="blue", width = 3)
        else:
            for i in range(0,len(after_stairs),1):
                screen.create_line(grid2Pixel(after_stairs[i][0][0:2],after_stairs[i][0][2])[0],
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
    

    async def close(self):
        sharedData.closing = True
        self.mpu_thread.join()
        if self.navigation_thread != None:
            self.navigation_thread.join()
        self.manager.close()
        
        


def grid2Pixel(inp,floor):
    if(floor == 0):
        return [(inp[0] * PIXELS_PER_GRID_FLOOR_B_X) + ELEVATOR_PIXEL_X_FLOOR_B + (PIXELS_PER_GRID_FLOOR_B_X / 2), ELEVATOR_PIXEL_Y_FLOOR_B - (inp[1] * PIXELS_PER_GRID_FLOOR_B_Y) - (PIXELS_PER_GRID_FLOOR_B_Y / 2)]
    elif(floor == 1):
        return [(inp[0] * PIXELS_PER_GRID_FLOOR_1_X) + ELEVATOR_PIXEL_X_FLOOR_1 + (PIXELS_PER_GRID_FLOOR_1_X / 2), ELEVATOR_PIXEL_Y_FLOOR_1 - (inp[1] * PIXELS_PER_GRID_FLOOR_1_Y) - (PIXELS_PER_GRID_FLOOR_1_Y / 2)]
    elif(floor == 2):
        return [(inp[0] * PIXELS_PER_GRID_FLOOR_2_X) + ELEVATOR_PIXEL_X_FLOOR_2 + (PIXELS_PER_GRID_FLOOR_2_X / 2), ELEVATOR_PIXEL_Y_FLOOR_2 - (inp[1] * PIXELS_PER_GRID_FLOOR_2_Y) - (PIXELS_PER_GRID_FLOOR_2_Y / 2)]
    elif(floor == 3):
        return [(inp[0] * PIXELS_PER_GRID_FLOOR_3_X) + ELEVATOR_PIXEL_X_FLOOR_3 + (PIXELS_PER_GRID_FLOOR_3_X / 2), ELEVATOR_PIXEL_Y_FLOOR_3 - (inp[1] * PIXELS_PER_GRID_FLOOR_3_Y) - (PIXELS_PER_GRID_FLOOR_3_Y / 2)]
    elif(floor == 4):
        return [(inp[0] * PIXELS_PER_GRID_FLOOR_4_X) + ELEVATOR_PIXEL_X_FLOOR_4 + (PIXELS_PER_GRID_FLOOR_4_X / 2), ELEVATOR_PIXEL_Y_FLOOR_4 - (inp[1] * PIXELS_PER_GRID_FLOOR_4_Y) - (PIXELS_PER_GRID_FLOOR_4_Y / 2)]
    else:
        return [(inp[0] * PIXELS_PER_GRID_FLOOR_5_X) + ELEVATOR_PIXEL_X_FLOOR_5 + (PIXELS_PER_GRID_FLOOR_5_X / 2), ELEVATOR_PIXEL_Y_FLOOR_5 - (inp[1] * PIXELS_PER_GRID_FLOOR_5_Y) - (PIXELS_PER_GRID_FLOOR_5_Y / 2)]
    

def flatten(list_of_list):
    if isinstance(list_of_list, list):
        fin_list = []
        for el in list_of_list:
            fin_list.extend(flatten(el))
        return fin_list
    else:
        return [list_of_list]
async def runNavigation(manager):
    await asyncio.sleep(5)
    # while not sharedData.closing:
        # while sharedData.navigation_started and not sharedData.closing:
    while(True):
            # await asyncio.sleep(.1)
            
            closest_beacons = manager.get_closest()
            all_beacons = manager.get_beacons()
            if manager.closest_full():
                print("********************************FULL*************************************************")
                print(f"Beacons: {all_beacons}")
                print(f"Closest Beacons: {closest_beacons}")    
                print("Entering localization")
                location = await tra_localization(closest_beacons,EMITTER_LOC_DICT)
                with sharedData.lock:
                    sharedData.estimated_location = location
                with open('locationData','a') as file:
                        file.write(f'Estimated Location: {location}\n')
                manager.clear_closest()
            else:
                # print("not full\n")
                pass
            
=======
        page.mainloop()


class PasscodeEntry:
    def __init__(self, ui: Wayfinder_UI):
        self.root = Tk()
        self.root.configure(background="white")
        self.root.geometry("%dx%d" % (self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        self.root.title('Insert Password for Developer Mode')
        passcode_frame = Frame(master=self.root, bg="white")
        self.master = passcode_frame
        ui.master = self.root
        #self.master.title("Passcode Entry")
        self.passcode = tk.StringVar()
        self.passcode.set("")
        self.enter = False      # True when Enter is pressed
        self.right_wrong_label = tk.Label(self.root, text = "")
        
        self.entry_label = tk.Label(self.master, text="Enter Passcode:")
        self.entry_label.grid(row=0, column=0, columnspan=3)

        self.passcode_entry = tk.Entry(self.master, textvariable=self.passcode, show='*', font=("Arial", 14))
        self.passcode_entry.grid(row=1, column=0, columnspan=3, pady=10)

        self.keypad_buttons = [
            '1', '2', '3',
            '4', '5', '6',
            '7', '8', '9',
        ]

        row_num = 2
        col_num = 0
        for key in self.keypad_buttons:
            button = tk.Button(self.master, text=key, width=5, height=2, command=lambda key=key: self.update_passcode(key))
            button.grid(row=row_num, column=col_num, padx=5, pady=5)
            col_num += 1
            if col_num > 2:
                col_num = 0
                row_num += 1
        
        
        self.clear_button = tk.Button(self.master, text="Clear", width=5, height=2, command=self.clear_passcode)
        self.clear_button.grid(row=row_num, column=0, padx=5, pady=5)
        zero_button = tk.Button(self.master, text='0', width=5, height=2, command=lambda key=key: self.update_passcode('0'))
        zero_button.grid(row=row_num, column=1, padx=5, pady=5)
        self.enter_button = tk.Button(self.master, text="Enter", width=5, height=2, command=self.enter_passcode)
        self.enter_button.grid(row=row_num, column=2, padx=5, pady=5)
        self.master.pack()

    def update_passcode(self, key):
        if not self.enter:
            self.passcode.set(self.passcode.get() + key)

    def clear_passcode(self):
        self.passcode.set("")
        self.enter = False

    def enter_passcode(self):
        print("Passcode entered:", self.passcode.get())
        #self.right_label = tk.Label(self.root, text = "Right passcode!").pack()
        if self.passcode.get() == str(3054):
            self.right_wrong_label.configure(text="Right passcode!")
            self.enter = True
        else:
            self.right_wrong_label.configure(text="Wrong passcode!")
        self.right_wrong_label.pack()
        self.passcode.set("")



if __name__ == '__main__': 
    # Read json file for services and rooms 
    services_filename = open("services.json")
    nodes_filename = open("node.json")
    services_json = json.load(services_filename)
    nodes_json = json.load(nodes_filename)
    # Call Wayfinder UI
    wayfinder = Wayfinder_UI(services_json, nodes_json)
>>>>>>> UI
