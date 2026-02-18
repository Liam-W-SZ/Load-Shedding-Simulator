

from tkinter import Tk, Label
from PIL import Image, ImageTk

# Create Tkinter root window
root = Tk()

# Load an image (make sure the path is correct)
#/home/main/Desktop/Eng Model Code 2025/SZ_Logo.png
image = Image.open(r"/home/main/Desktop/Eng_Model_Code_2025/SZ_Logo.png")
#r"/home/main/Desktop/Liam/build/assets/frame0")
photo = ImageTk.PhotoImage(image)

# Create label with image
label = Label(root, image=photo)
label.pack()

root.mainloop()

