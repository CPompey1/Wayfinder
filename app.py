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
from MPU.run_mpu import MpuClass
from globals import *
from BeaconManager import BeaconManager
if not SIMULATION: from MPU.run_mpu import runMpu
from globals import EMITTER_LOC_DICT
from tra_localization import tra_localization


FONT = "Calibri 26 bold"
FONT_SERVICES = "Calibri 15"
SCREEN_DIMENSION = "768x1024"


class Wayfinder_UI(threading.Thread):
    global service_array
    def __init__(self, file):
    # MAIN PAGE FOR WELCOME
    # Change this based on display dimensions
        super().__init__()
        #initliize beacon manager and threads
        self.manager = BeaconManager()
        self.manager.initialize_scanning()
        self.bfs = BFS()
        self.navigation_thread = None
        self.mpu = MpuClass()
        if not SIMULATION: 
            self.mpu_thread = threading.Thread(target=runMpu, daemon=True)
            self.mpu_thread.start()
        else:
            self.mpu_thread = threading.Thread(target=sim_mpu, daemon=True)
            self.mpu_thread.start()
        
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
        window = Tk()
        window.title('Wayfinder')
        #window.focus_set()
        window.geometry("%dx%d" % (window.winfo_screenwidth(), window.winfo_screenheight()))
        #window.state('zoomed')
        #window.geometry(self.SCREEN_DIMENSION)
        self.sel_service = "Second Floor Elevator"

        window.bind("<Escape>", lambda e: window.quit())
        # self.master = window
        self.master = window
        title_label = Label(master= self.master, text= "Welcome to Lockwood Wayfinder!", font=FONT).pack()
        img = ImageTk.PhotoImage(Image.open("lockwood_main.jpg"))
        panel = Label(window, image=img)
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
        self.master.mainloop()

    # SECOND PAGE FOR SERVICE SELECTION
    # https://www.youtube.com/watch?v=wFyzmZVKPAw    useful video for multiple pages layout
            
    def select_service(self):
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
       
    # THIRD PAGE FOR ACTUAL NAVIGATION
    # HERE THE CODE TO COMMUNICATE BETWEEN THE SELECTED SERVICE AND THE BLUETOOTH CODE
    def start_navigation(self, goal: StringVar):
        #stubd data. Must be updated
        user_location_feet = (45, 65, 1)
        dest_id = "Third Floor Bathroom_a"
        preference = "stairs"

        self.master.destroy()
        nav_page = Tk()
        self.navigation_thread = threading.Thread(target=runNavigation, args=(self.manager,))
        self.navigation_thread.start()
        # runNavigation(self.manager))s

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
        start.append(self.bfs.nodes[nearest_node_id]["location"][0:2])
        goal.append(self.bfs.nodes[nodePath[0]]["location"][0:2])
        for i in range(len(nodePath)):
            if i < len(nodePath) - 1:
                start.append(self.bfs.nodes[nodePath[i]]["location"][0:2])
                goal.append(self.bfs.nodes[nodePath[i+1]]["location"][0:2])
            locations[nodePath[i]] = self.bfs.nodes[nodePath[i]]["location"]

        
        repaint(nav_page, start, goal)
        #draw_path(nav_page, start, goal)
        nav_page.mainloop()

    # DEVELOPER MODE TO CHECK ON EMITTERS FUNCTIONALITIES
    def developer_mode(self):
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
    def stairs_or_el(self):
        self.stairs = messagebox.askyesnocancel(title = "Preference", message="Stairs or Elevator? \nYes: Stairs, No: Elevator")
        if self.stairs is not None:
            self.select_service()

    def service_confirmation(self, args: Event):
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
    def close(self):
        sharedData.closing = True
        self.mpu_thread.join()
        if self.navigation_thread != None:
            self.navigation_thread.join()
        self.manager.close()
        
        
# Function that draws lines for directions to follow
def draw_path(page: Tk, start, goal):
    #screen = Canvas(page, width= 600, height=550, background="black")
    # screen.pack(anchor='nw', fill='both', expand=1)

    # NEED TO CLEAR THE SCREEN HERE FIRST

    w = page.winfo_screenwidth()
    h = page.winfo_screenheight()
    screen = Canvas(master=page, width=w, height=h)
    screen.pack(anchor="center")
    img_floor = Image.open("flr4.jpg")
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
    page.update()
    
    #start1 = [150,0]
    for i in range(0,len(start),1):
        screen.create_line(grid2Pixel(start[i])[0] - 50,grid2Pixel(start[i])[1] + 100,grid2Pixel(goal[i])[0] - 50,grid2Pixel(goal[i])[1] + 100, fill="blue", width = 3)

    # Destination comes from JSON file and user selection
    #eleveator pixel origin (130,403)
    #goal1 = [150, 400]
    box0s = [130, 403]
    box0e = [130, 387]
    box1s = [130, 403]
    box1e = [146, 403]
    box2s = [146, 403]
    box2e = [146, 387]
    box3s = [146, 387]
    box3e = [130, 387]
    #screen.create_line(start1[0],start1[1],goal1[0], goal1[1], fill="red", width = 3)
    line_start = grid2Pixel([0,0])
    line_stop = grid2Pixel([2,2])
    screen.create_line(line_start[0],line_start[1],line_stop[0],line_stop[1], fill="green", width = 3)
   
    screen.create_line(box0s[0],box0s[1],box0e[0],box0e[1], fill="red", width = 3)
    screen.create_line(box1s[0],box1s[1],box1e[0],box1e[1], fill="red", width = 3)
    screen.create_line(box2s[0],box2s[1],box2e[0],box2e[1], fill="red", width = 3)
    screen.create_line(box3s[0],box3s[1],box3e[0],box3e[1], fill="red", width = 3)

def repaint(nav_page: Tk, start, goal):
    
    #SEPARATE START AND GOAL INTO BEFORE STAIRS AND AFTER STAIRS
    #BEFORE_STAIRS = lines_before_stairs(start,goal)
    #AFTER_STAIRS = lines_after_stairs(start,goal)
    #NEED USER POSITION = NEAREST_NODE_ID

    draw_path(nav_page, start, goal)
    while True:
        nav_page.update()
        time.sleep(2)

        #GET USER ORIENTATION FROM IMU (SHARED DATA)
        #GET DIRECTION OF MOVEMENT FROM IMU (INCOMPLETE RIGHT NOW)

        #GET USER LOCATION FROM NAVIGATION (SHARED DATA)

        #CONVERT USER POSITION TO GRID SPACE

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

            #USERPOSITION = CURRENT USER POSITION
            #IF BEFORE STAIRS IS NOT EMPTY
                #PATH OF NODES = BEFORE STAIRS
            #ELSE
                #PATH OF NODES = AFTER STAIRS       #AFTER STAIRS SHOULD ONLY START AFTER REACHING THE NEXT FLOOR
                
            #LOOP THROUGH PATH OF NODES AND CHECK AGAINST POSITIONS
                #IF CURRENT USER POSITION EXISTS IN PATH
                    #REMOVE THE NODE FROM THE PATH (START AND GOAL VARIABLES LEN - 1)
                #ELSE IF CURRENT USER POSITION EXISTS IN LIST OF ALL NODES IN THE CURRENT FLOOR
                    #ADD NODE TO THE PATH WITH (LEN(GOAL) - 1) INTO LEN(START) AND NEW NODE INTO LEN(GOAL)
        
            #THEN, REDRAW
        

        #POSSIBLE LATER
            #IF THE USER IMAGE HAS A DIRECTION IT CAN FACE
                #REDRAW WHEN IMU ORIENTATION CHANGES BY INCREMENTS OF 15 DEGREES
                #THIS MEANS ONLY REDRAW WHEN IMU ORIENTATION CLOSEST ANGLE IS A DIFFERENT MULTIPLE OF 15 DEGREES


        #hey
def grid2Pixel(inp,floor):
    return [(inp[0] * PIXELS_PER_GRID_FLR4) + ELEVATOR_PIXEL_X_FLR4, ELEVATOR_PIXEL_Y_FLR4- (inp[1] * PIXELS_PER_GRID_FLR4) ]

def flatten(list_of_list):
    if isinstance(list_of_list, list):
        fin_list = []
        for el in list_of_list:
            fin_list.extend(flatten(el))
        return fin_list
    else:
        return [list_of_list]

def runNavigation(manager):
    while True and not sharedData.closing:
        closest_beacons = manager.get_closest()
        if not None in closest_beacons:
            print("Entering localization")
            location = tra_localization(closest_beacons,EMITTER_LOC_DICT)
            with sharedData.lock:
                sharedData.estimated_location = location
            manager.clear_closest()
            print("********************************FULL*************************************************")
        else:
            # print("not full\n")
            pass

async def main():
    # Read json file for services and rooms 
    filename = open("services.json")
    services_from_jason = json.load(filename)
    #print(services_from_jason)
    # Call Wayfinder UI
    wayfinder = Wayfinder_UI(services_from_jason)
    wayfinder.close()

asyncio.run(main())
