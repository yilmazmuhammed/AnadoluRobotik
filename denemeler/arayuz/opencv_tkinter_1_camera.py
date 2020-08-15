import numpy as np
import cv2
import tkinter as tk
from PIL import Image, ImageTk

# Set up GUI
window = tk.Tk()  # Makes main window
window.wm_title("Pencere Başlığı")
window.config(background="#FFFFFF")

# Graphics window
imageFrame = tk.Frame(window, width=600, height=500)
imageFrame.grid(row=0, column=0, padx=10, pady=2)

# Capture video frames
lmain = tk.Label(imageFrame)
lmain.grid(row=0, column=0)
# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture("../../cember.mp4")


def show_frame():
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(10, show_frame)


# Slider window (slider controls stage position)
sliderFrame = tk.Frame(window, width=600, height=100)
sliderFrame.grid(row=600, column=0, padx=10, pady=2)

if __name__ == '__main__':
    show_frame()  # Display 2
    window.mainloop()  # Starts GUI
