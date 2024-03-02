from tkinter import *
from tkinter import ttk
from tkinter import messagebox
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
        window.focus_set()
        window.bind("<Escape>", lambda e: window.quit())
        self.master = window
        title_label = ttk.Label(master= self.master, text= "Welcome to Lockwood Wayfinder!", font=FONT)
        title_label.pack()
        img = ImageTk.PhotoImage(Image.open("lockwood_main.jpg"))
        panel = Label(window, image=img)
        panel.pack()
        start_frame = ttk.Frame(master=self.master)
        start_button = ttk.Button(master=start_frame, text= "Start Navigating", command = self.stairs_or_el)
        start_button.pack(side = 'left')
        start_frame.pack(pady=10)
        dev_mode_frame = ttk.Frame(master=self.master)
        dev_mode_button = ttk.Button(master=dev_mode_frame, text= "Developer Mode", command = self.developer_mode)
        dev_mode_button.pack(side = 'left')
        dev_mode_frame.pack(pady=10)
        self.selected = False
        self.master.mainloop()

    # SECOND PAGE FOR SERVICE SELECTION
    # https://www.youtube.com/watch?v=wFyzmZVKPAw    useful video for multiple pages layout
    
            
    def select_service(self):
        global services_list
        global room_frame

        # Creating Treeview for all services
        def onselect(evt: Event):
            if not evt.widget.curselection():
                return
            try: 
                room_frame.Destroy()
            except:
            #lbl = ttk.Label(c, text="Service Room/Floor")
            # Note here that Tkinter passes an event object to onselect()
                w = evt.widget.curselection()[0] # Number from 0 to n number of services categories
                self.select_service = str(services_list.get(services_list.curselection()))
                #print(self.select_service)
                room_frame = ttk.Frame(page1, padding=(5,5,12,0))
                room_frame.grid(column=1, row=0, sticky='nsw')
                floor_array = {}
                # Side menu depending on selected service
                try:
                    match w:
                        case 0:
                            floor_array = self.json_file_dict["service_group"][0][self.service_array[0]][0]
                        case 1:
                            floor_array = self.json_file_dict["service_group"][0][self.service_array[1]][0]
                        case 2:
                            floor_array = self.json_file_dict["service_group"][0][self.service_array[2]][0]
                        case 3:
                            floor_array = self.json_file_dict["service_group"][0][self.service_array[3]][0]
                        case 4:
                            floor_array = self.json_file_dict["service_group"][0][self.service_array[4]][0]
                        case 5:
                            floor_array = self.json_file_dict["service_group"][0][self.service_array[5]][0]
                        case 6:
                            floor_array = self.json_file_dict["service_group"][0][self.service_array[6]][0]
                except:
                    # If no services are available for the selected category
                    print("No services for this category")
                
                list_services = flatten(list(floor_array.values()))
                #print(list_services)

                # FIX HEIGHT TO BE PRETTY PRETTIER
                room_list = Listbox(room_frame, height=13, font=FONT_SERVICES,  width=50, name='room_list', selectmode="SINGLE") #, width=10, height=1024)
                room_row = 0
                floor_ind = 0 

                for room in list_services:
                    if room is not None:
                        room_list.insert(room_row, room)
                        room_row += 1
                    else:
                        floor_ind += 1 
                        # Might use this to differentiate between floors later...
                        #room_list.insert(room_row, "No services on this floor")
                        room_row += 1



                '''for floor_groups in list_services:
                    if floor_groups is not None:
                        print("Floor groups", floor_groups)
                        for room in floor_groups:
                            #print("room", room)
                            if room is not None:
                                #print("Room", room)
                                room_list.insert(room_row, room)
                                room_row += 1
                            else: 
                                room_list.insert(room_row, "No services on this floor")
                                room_row += 1
                '''
                room_list.bind('<Double-1>', self.service_confirmation)
                room_list.grid(column=1, row=0, sticky='nse')
            self.master.mainloop()
                
        #print("Start button pressed")
        # Create new page
        page1 = Tk()
        page1.title('Select Service')
        page1.geometry(SCREEN_DIMENSION)
        # Escape sequence for fullscreen mode
        page1.focus_set()
        page1.grid_columnconfigure(0, weight=1)
        page1.grid_columnconfigure(1, weight=5)
        page1.bind("<Escape>", lambda e: page1.quit())
        self.master.destroy()
        #self.master = page1
        # Create title label
        #title_label = ttk.Label(master= self.master, text= "Select the Service", font=FONT)
        #title_label.pack()
        # Create Frame for services
        services_frame = ttk.Frame(page1, padding=(5, 5, 12, 0))
        services_frame.grid(column=0, row=0, sticky='nsw')
        room_frame = ttk.Frame(page1, padding=(5,5,12,0))
        room_frame.grid(column=1, row=0)#, sticky='nse')
        services_list = Listbox(services_frame, height = len(self.service_array), width=10, font=FONT, name='service_list') #, width=10, height=1024)
        #services_frame.grid(column=0, row=0, sticky='nsw')
        
        # https://www.youtube.com/watch?v=IJ-iVnN09-8
        services_list.bind('<<ListboxSelect>>', onselect)
        row = 0
        for service in self.service_array:
            services_list.insert(row, service)
            row += 1
        services_list.grid(column=0, row=0, sticky='nsw')
        self.master = page1
        # Good so far
        
       
    # THIRD PAGE FOR ACTUAL NAVIGATION
    # HERE THE CODE TO COMMUNICATE BETWEEN THE SELECTED SERVICE AND THE BLUETOOTH CODE
    def start_navigation(self, goal: StringVar):
        nav_page = Tk()
        nav_page.title('Wayfinder')
        nav_page.geometry(SCREEN_DIMENSION)
        nav_page.focus_set()
        self.master.destroy()
        self.master = nav_page
        label_mess = "Preview navigation to:"
        label = ttk.Label(master= self.master, background= "White", text= label_mess, font=FONT)
        label.pack()
        label_ser = ttk.Label(master= self.master, background= "White", text= goal, font=FONT_SERVICES)
        label_ser.pack()

        img_floor = ImageTk.PhotoImage(Image.open("floor_2.jpg"))
        panel1 = Label(master=self.master, image=img_floor)
        panel1.pack()
        self.master.mainloop()



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
            floor_services_flat= flatten(list(self.json_file_dict["service_group"][0][self.select_service][0].values()))
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


        
    



if __name__ == '__main__': 
    # Read json file for services and rooms 
    filename = open("services.json")
    services_from_jason = json.load(filename)
    #print(services_from_jason)
    # Call Wayfinder UI
    wayfinder = Wayfinder_UI(services_from_jason)


 
    

   




