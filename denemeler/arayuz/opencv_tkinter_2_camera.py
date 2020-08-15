from time import sleep

from PIL import Image, ImageTk
from tkinter import Tk, PhotoImage, Label, Frame, Button
import datetime
import cv2
import os


class Window(Tk):
    def __init__(self):
        super().__init__()
        self.title("Robot başlatılıyor | Anadolu Robotik")  # pencere başlığı ayarla
        self.tk.call('wm', 'iconphoto', self._w, PhotoImage(file="anadolu_robotik_kare.png"))  # pencere iconu ayarla
        self.config(bg="skyblue")  # arkaplan rengi


class OpeningWindow:
    def __init__(self, window, next_window=None):
        self.next_window = next_window
        self.up_frame = Frame(window, width=640, height=400, bg='skyblue')
        self.up_frame.grid(row=0, column=0, padx=10, pady=5)

        image = PhotoImage(file="/home/myilmaz/Clouds/Dropbox/Git/GitHub/joystick/arayuz/anadolu_robotik_pp.png")
        image_label = Label(self.up_frame, image=image)
        image_label.image = image
        image_label.grid(row=0, column=0, padx=5, pady=25)

        self.sensors_control_label = Label(self.up_frame, text="Sensörler kontrol ediliyor...", bg="skyblue")
        self.sensors_control_label.grid(row=1, column=0, padx=5, pady=0)

        self.completion_label = Label(self.up_frame, text=":::", bg="skyblue")
        self.completion_label.grid(row=2, column=0, padx=5, pady=5)

        self.count = 0
        self.limit = 50
        self.controls = [self.is_active_lidars, self.is_active_motors, self.controls_completed, self.start_vehicle]
        self.controls2 = [self.is_active_lidars, self.is_active_motors, self.controls_completed, self.start_vehicle]
        self.control_loop()

    def control_loop(self):
        if len(self.controls) > 0:
            control = self.controls[0]
            if control():
                self.controls.remove(control)
        else:
            pass
        window.after(30, self.control_loop)

    def is_active_lidars(self):
        self.sensors_control_label['text'] = "Lidarlar kontrol ediliyor..."
        if self.count == self.limit:  # TODO control
            self.completion_label['text'] += ":::"
            self.count = 0
            return True
        self.count += 1
        return False

    def is_active_motors(self):
        self.sensors_control_label['text'] = "Motorlar kontrol ediliyor..."
        if self.count == self.limit:  # TODO control
            self.completion_label['text'] += ":::"
            self.count = 0
            return True
        self.count += 1
        return False

    def controls_completed(self):
        self.sensors_control_label['text'] = "Bütün kontroller tamamlandı."
        if self.count == self.limit:  # TODO control
            self.completion_label['text'] += ":::"
            self.count = 0
            return True
        self.count += 1
        return False

    def start_vehicle(self):
        self.sensors_control_label['text'] = "Araç çalıştırılıyor..."
        if self.count == self.limit:  # TODO control
            self.completion_label['text'] += ":::"
            self.count = 0
            return True
        self.count += 1
        return False

    def destroy(self):
        # self.etiket['text'] = 'Elveda zalim dünya...'
        # self.düğme['text'] = 'Bekleyin...'
        # self.düğme['state'] = 'disabled'
        self.after(30, super().destroy)


class Application:
    def __init__(self, output_path="./"):
        self.sayac = 0
        """ Initialize application which uses OpenCV + Tkinter. It displays
            a video stream in a Tkinter window and stores current snapshot on disk """
        self.vs = cv2.VideoCapture(0)  # capture video frames, 0 is your default video camera
        self.output_path = output_path  # store output path
        self.current_image = None  # current image from the camera

        self.tk_window = Tk()  # initialize root window
        self.tk_window.title("Anadolu Robotik")  # set window title
        # self.destructor function gets fired when the window is closed
        self.tk_window.protocol('WM_DELETE_WINDOW', self.destructor)
        self.tk_window.config(bg="skyblue")  # arkaplan rengi

        self.panel = Label(self.tk_window)  # initialize image panel
        self.panel.pack(padx=10, pady=10)

        # create a button, that when pressed, will take the current frame and save it to file
        btn = Button(self.tk_window, text="Snapshot!", command=self.take_snapshot)
        btn.pack(fill="both", expand=True, padx=10, pady=10)
        self.etiket = Label(text='Merhaba Zalim Dünya')
        self.etiket.pack()
        # start a self.video_loop that constantly pools the video sensor
        # for the most recently read frame
        self.video_loop()

    def video_loop(self):
        self.sayac = self.sayac + 1
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.vs.read()  # read frame from video stream
        if ok:  # frame captured without any errors
            # frame = cv2.flip(frame, 1)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
            self.current_image = Image.fromarray(cv2image)  # convert image for PIL
            imgtk = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter
            self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.config(image=imgtk)  # show the image
        self.etiket['text'] = str(self.sayac)
        self.tk_window.after(30, self.video_loop)  # call the same function after 30 milliseconds

    def take_snapshot(self):
        """ Take snapshot and save it to the file """
        ts = datetime.datetime.now()  # grab the current timestamp
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))  # construct filename
        p = os.path.join(self.output_path, filename)  # construct output path
        self.current_image.save(p, "JPEG")  # save image as jpeg file
        print("[INFO] saved {}".format(filename))

    def destructor(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing...")
        self.tk_window.destroy()
        self.vs.release()  # release web camera
        cv2.destroyAllWindows()  # it is not mandatory in this application


if __name__ == '__main__':
    window = Window()
    ow2 = OpeningWindow(window)
    ow = OpeningWindow(window, ow2)
    window.mainloop()

    # start the app
    print("[INFO] starting...")
    pba = Application()
    pba.tk_window.mainloop()
