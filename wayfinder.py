from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import Canvas
import ttkbootstrap as ttkint
from PIL import ImageTk, Image, ImageOps
import json

FONT = "Calibri 26 bold"
FONT_SERVICES = "Calibri 15"
SCREEN_DIMENSION = "768x1024"

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
    def __init__(self, serv_file, nodes_file):
    # MAIN PAGE FOR WELCOME
    # Change this based on display dimensions
        self.json_file_dict: dict = serv_file
        self.nodes: dict = nodes_file
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
        self.stairs = True
        window = Tk()
        window.title('Wayfinder')
        #window.focus_set()
        window.geometry("%dx%d" % (window.winfo_screenwidth(), window.winfo_screenheight()))
        #window.state('zoomed')
        #window.geometry(self.SCREEN_DIMENSION)
        self.sel_service = "Second Floor Elevator"

        window.bind("<Escape>", lambda e: window.quit())
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
        self.master.destroy()
        nav_page = Tk()
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
