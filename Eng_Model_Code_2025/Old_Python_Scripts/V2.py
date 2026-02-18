from tkinter import *
from PIL import Image,ImageTk #import images
from tkinter import simpledialog
from tkinter import messagebox
#import matplotlib.pyplot as plt
import numpy as np
import json
import tkinter as tk
import tkinter.messagebox
import time
import threading
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#import matplotlib.animation as animation

stop_event = threading.Event()



import Main_ModBus_Script, time #exclude for now

root = Tk()

root.title('LSS - V1') # Give Title to Old Window GUI
#root.iconbitmap(r"/home/main/Desktop/Eng_Model_Code_2025/Jedi.ico") #download ico and place in same folder as script
#r"/home/main/Desktop/Eng_Model_Code_2025/SZ_Logo.png"
root.geometry("800x450") #Give Size to your widget
#root.state('zoomed') #Makes window expandable
root.configure(background='white')
#root.resizable(True,True)

r_label=Label(root,text="Load Shedding Simulator",font=('Arial Black',20),bg='white',anchor='w')
r_label.place(x=330,y=40)

img1 = ImageTk.PhotoImage(Image.open(r"/home/main/Desktop/Eng_Model_Code_2025/SZ_Logo.png"))

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

#print(data.items())
#print(data)

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
    #Pre_Sim()
    #print(clicked.get())  #prints stage selected
    update_text_panel(clicked.get() + " Load Shedding Initiated")
    print(clicked.get() + " Load Shedding Initiated")
    h_on = data[clicked.get()][0]["hours_on"]
    h_off = data[clicked.get()][0]["hours_off"]
    Sim_period = data[clicked.get()][0]["Simulation Period"]
    #print(str(h_on) + " hours Power off") #prints hours on
    #print(str(h_off)+ " hours Power on") #prints hours off
    #print(str(Sim_period)+ " hours is the simulation Period") #prints hours off

    threading.Thread(target=Powerloop, args=(Sim_period, h_on, h_off), daemon=True).start()
    #Powerloop(Sim_period,h_on,h_off)


    return

mybutton = Button(root, text= "Start Sim", command=B_StartSim)
mybutton.place(x=10,y=200,width=100, height=30)


#End Simulation Button

def B_EndSim():
    stop_event.set()
    #Main_ModBus_Script.GridOff()
    #Main_ModBus_Script.EssLoadOff()
    Delete_last_line()
    update_text_panel("\nSimulation Ended")
    print("\nSimulation Ended")
    #stop_event.set()
    #stop_event.clear()


    return

mybutton = Button(root, text= "End Sim", command=B_EndSim)
mybutton.place(x=120,y=200,width=100, height=30)



#Manual Simulation Button

def B_GridOn():
    Main_ModBus_Script.GridOn()
    update_text_panel("Grid On button pressed")
    print("Grid On button pressed")
    return

mybutton = Button(root, text= "Grid On", command=B_GridOn)
mybutton.place(x=10,y=300,width=100, height=30)

def B_GridOff():
    Main_ModBus_Script.GridOff()
    update_text_panel("Grid Off button pressed")
    print("Grid Off button pressed")
    return

mybutton = Button(root, text= "Grid Off", command=B_GridOff)
mybutton.place(x=120,y=300,width=100, height=30)

def B_EssOn():
    Main_ModBus_Script.EssLoadOn()
    update_text_panel("Ess On button pressed")
    print("Ess On button pressed")
    return

mybutton = Button(root, text= "Ess On", command=B_EssOn)
mybutton.place(x=10,y=350,width=100, height=30)

def B_EssOff():
    Main_ModBus_Script.EssLoadOff()
    update_text_panel("Ess Off button pressed")
    print("Ess Off button pressed")
    return

mybutton = Button(root, text= "Ess Off", command=B_EssOff)
mybutton.place(x=120,y=350,width=100, height=30)

def B_NessOn():

    update_text_panel("Non-Ess On button pressed - Not activated")
    print("Non-Ess On button pressed - Not activated")
    return

mybutton = Button(root, text= "N-Ess On", command=B_NessOn)
mybutton.place(x=10,y=400,width=100, height=30)

def B_NessOff():

    update_text_panel("Non-Ess Off button pressed - Not activated")
    print("Non-Ess Off button pressed - Not activated")
    return

mybutton = Button(root, text= "N-Ess Off", command=B_NessOff)
mybutton.place(x=120,y=400,width=100, height=30)


##########################################################################

#Creating second frame

frame2 = LabelFrame(root, padx=100,pady=100)
frame2.place(x=225, y=100, width=575, height=350)
#frame2.place(x=200, y=100, width=650, height=375)
frame2.configure(background='#cf22f9')

text_panel = Text(frame2, height=12, width=50, font=('Arial', 12), bg='white', fg = 'black')
text_panel.place(x=-70, y=-90)

# Disable editing of the Text widget (only for display)
text_panel.config(state=DISABLED)

# Function to update the Text widget with status messages
def update_text_panel(message):
    text_panel.config(state=NORMAL)
    text_panel.insert(END, message+ "\n")
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

# Tick Boxes

TB = StringVar()
TB2 = StringVar()
TB3 = StringVar()
TB4 = StringVar()


'''
c1 = Checkbutton(frame2, text="Grid Input", variable= TB, onvalue="Okay",offvalue="No") #Creates square check Box
c1.configure(background='#cf22f9')
c1.deselect() #deselects check box when running program for the first time
c1.place(x=380,y=-50)

c2 = Checkbutton(frame2, text="PV Input", variable= TB2, onvalue="Okay",offvalue="No") #Creates square check Box
c2.configure(background='#cf22f9')
c2.deselect() #deselects check box when running program for the first time
c2.place(x=380,y=0)

c3 = Checkbutton(frame2, text="Battery", variable= TB3, onvalue="Okay",offvalue="No") #Creates square check Box
c3.configure(background='#cf22f9')
c3.deselect() #deselects check box when running program for the first time
c3.place(x=380,y=50)

c4 = Checkbutton(frame2, text="Load", variable= TB4, onvalue="Okay",offvalue="No") #Creates square check Box
c4.configure(background='#cf22f9')
c4.deselect() #deselects check box when running program for the first time
c4.place(x=380,y=100)
#c4.config(state=DISABLED) #Disabling a CheckButton
'''

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

    print("Help Button Pressed - Not actrivated")
    return


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

    
    #works for minutes
    total_seconds = hours * 60  # convert hours to seconds
    while total_seconds > 0:
        if stop_event.is_set():
            break
        
        minutes = (total_seconds % 3600)//60
        seconds = (total_seconds % 60)//1    
        print(f"Time remaining:{minutes:02}:{seconds:02}", end='\r')
        #Single_line_update(f"(Countdown Timer)-Time remaining: {hours:02}:{minutes:02}:{seconds:02}")
        time.sleep(1)
        total_seconds -= 1
    '''
       
    #works for hours
    total_seconds = hours * 3600  # convert hours to seconds
    while total_seconds > 0:
        if stop_event.is_set():
            break
        hours = (total_seconds % 216000)//3600
        minutes = (total_seconds % 3600)//60
        seconds = (total_seconds % 60)//1    
        print(f"Time remaining: {hours:02}:{minutes:02}:{seconds:02}", end='\r')
        #Single_line_update(f"(Countdown Timer)-Time remaining: {hours:02}:{minutes:02}:{seconds:02}")
        time.sleep(1)
        total_seconds -= 1
    '''
    '''       
    #testing in seconds
    total_seconds = hours   # convert hours to seconds
    while total_seconds > 0:
        if stop_event.is_set():  # To stop if the event is triggered
            break
        seconds = total_seconds
        print(f"(Countdown Timer)-Time remaining: {seconds:02}", end='\r')
        #Single_line_update(f"(Countdown Timer)-Time remaining: {seconds:02}")
        #Delete_last_line()
        time.sleep(1)
        total_seconds -= 1
    '''
    

def Powerloop(P_hours,h_on,h_off):

    while P_hours >= (h_off):


        #Main_ModBus_Script.GridOff()
        #Main_ModBus_Script.EssLoadOn()
        #print("(Power Loop)-Grid Power off - Hours Remaining: " + str(P_hours) )
        print("\n(Power Loop)-Load Shedding Starting - switching Grid power off" )
        print("(Power Loop)-Grid Power off - Hours Remaining: " + str(P_hours) )
        #Delete_last_line()
        update_text_panel("\nLoad Shedding Starting - switching Grid power off" )
        update_text_panel("Grid Power off - Hours Remaining: " + str(P_hours))
        #time.sleep(5)
        threaded_countdown_timer(h_off)
        countdown_timer(h_off)

        P_hours -= h_off
        print("\n(Power Loop)-Load Shedding complete, switching Grid power on")
        #Delete_last_line()
        update_text_panel("\nLoad Shedding complete, switching Grid power on")

        #Main_ModBus_Script.GridOn()
        
        if (P_hours) >= h_on:

            print("(Power Loop)-Grid Power on - Hours Remaining: " + str(P_hours))
            #Delete_last_line()
            update_text_panel("Grid Power on - Hours Remaining: " + str(P_hours))
            
            threaded_countdown_timer(h_on)
            countdown_timer(h_on)
        
        P_hours -= h_on


    if (P_hours) < h_on:
            #print("Simululation Complete")
            B_EndSim()
        


root.mainloop() #makes whole program (root and new windows) run continuously
