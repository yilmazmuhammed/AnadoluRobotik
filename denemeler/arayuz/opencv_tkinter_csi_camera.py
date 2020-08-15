from threading import Thread

import numpy as np
import cv2
import tkinter as tk
from PIL import Image, ImageTk

# Set up GUI
from csi_camera import CSI_Camera

window = tk.Tk()  # Makes main window
window.wm_title("Pencere Başlığı")
window.config(background="#FFFFFF")

# Graphics window
imageFrame = tk.Frame(window, width=600, height=500)
imageFrame.grid(row=0, column=0, padx=10, pady=2)

# # Capture video frames
# lmain = tk.Label(imageFrame)
# lmain.grid(row=0, column=0)


cameras_frame = tk.Frame(imageFrame, bg='skyblue')
tk.Label(cameras_frame, text="Ön Kamera", width=40, bg='skyblue').grid(row=0, column=0, padx=10, pady=5)
lmain = tk.Label(cameras_frame, text=" ")
lmain.grid(row=1, column=0, padx=10)
cameras_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=(70, 10))
# cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture("../../cember.mp4")
left_camera = CSI_Camera(sensor_id=0, sensor_mode=3, flip_method=0, display_height=540, display_width=960)
left_camera.start()


def show_frame():
    while True:
        _, frame = left_camera.read()
        frame = cv2.flip(frame, 1)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)
    # lmain.after(10, show_frame)


update_thread = Thread(target=show_frame)
update_thread.start()


if __name__ == '__main__':
    # show_frame()  # Display 2
    window.mainloop()  # Starts GUI
