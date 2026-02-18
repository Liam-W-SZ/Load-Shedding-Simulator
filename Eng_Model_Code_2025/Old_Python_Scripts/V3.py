from tkinter import *
from PIL import Image,ImageTk #import images
from tkinter import simpledialog
from tkinter import messagebox
import numpy as np
import json
import tkinter as tk
import tkinter.messagebox
import time
import threading
import os
import platform

stop_event = threading.Event()

#import Main_ModBus_Script, time #exclude for now

root = Tk()

root.title('LSS - V1') # Give Title to Old Window GUI
#root.iconbitmap(r"/home/main/Desktop/Eng_Model_Code_2025/Jedi.ico") #download ico and place in same folder as script
#r"/home/main/Desktop/Eng_Model_Code_2025/SZ_Logo.png"
root.geometry("800x450") #Give Size to your widget
root.configure(background='white')


r_label=Label(root,text="Load Shedding Simulator",font=('Arial Black',20),bg='white',anchor='w')
r_label.place(x=330,y=40)

img1 = ImageTk.PhotoImage(Image.open(r"SZ_Logo.png"))

mylabel = Label(root,image=img1)
mylabel.grid(row=0,column=0)

# creating panels
frame1 = LabelFrame(root, padx=100,pady=100)
frame1.place(x=0, y=100, width=225.0, height=350)
frame1.configure(background='#2e1872')

#placing Frame 1 Label
f1_label=Label(frame1,text="Config Simulations",font=('Arial Black',12),bg='white',fg ='white',anchor='nw')
f1_label.configure(background='#2e1872')
f1_label.place(x=-70,y=-90)

#placing Frame 1 Second Label
f2_label=Label(frame1,text="Manual Simulations",font=('Arial Black',12),bg='white',fg ='white',anchor='nw')
f2_label.configure(background='#2e1872')
f2_label.place(x=-70,y=50)

#open Json file
with open("Load_Shedding_Config_File.json","r") as file:
    data = json.load(file)


#Adding Drop down Menu to Frame 1
OPTIONS = list(data.keys())

clicked = StringVar()
clicked.set(OPTIONS[0])

drop = OptionMenu(frame1,clicked,*OPTIONS) #this function creates drop down menu with all options listed above
drop.place(x=-50,y=-50,width=120, height=40)

#Start Simulation Button

def B_StartSim():

    global h_on,h_off,Sim_period
   
    stop_event.clear()
    GridOn_button['state'] = 'disabled'
    GridOff_button['state'] = 'disabled'
    EssOn_button['state'] = 'disabled'
    EssOff_button['state'] = 'disabled'
    NessOn_button['state'] = 'disabled'
    NessOff_button['state'] = 'disabled'

    update_text_panel(clicked.get() + " Load Shedding Initiated")
    print(clicked.get() + " Load Shedding Initiated")
    h_on = data[clicked.get()][0]["hours_on"]
    h_off = data[clicked.get()][0]["hours_off"]
    Sim_period = data[clicked.get()][0]["Simulation Period"]
    threading.Thread(target=Powerloop, args=(Sim_period, h_on, h_off), daemon=True).start()

    return

StartSim_button = Button(root, text= "Start Sim", command=B_StartSim)
StartSim_button.place(x=10,y=200,width=100, height=30)

#End Simulation Button

def B_EndSim():
    
    #stop_event.clear()
    stop_event.set()

    GridOn_button['state'] = 'normal'
    GridOff_button['state'] = 'normal'
    EssOn_button['state'] = 'normal'
    EssOff_button['state'] = 'normal'
    NessOn_button['state'] = 'normal'
    NessOff_button['state'] = 'normal'

    clear_text_panel()
    update_text_panel("Simulation Ended Forcefully")
    print("Simulation Ended Forcefully")


EndSim_button = Button(root, text= "End Sim", command=B_EndSim)
EndSim_button.place(x=120,y=200,width=100, height=30)

def End_Sim():
    stop_event.set()
    #Main_ModBus_Script.GridOff()
    #Main_ModBus_Script.EssLoadOff()
    Delete_last_line()
    update_text_panel("Simulation Complete")


#Manual Simulation Button

def B_GridOn():
    #Main_ModBus_Script.GridOn()
    update_text_panel("Grid On button pressed")
    print("Grid On button pressed")
    return

GridOn_button = Button(root, text= "Grid On", command=B_GridOn)
GridOn_button.place(x=10,y=300,width=100, height=30)

def B_GridOff():
    #Main_ModBus_Script.GridOff()
    update_text_panel("Grid Off button pressed")
    print("Grid Off button pressed")
    return

GridOff_button = Button(root, text= "Grid Off", command=B_GridOff)
GridOff_button.place(x=120,y=300,width=100, height=30)

def B_EssOn():
    #Main_ModBus_Script.EssLoadOn()
    update_text_panel("Ess On button pressed")
    print("Ess On button pressed")
    return

EssOn_button = Button(root, text= "Ess On", command=B_EssOn)
EssOn_button.place(x=10,y=350,width=100, height=30)

def B_EssOff():
    #Main_ModBus_Script.EssLoadOff()
    update_text_panel("Ess Off button pressed")
    print("Ess Off button pressed")
    return

EssOff_button = Button(root, text= "Ess Off", command=B_EssOff)
EssOff_button.place(x=120,y=350,width=100, height=30)

def B_NessOn():

    #Main_ModBus_Script.NessLoadOn()
    update_text_panel("Non-Ess On button pressed - Not activated")
    print("Non-Ess On button pressed - Not activated")
    return

NessOn_button = Button(root, text= "N-Ess On", command=B_NessOn)
NessOn_button.place(x=10,y=400,width=100, height=30)

def B_NessOff():

    #Main_ModBus_Script.NessLoadOff()
    update_text_panel("Non-Ess Off button pressed - Not activated")
    print("Non-Ess Off button pressed - Not activated")
    return

NessOff_button = Button(root, text= "N-Ess Off", command=B_NessOff)
NessOff_button.place(x=120,y=400,width=100, height=30)


##########################################################################

#Creating second frame

frame2 = LabelFrame(root, padx=100,pady=100)
frame2.place(x=225, y=100, width=575, height=350)
frame2.configure(background='#cf22f9')

text_panel = Text(frame2, height=12, width=50, font=('Arial', 12), bg='white', fg = 'black')
text_panel.place(x=-70, y=-90)

# Disable editing of the Text widget (only for display)
text_panel.config(state=DISABLED)

# Function to update the Text widget with status messages
def update_text_panel(message):
    text_panel.config(state=NORMAL)
    text_panel.insert(END, message +"\n")
    text_panel.yview(END)  # Automatically scroll to the bottom
    text_panel.config(state=DISABLED)

def clear_text_panel():
    text_panel.config(state=NORMAL)  # Make the text panel editable
    text_panel.delete(1.0, END)  # Delete all text from the beginning to the end
    text_panel.config(state=DISABLED)  # Make the text panel non-editable again

def Single_line_update(message):

    text_panel.config(state=NORMAL)  # Make the text panel editable
    
    # Delete the last line of text (if any)
    text_panel.delete("end-1l linestart", "end-1l lineend")  # Deletes the last line
    
    # Insert the new message
    text_panel.insert(END, message)
    text_panel.config(state=DISABLED)  # Make the text panel non-editable again

def Delete_last_line():
    text_panel.config(state=NORMAL)  # Make the text panel editable
    
    # Get the current position (end of the text)
    current_position = text_panel.index("end-1c")  # "end-1c" gets the last character
    
    # Find the position of the previous line
    previous_line_start = text_panel.index(f"{current_position} linestart")
    previous_line_end = text_panel.index(f"{previous_line_start} lineend")
    
    # Delete the previous line
    text_panel.delete(previous_line_start, previous_line_end)
    
    text_panel.config(state=DISABLED) 

##############################################################################################


# Save, Quit, Help and Clear Buttons

def B_Save():

    print("Saved Button Pressed - Not actrivated")
    return


Save_button = Button(frame2, text= "Save", command=B_Save)
Save_button.place(x=-75,y=170,width=100, height=30)

def B_Clear():

    clear_text_panel()
    print("Clear Button Pressed - Not actrivated")
    return


Clear_button = Button(frame2, text= "Clear", command=B_Clear)
Clear_button.place(x=50,y=170,width=100, height=30)

def B_Help():
    try:
        # Open the help.txt file and read it
        with open("Help_File.txt", "r") as file:
            help_content = file.read()
            # Create a new window to display the help text
            help_window = tk.Toplevel()
            help_window.title("Help")
            text_widget = tk.Text(help_window, wrap="word", width=50, height=20)
            text_widget.insert("1.0", help_content)
            text_widget.pack(expand=True, fill="both")
            text_widget.config(state="disabled")  # Make text non-editable
    except FileNotFoundError:
        messagebox.showerror("Error", "Help file not found.")

# # Example of setting up a Tkinter window
# root = tk.Tk()
# root.title("Help Button Example")


Help_button = Button(frame2, text= "Help", command=B_Help)
Help_button.place(x=175,y=170,width=100, height=30)

def B_Quit():

    root.quit()
    #print("Quit Button Pressed - Not Activated")
    return


Quit_button = Button(frame2, text= "Quit", command=B_Quit)
Quit_button.place(x=300,y=170,width=100, height=30)


############################################################################################

#utuility functions

#Pre Simulation Functions


# Input box to ask user to specify the time period they want the simulation to occur over (Not used. Determined in Json file)
def show_input_box():

    mess_b = tk.Tk()
    mess_b.withdraw()
    user_input = simpledialog.askstring("Input", "How long do you want the simulation to last? [Answer in hours]:")
    mess_b.destroy()
    

    return user_input

# Input box to ask user to specify the time period they want the simulation to occur over (Not used. Determined in Json file)
def Pre_Sim():

    global P_hours

    user_input = show_input_box()
    
    
    if user_input is None:
        print("Simulation canceled by the user.\n")
        return
    
    try:
        P_hours = int(user_input)
    except ValueError:
        print("Invalid input. Please enter a valid number of hours.\n")
        return

    P_hours = int(user_input)
    print(str(P_hours) + ' hours period of load shedding')


# Run countdown in a separate thread
def threaded_countdown_timer(hours):
    threading.Thread(target=countdown_timer, args=(hours,), daemon=True).start()

def countdown_timer(hours):
  
    #testing in seconds
    total_seconds = hours*60   # convert hours to seconds
    #time.sleep(1)
    first_update = True  # Flag to ensure the line is updated only once at the start
    c = 0


    while total_seconds > 0:
        if stop_event.is_set():  # To stop if the event is triggered
            break
        minutes = (total_seconds % 3600)//60
        seconds = (total_seconds % 60)//1  
        print(f"(Countdown Timer)-Time remaining:{minutes:02}:{seconds:02}", end='\r')
        #Single_line_update(f"(Countdown Timer)-Time remaining: {seconds:02}")

        
        if c<3:
            Single_line_update(f"")
            #first_update = False  # Reset the flag to prevent further updates on the same line

        else:
            # Update the same line in the text widget (only for timer updates)
            Single_line_update(f"(Countdown Timer)-Time remaining:{minutes:02}:{seconds:02}")

        #Delete_last_line()
        time.sleep(1)
        total_seconds -= 1
        c +=1

    Single_line_update("")  # Clear the line
    
    
    

def Powerloop(P_hours, h_on, h_off):
    while P_hours >= (h_off):
        # Check if stop event is set and break out of the loop
        if stop_event.is_set():
            break

        # Main simulation logic for Grid Off and Ess On...
        print("\n(Power Loop)-Load Shedding Starting - switching Grid power off")
        update_text_panel("\nLoad Shedding Starting - switching Grid power off")
        update_text_panel("Grid Power off - Hours Remaining: " + str(P_hours))

        # Count down for h_off hours
        threaded_countdown_timer(h_off)
        countdown_timer(h_off)

        P_hours -= h_off

        # Check again before continuing to Grid On part
        if stop_event.is_set():
            break

        print("\n(Power Loop)-Load Shedding complete, switching Grid power on")
        update_text_panel("\nLoad Shedding complete, switching Grid power on")

        if P_hours >= h_on:
            update_text_panel("Grid Power on - Hours Remaining: " + str(P_hours))
            threaded_countdown_timer(h_on)
            countdown_timer(h_on)

        P_hours -= h_on

    if P_hours < h_on:
        End_Sim()

    
root.mainloop() #makes whole program (root and new windows) run continuously
