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
import sys
import Main_ModBus_Script, time #exclude for now
# import Main_ModBus_Script

stop_event = threading.Event()

print_lock = threading.Lock()
current_ess_msg = ["Essential Power On Time remaining: 00:00:00"]
current_ness_msg = ["Non-Essential Power On Time remaining: 00:00:00"]

# Enable ANSI escape codes on Windows
if os.name == 'nt':
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

timer_lines_initialized = False

def print_timers():
    global timer_lines_initialized
    with print_lock:
        ess = current_ess_msg[0]
        ness = current_ness_msg[0]
        max_len = max(len(ess), len(ness))
        ess = ess.ljust(max_len)
        ness = ness.ljust(max_len)
        if not timer_lines_initialized:
            # Print two blank lines to reserve space and flush
            print()
            print()
            timer_lines_initialized = True
        # Move cursor up two lines to the start of the timer block
        sys.stdout.write('\033[2F')
        sys.stdout.flush()
        # Clear and print Essential line
        sys.stdout.write('\033[2K' + ess + '\n')
        sys.stdout.flush()
        # Clear and print Non-Essential line
        sys.stdout.write('\033[2K' + ness + '\n')
        sys.stdout.flush()
        # Do not move the cursor up again; let it rest after the two lines

root = Tk()

root.title('LSS - V1') # Give Title to Old Window GUI
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

    global h_on,h_off,Ess_h_on,Ess_h_off,Ness_h_on,Ness_h_off,Sim_period
    
    #update_text_panel(clicked.get() + " Load Shedding Initiated:")
   
    stop_event.clear()

    Main_ModBus_Script.EssLoadOff()
    Main_ModBus_Script.NessLoadOff()
    Main_ModBus_Script.EssLoadOff2()
    Main_ModBus_Script.NessLoadOff2()

    time.sleep(2)

    h_on = data[clicked.get()][0]["hours_on"]
    h_off = data[clicked.get()][0]["hours_off"]
    Sim_period = data[clicked.get()][0]["Simulation Period"]
    Ess_h_on = data[clicked.get()][0]["Ess_hours_on"]
    Ess_h_off = data[clicked.get()][0]["Ess_hours_off"]
    Ness_h_on = data[clicked.get()][0]["NEss_hours_on"]
    Ness_h_off = data[clicked.get()][0]["NEss_hours_off"]

    if (clicked.get() == "Custom_Sim"):

        print("Custom Simulation Selected")
        GridOn_button['state'] = 'disabled'
        GridOff_button['state'] = 'disabled'
        EssOn_button['state'] = 'disabled'
        EssOff_button['state'] = 'disabled'
        NessOn_button['state'] = 'disabled'
        NessOff_button['state'] = 'disabled'
        drop.config(state = 'disabled')
        StartSim_button['state'] = 'disabled'
        EndSim_button['state'] = 'normal'
        
        threading.Thread(target=Scheduling_loop, args=(Sim_period, Ess_h_on, Ess_h_off, Ness_h_on, Ness_h_off), daemon=True).start()

    
    else:
        print("Load Shedding Simulation Selected")
        update_text_panel(clicked.get() + " Load Shedding Initiated:")
        # Main_ModBus_Script.GridOn()
        # time.sleep(5)  #Wait Ess & Ness Meter to turn on
        # Main_ModBus_Script.EssLoadOn()
        # Main_ModBus_Script.NessLoadOn()
        # time.sleep(5)
        
        #Disable manual buttons during simulation
        GridOn_button['state'] = 'disabled'
        GridOff_button['state'] = 'disabled'
        EssOn_button['state'] = 'disabled'
        EssOff_button['state'] = 'disabled'
        NessOn_button['state'] = 'disabled'
        NessOff_button['state'] = 'disabled'
        drop.config(state = 'disabled')
        StartSim_button['state'] = 'disabled'
        EndSim_button['state'] = 'normal'

        
        print(clicked.get() + " Load Shedding Initiated")

        threading.Thread(target=Powerloop, args=(Sim_period, h_on, h_off), daemon=True).start()

    return

StartSim_button = Button(root, text= "Start Sim", command=B_StartSim)
StartSim_button.place(x=10,y=200,width=100, height=30)

#End Simulation Button
def B_EndSim():
    
    #stop_event.clear()
    stop_event.set()
    
    Main_ModBus_Script.EssLoadOff()
    Main_ModBus_Script.NessLoadOff()
    Main_ModBus_Script.EssLoadOff2()
    Main_ModBus_Script.NessLoadOff2()

    # Main_ModBus_Script.GridOff()
    
    #Re-enable buttons when simulation Forcefully Stopped
    GridOn_button['state'] = 'normal'
    GridOff_button['state'] = 'normal'
    EssOn_button['state'] = 'normal'
    EssOff_button['state'] = 'normal'
    NessOn_button['state'] = 'normal'
    NessOff_button['state'] = 'normal'
    drop.config(state = 'normal')
    StartSim_button['state'] = 'normal'
    EndSim_button['state'] = 'disabled'

    # time.sleep(1)
    clear_text_panel()
    # time.sleep(3)    
    # clear_text_panel()
    #update_text_panel(clicked.get() +" Simulation Ended Forcefully")
    print("Simulation Ended Forcefully")


EndSim_button = Button(root, text= "End Sim", command=B_EndSim)
EndSim_button.place(x=120,y=200,width=100, height=30)

def End_Sim():
    stop_event.set()
    # Main_ModBus_Script.EssLoadOff()
    # Main_ModBus_Script.NessLoadOff()
    # Main_ModBus_Script.EssLoadOff2()
    # Main_ModBus_Script.NessLoadOff2()
    Main_ModBus_Script.Relay_Toggle_ESS(False)
    Main_ModBus_Script.Relay_Toggle_ESS2(False)
    Main_ModBus_Script.Relay_Toggle_Non_ESS(False)
    Main_ModBus_Script.Relay_Toggle_Non_ESS2(False)
    # Main_ModBus_Script.GridOff()
    
    Delete_last_line()
    update_text_panel("\n"+clicked.get() +" Simulation Complete")
    
    #Re-enable buttons when simulation Stopped
    GridOn_button['state'] = 'normal'
    GridOff_button['state'] = 'normal'
    EssOn_button['state'] = 'normal'
    EssOff_button['state'] = 'normal'
    NessOn_button['state'] = 'normal'
    NessOff_button['state'] = 'normal'
    drop.config(state = 'normal')
    StartSim_button['state'] = 'normal'
    EndSim_button['state'] = 'disabled'


#Manual Simulation Button

def B_GridOn():
    # Main_ModBus_Script.GridOn()
    update_text_panel("Grid On button pressed")
    print("Grid On button pressed")
    return

GridOn_button = Button(root, text= "Grid On", command=B_GridOn)
GridOn_button.place(x=10,y=300,width=100, height=30)

def B_GridOff():
    # Main_ModBus_Script.GridOff()
    update_text_panel("Grid Off button pressed")
    print("Grid Off button pressed")
    return

GridOff_button = Button(root, text= "Grid Off", command=B_GridOff)
GridOff_button.place(x=120,y=300,width=100, height=30)

def B_EssOn():
    Main_ModBus_Script.Relay_Toggle_ESS(True)
    Main_ModBus_Script.Relay_Toggle_ESS2(True)
    # Main_ModBus_Script.EssLoadOn()
    # Main_ModBus_Script.EssLoadOn2()
    update_text_panel("Ess On button pressed")
    print("Ess On button pressed")
    return

EssOn_button = Button(root, text= "Ess On", command=B_EssOn)
EssOn_button.place(x=10,y=350,width=100, height=30)

def B_EssOff():
    Main_ModBus_Script.Relay_Toggle_ESS(False)
    Main_ModBus_Script.Relay_Toggle_ESS2(False)
    # Main_ModBus_Script.EssLoadOff()
    # Main_ModBus_Script.EssLoadOff2()
    update_text_panel("Ess Off button pressed")
    print("Ess Off button pressed")
    return

EssOff_button = Button(root, text= "Ess Off", command=B_EssOff)
EssOff_button.place(x=120,y=350,width=100, height=30)

def B_NessOn():
    Main_ModBus_Script.Relay_Toggle_Non_ESS(True)
    Main_ModBus_Script.Relay_Toggle_Non_ESS2(True)
    # Main_ModBus_Script.NessLoadOn()
    # Main_ModBus_Script.NessLoadOn2()
    #Main_ModBus_Script.EssLoadOn()
    #Main_ModBus_Script.EssLoadOn2()
    update_text_panel("Non-Ess On button pressed - Not activated")
    print("Non-Ess On button pressed - Not activated")
    return

NessOn_button = Button(root, text= "N-Ess On", command=B_NessOn)
NessOn_button.place(x=10,y=400,width=100, height=30)

def B_NessOff():
    Main_ModBus_Script.Relay_Toggle_Non_ESS(False)
    Main_ModBus_Script.Relay_Toggle_Non_ESS2(False)
    # Main_ModBus_Script.NessLoadOff()
    # Main_ModBus_Script.NessLoadOff2()
    # Main_ModBus_Script.EssLoadOff()
    # Main_ModBus_Script.EssLoadOff2()
    update_text_panel("Non-Ess Off button pressed")
    print("Non-Ess Off button pressed")
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

# Function to update the Text Panel
def update_text_panel(message):
    text_panel.config(state=NORMAL)
    text_panel.insert(END, message +"\n")
    text_panel.yview(END)   #Wait Ness Meter to turn on
    text_panel.config(state=DISABLED)

def clear_text_panel():
    text_panel.config(state=NORMAL)  
    text_panel.delete(1.0, END)  # Delete all text from the beginning to the end
    text_panel.config(state=DISABLED)  

def Single_line_update(message):
    text_panel.config(state=NORMAL)
    # Delete the last line (timer line) if it exists
    last_line_index = text_panel.index("end-2l")
    if float(last_line_index) > 1.0:
        text_panel.delete("end-2l", "end-1l")
    else:
        text_panel.delete("1.0", "end-1l")
    # Insert the new timer message as the last line
    text_panel.insert(END, message + "\n")
    text_panel.config(state=DISABLED)

def Delete_last_line():
    text_panel.config(state=NORMAL)    
    current_position = text_panel.index("end-1c")  
       
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


Help_button = Button(frame2, text= "Help", command=B_Help)
Help_button.place(x=175,y=170,width=100, height=30)

def B_Quit():
    
    
    # Main_ModBus_Script.EssLoadOff()
    # Main_ModBus_Script.NessLoadOff()
    # Main_ModBus_Script.GridOff()
    Main_ModBus_Script.EssLoadOff()
    Main_ModBus_Script.NessLoadOff()
    Main_ModBus_Script.EssLoadOff2()
    Main_ModBus_Script.NessLoadOff2()
    root.quit()
    #print("Quit Button Pressed - Not Activated")
    return


Quit_button = Button(frame2, text= "Quit", command=B_Quit)
Quit_button.place(x=300,y=170,width=100, height=30)


############################################################################################

#utuility functions - Not Used

#Pre Simulation Functions
'''
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
'''

# Run countdown in a separate thread
def threaded_countdown_timer(hours):
    threading.Thread(target=countdown_timer, args=(hours,), daemon=True).start()

def countdown_timer(hours):
    total_seconds = hours*3600
    c = 0
    while total_seconds > 0:
        if stop_event.is_set():
            break
        hours = (total_seconds % 216000)//3600
        minutes = (total_seconds % 3600)//60
        seconds = (total_seconds % 60)//1
        print(f"Time remaining: {hours:02}:{minutes:02}:{seconds:02}", end='\r')
        if c < 1:
            Single_line_update("")
        else:
            Single_line_update(f"Time remaining: {hours:02}:{minutes:02}:{seconds:02}")
        time.sleep(1)
        total_seconds -= 1
        c += 1
    Single_line_update("")  # Clear the line

def Powerloop(P_hours, h_on, h_off):
    while P_hours >= (h_off):
        
        # Check if stop event is set and break out of the loop
        if stop_event.is_set():
            break

        
        print("\n(Power Loop)-Load Shedding Starting - switching Grid power off")
        update_text_panel("\nLoad Shedding Starting...")
        update_text_panel("Grid Power Off")
        update_text_panel("Non-Essential Power Off")
        update_text_panel("Essential Power On")        
        update_text_panel("Simulation Hours Remaining: " + str(P_hours))
        
        # Main_ModBus_Script.NessLoadOff()
        # Main_ModBus_Script.GridOff()

        # Count down for h_off hours
        countdown_timer(h_off)
        P_hours -= h_off

        # Check again before continuing to Grid On part
        if stop_event.is_set():
            break

        print("\n(Power Loop)-Load Shedding complete, switching Grid power on")
        update_text_panel("\nLoad Shedding complete")
        update_text_panel("Grid Power On")
        update_text_panel("Non-Essential Power On")
        update_text_panel("Essential Power On") 
        
        # Main_ModBus_Script.GridOn()
        # time.sleep(5) #Wait Ness Meter to turn on
        # Main_ModBus_Script.NessLoadOn()

        if P_hours >= h_on:
            update_text_panel("Simulation Hours Remaining: " + str(P_hours))
            countdown_timer(h_on)

        P_hours -= h_on

    if P_hours < h_on:
        End_Sim()

################################################################################### (New Code)


def Scheduling_loop(P_hours, Ess_h_on, Ess_h_off, Ness_h_on, Ness_h_off):
    update_text_panel("Custom Simulation Starting...")
    print("Custom Simulation Starting...")
    update_text_panel("Grid Power Remains On")
    print("Grid Power Remains On")
    update_text_panel("Essential and Non-Essential Loads will cycle independently.")
    print("Essential and Non-Essential Loads will cycle independently.")
    update_text_panel("Total Simulation Hours: " + str(P_hours))
    print("Total Simulation Hours: " + str(P_hours))

    # Insert a blank line after the header block
    text_panel.config(state=NORMAL)
    text_panel.insert(END, "\n")
    # Insert remaining hours line
    text_panel.insert(END, f"Remaining Simulation Hours: {P_hours}\n")
    rem_line_index = int(float(text_panel.index("end-2l").split('.')[0]))
    # Insert Ess and NEss timer lines
    text_panel.insert(END, "\n")
    ess_line_index = int(float(text_panel.index("end-2l").split('.')[0]))
    text_panel.insert(END, "\n")
    ness_line_index = int(float(text_panel.index("end-2l").split('.')[0]))
    text_panel.config(state=DISABLED)

    sim_hours = {"remaining": P_hours}
    sim_hours_lock = threading.Lock()

    # Only update the timer line if the value actually changes
    def timer_line_update(line_index, msg, prev_msg_holder):
        def update():
            if prev_msg_holder[0] != msg:
                text_panel.config(state=NORMAL)
                text_panel.delete(f"{line_index}.0", f"{line_index}.end")
                text_panel.insert(f"{line_index}.0", msg)
                text_panel.config(state=DISABLED)
                prev_msg_holder[0] = msg
        root.after(0, update)

    def update_remaining_hours(new_value, prev_msg_holder):
        msg = f"Remaining Simulation Hours: {new_value:.2f}"
        def update():
            if prev_msg_holder[0] != msg:
                text_panel.config(state=NORMAL)
                text_panel.delete(f"{rem_line_index}.0", f"{rem_line_index}.end")
                text_panel.insert(f"{rem_line_index}.0", msg)
                text_panel.config(state=DISABLED)
                prev_msg_holder[0] = msg
        root.after(0, update)

    def countdown_timer_custom(period, power_state, line_index, prev_msg_holder):
        total_seconds = int(period * 3600)
        is_ess = "Essential" in power_state
        is_Ness = "Non-Essential" in power_state
        # Meter control logic
        if is_Ness:
            if "On" in power_state:
                Main_ModBus_Script.Relay_Toggle_Non_ESS(True)
                Main_ModBus_Script.Relay_Toggle_Non_ESS2(True)
                # Main_ModBus_Script.NessLoadOn()
                # Main_ModBus_Script.NessLoadOn2()
                print("NEss on- loop")
                #pass
            else:
                Main_ModBus_Script.Relay_Toggle_Non_ESS(False)
                Main_ModBus_Script.Relay_Toggle_Non_ESS2(False)
                # Main_ModBus_Script.NessLoadOff()
                # Main_ModBus_Script.NessLoadOff2()
                print("NEss off - loop")
                #pass
        elif is_ess:
            if "On" in power_state:
                Main_ModBus_Script.Relay_Toggle_ESS(True)
                Main_ModBus_Script.Relay_Toggle_ESS2(True)
                # Main_ModBus_Script.EssLoadOn()
                # Main_ModBus_Script.EssLoadOn2()
                print("Ess on- loop")
                #pass
            else:
                Main_ModBus_Script.Relay_Toggle_ESS(False)
                Main_ModBus_Script.Relay_Toggle_ESS2(False)
                # Main_ModBus_Script.EssLoadOff()
                # Main_ModBus_Script.EssLoadOff2()
                print("Ess off - loop")
                
        while total_seconds > 0 and not stop_event.is_set():
            h = (total_seconds % 216000) // 3600
            m = (total_seconds % 3600) // 60
            s = (total_seconds % 60) // 1
            msg = f"{power_state} Time remaining: {h:02}:{m:02}:{s:02}"
            timer_line_update(line_index, msg, prev_msg_holder)
            # Update the shared message (no terminal printing)
            if is_Ness:
                current_ness_msg[0] = msg
            else:
                current_ess_msg[0] = msg
            time.sleep(1)
            total_seconds -= 1
        # Finalize the line with 0:0:00
        final_msg = f"{power_state} Time remaining: 00:00:00"
        timer_line_update(line_index, final_msg, prev_msg_holder)
        if is_Ness:
            current_ness_msg[0] = final_msg
        else:
            current_ess_msg[0] = final_msg

    def ess_cycle():
        elapsed = 0
        state = True  # True = ON, False = OFF
        prev_ess_msg = [""]
        prev_rem_msg = [""]
        while elapsed < P_hours and not stop_event.is_set():
            with sim_hours_lock:
                remaining = max(P_hours - elapsed, 0)
            if state:
                period = min(Ess_h_on, remaining)
                power_state = "Essential Power On"
            else:
                period = min(Ess_h_off, remaining)
                power_state = "Essential Power Off"
            if period <= 0:
                break
            countdown_timer_custom(period, power_state, ess_line_index, prev_ess_msg)
            elapsed += period
            with sim_hours_lock:
                sim_hours["remaining"] = max(sim_hours["remaining"] - period, 0)
                update_remaining_hours(sim_hours["remaining"], prev_rem_msg)
            state = not state
        timer_line_update(ess_line_index, "Essential Power Off (End)", prev_ess_msg)
        print("Essential Power Off (End)")

    def ness_cycle():
        elapsed = 0
        state = True  # True = ON, False = OFF
        prev_ness_msg = [""]
        while elapsed < P_hours and not stop_event.is_set():
            remaining = max(P_hours - elapsed, 0)
            if state:
                period = min(Ness_h_on, remaining)
                power_state = "Non-Essential Power On"
            else:
                period = min(Ness_h_off, remaining)
                power_state = "Non-Essential Power Off"
            if period <= 0:
                break
            countdown_timer_custom(period, power_state, ness_line_index, prev_ness_msg)
            elapsed += period
            state = not state
        timer_line_update(ness_line_index, "Non-Essential Power Off (End)", prev_ness_msg)
        print("Non-Essential Power Off (End)")

    ess_thread = threading.Thread(target=ess_cycle, daemon=True)
    ness_thread = threading.Thread(target=ness_cycle, daemon=True)
    ess_thread.start()
    ness_thread.start()
    ess_thread.join()
    ness_thread.join()
    End_Sim()

root.mainloop()
