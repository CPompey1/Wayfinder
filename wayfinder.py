from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import Canvas
import ttkbootstrap as ttkint
from PIL import ImageTk, Image
import json

FONT = "Calibri 28 bold"
FONT_SERVICES = "Calibri 15"
SCREEN_DIMENSION = "600x1024"
XDIMENSION = 600
YDIMENSION = 1024

def flatten(list_of_list):
    if isinstance(list_of_list, list):
        fin_list = []
        for el in list_of_list:
            fin_list.extend(flatten(el))
        return fin_list
    else:
        return [list_of_list]

class Wayfinder_UI:
    global service_array
    def __init__(self, file):
    # MAIN PAGE FOR WELCOME
    # Change this based on display dimensions
        self.json_file_dict: dict = file
        self.service_array = list(self.json_file_dict["service_group"][0].keys())
        self.stairs = True
        window = Tk()
        window.title('Wayfinder')
        window.geometry(SCREEN_DIMENSION)
        #window.focus_set()
        window.bind("<Escape>", lambda e: window.quit())
        self.master = window
        title_label = ttk.Label(master= self.master, text= "Welcome to Lockwood Wayfinder!", font=FONT)
        title_label.pack()
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
        self.sel_service = "Second Floor Elevator"

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
            w = evt.widget.curselection()[0] # Number from 0 to n number of services categories
            self.sel_service = str(services_lb.get(services_lb.curselection()))
            floor_array = {}
            # Side menu depending on selected service
            try:
                floor_array = self.json_file_dict["service_group"][0][self.service_array[w]][0]
                list_services = flatten(list(floor_array.values()))
            except:
                # If no services are available for the selected category
                print("No services for this category")
            list_services = flatten(list(floor_array.values()))
            # Listbox for rooms
            room_lb = Listbox(self.master, font=FONT_SERVICES, name='room_list', selectmode="SINGLE")
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
        page1.title('Select Service')
        page1.geometry(SCREEN_DIMENSION)
        # Escape sequence for fullscreen mode
        page1.focus_set()
        page1.grid_columnconfigure(1, weight=5)
        page1.bind("<Escape>", lambda e: page1.quit())
        self.master.destroy()
        self.master = page1

        # Listbox for services
        services_lb = tk.Listbox(page1, height = len(self.service_array), width = 10, font=FONT, name='service_list')
        for item in self.service_array:
            services_lb.insert(tk.END, item)
        services_lb.grid(column=0, row=0, sticky='nw', padx=0, pady=2)
        services_lb.bind('<<ListboxSelect>>', onselect)
        services_lb.select_set(0)

        # Good so far
        self.master.mainloop()
        
       
    # THIRD PAGE FOR ACTUAL NAVIGATION
    # HERE THE CODE TO COMMUNICATE BETWEEN THE SELECTED SERVICE AND THE BLUETOOTH CODE
    def start_navigation(self, goal: StringVar):
        self.master.destroy()
        nav_page = Tk()
        nav_page.title('Wayfinder')
        nav_page.geometry(SCREEN_DIMENSION)
        self.master = nav_page
        #nav_page.focus_set()
        #label_mess = "Preview navigation to:"
        #label = ttk.Label(master= self.master, background= "White", text= label_mess, font=FONT)
        #label.pack()
        #label_ser = ttk.Label(master= self.master, background= "White", text= goal, font=FONT_SERVICES)
        #label_ser.pack()
        start = [0,0]
        goal = [40, 550]
        draw_path(nav_page, start, goal)
        nav_page.mainloop()

 

    # DEVELOPER MODE TO CHECK ON EMITTERS FUNCTIONALITIES
    def developer_mode(self):
        pass
    # Pop-up message to select stairs over elevator
    def stairs_or_el(self):
        self.stairs = messagebox.askyesno(title = "Preference", message="Stairs?")
        self.select_service()
    def service_confirmation(self, args: Event):
        if not args.widget.curselection():
            return
        if not self.selected:
            self.selected = True
            idx = args.widget.curselection()[0]
            floor_services_flat= flatten(list(self.json_file_dict["service_group"][0][self.sel_service][0].values()))
            serv_not_none = []
            # Getting rid of None values from json file
            for el in floor_services_flat:
                if el is not None:
                    serv_not_none.append(el)
            sel_service = serv_not_none[idx]
            print(sel_service)
            mess= "Selected service: \""
            mess = mess + str(sel_service)
            mess = mess + "\". \nWould you like to proceed?"
            selection = messagebox.askyesno(title="Service confirmation", message=mess, parent=self.master)
            if selection:
                self.start_navigation(sel_service)
            else:
                self.selected = False

# Function that draws lines for directions to follow
def draw_path(page, start, goal):
    # screen = Canvas(self.master, width= 600, height=550, background="black")
    # screen.pack(anchor='nw', fill='both', expand=1)
    screen = Canvas(master=page, width=600, height=700)
    screen.configure(background="white")
    screen.pack(anchor="center")
    
    img_floor = ImageTk.PhotoImage(Image.open("floor_2.jpg"))
    # Play with position
    screen.create_image(0,0, image= img_floor, anchor= "nw")
    screen.create_line(start[0],start[1],goal[0], goal[1], fill="red", width = 3)
    page.mainloop()

        
    



if __name__ == '__main__': 
    # Read json file for services and rooms 
    filename = open("services.json")
    services_from_jason = json.load(filename)
    #print(services_from_jason)
    # Call Wayfinder UI
    wayfinder = Wayfinder_UI(services_from_jason)


 
    

   




