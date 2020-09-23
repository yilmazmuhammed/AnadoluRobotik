import copy
from datetime import datetime
from time import sleep

import cv2
import tkinter as tk

from PIL import Image, ImageTk
from random import randint
from threading import Thread
from tkinter import font as tkfont

from imutils.video import FPS

from csi_camera import CSI_Camera, gstreamer_pipeline

from joystick import Joystick
from lidars import RovLidars

try:
    from motors import RovMovement
except NotImplementedError as e:
    print("Motorlar çalıştırılamadı")
    print("NotImplementedError:", e)

print("import sonrası")

arayuz_running = True


class SampleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.manuel_thread = None

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.wm_title("Robot başlatılıyor - Anadolu Robotik")
        self.tk.call('wm', 'iconphoto', self._w, tk.PhotoImage(file="anadolu_robotik_kare.png"))  # pencere iconu ayarla
        self.config(bg="skyblue")  # arkaplan rengi

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.rov_movement = RovMovement(
            xy_lf_pin="-1", xy_rf_pin="4", xy_lb_pin="-0", xy_rb_pin="6",
            z_lf_pin="-3", z_rf_pin="2", z_lb_pin="-5", z_rb_pin="7",
            arm_pin=8,
            initialize_motors=False, ssc_control=True
        )

        self.frames = {}
        for F in (StartPage, SelectMissionPage, ObservationPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name, mission=None):
        """Show a frame for the given page name"""
        frame = self.frames[page_name]
        if mission == 1:
            self.manuel_thread = Thread(target=update_from_joystick, args=(self.rov_movement,))
            self.frames["ObservationPage"].baslat()
            self.manuel_thread.start()
            pass
        frame.tkraise()

    def remove_frame(self, page_name):
        """Remove a frame for the given page name"""
        self.frames.pop(page_name, None)

    def destroy(self):
        global arayuz_running
        arayuz_running = False
        if self.manuel_thread:
            print("self.manuel_thread bekleniyor...")
            self.manuel_thread.join()

        if self.rov_movement:
            self.rov_movement.stop()
        print("Program kapatılıyor...")
        self.after(30, super().destroy)


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, width=640, height=400, bg='skyblue', padx=10, pady=10)
        self.controller = controller

        image = tk.PhotoImage(file="anadolu_robotik_pp.png")
        image_label = tk.Label(self, image=image)
        image_label.image = image
        image_label.grid(row=0, column=0, padx=10, pady=25)

        self.control_status_label = tk.Label(self, text="Sensörler kontrol ediliyor...", bg="skyblue")
        self.control_status_label.grid(row=1, column=0, padx=5, pady=0)

        self.completion_bar_label = tk.Label(self, text=":::", bg="skyblue")
        self.completion_bar_label.grid(row=2, column=0, padx=5, pady=5)

        # label = tk.Label(self, text="This is the start page", font=controller.title_font)
        # label.pack(side="top", fill="x", pady=10)
        #
        # button1 = tk.Button(self, text="Go to Page One",
        #                     command=lambda: controller.show_frame("SelectMissionPage"))
        # button1.grid(row=3, column=0, padx=5, pady=5)
        # button2 = tk.Button(self, text="Go to Page Two",
        #                     command=lambda: controller.show_frame("PageTwo"))
        # button1.pack()
        # button2.pack()

        self.count = 0
        self.limit = 10
        self.is_active_lidars()
        self.lidar = False

    def is_active_lidars(self):
        print("is_active_lidars")
        if self.count == self.limit:  # TODO control
            self.control_status_label['text'] = "Motorlar kontrol ediliyor..."
            self.completion_bar_label['text'] += ":::"
            self.count = 0
            self.after(5, self.is_active_motors)
            return
        self.control_status_label['text'] = "Lidarlar kontrol ediliyor..."
        self.count += 1
        self.after(30, self.is_active_lidars)

    def is_active_motors(self):
        print("Motorlar kontrol ediliyor...")
        self.controller.rov_movement.initialize_motors()
        self.control_status_label['text'] = "IMU kalibre ediliyor..."
        self.completion_bar_label['text'] += ":::"
        self.after(50, self.is_active_imu)

    def is_active_imu(self):
        print("IMU kalibre ediliyor...")
        # LINE 65
        self.controller.rov_movement._initialize_imu()
        self.control_status_label['text'] = "Araç hazır..."
        self.completion_bar_label['text'] += ":::"
        self.after(50, self.controls_completed)

    def controls_completed(self):
        print("controls_completed")
        self.control_status_label['text'] = "Bütün kontroller tamamlandı."
        if self.count == self.limit:  # TODO control
            self.completion_bar_label['text'] += ":::"
            self.count = 0
            self.controller.show_frame("SelectMissionPage", 0)
            # self.controller.remove_frame(StartPage)
            self.destroy()
            return
        self.count += 1
        self.after(30, self.controls_completed)


class SelectMissionPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="skyblue", padx=10, pady=10)
        self.controller = controller

        manuel_missions_frame = tk.Frame(self, bg="skyblue")
        manuel_missions_frame.pack(side="top")
        manuel_missions_label = tk.Label(manuel_missions_frame, text="Manuel görevler", font=controller.title_font,
                                         bg="skyblue")
        manuel_missions_label.pack()

        mission_1_frame = tk.Frame(self, bg="skyblue")
        mission_1_frame.pack()
        mission_1_image = tk.PhotoImage(file="joystick.png")
        mission_1_button = tk.Button(mission_1_frame, text="Görev 1", image=mission_1_image, compound="top",
                                     command=lambda: controller.show_frame("ObservationPage", 1))
        mission_1_button.image = mission_1_image
        mission_1_button.pack()

        autonomous_missions_frame = tk.Frame(self, bg="skyblue")
        autonomous_missions_frame.pack(side="top", fill="y", pady=10)
        autonomous_missions_label = tk.Label(autonomous_missions_frame, text="Otonom görevler", compound="top",
                                             font=controller.title_font, bg="skyblue")
        autonomous_missions_label.pack()

        mission_2_frame = tk.Frame(self, bg="skyblue")
        mission_2_frame.pack(side='left', fill="x", padx=10, pady=10)
        mission_2_image = tk.PhotoImage(file="mission_2.png")
        mission_2_button = tk.Button(mission_2_frame, text="Görev 2", image=mission_2_image, compound="top",
                                     command=lambda: controller.show_frame("ObservationPage", 2))
        mission_2_button.image = mission_2_image
        mission_2_button.pack()

        mission_3_frame = tk.Frame(self, bg="skyblue")
        mission_3_frame.pack(side='right', fill="x", padx=10, pady=10)
        mission_3_image = tk.PhotoImage(file="mission_3.png")
        mission_3_button = tk.Button(mission_3_frame, text="Görev 3", image=mission_3_image, compound="top",
                                     command=lambda: controller.show_frame("ObservationPage", 3))
        mission_3_button.image = mission_3_image
        mission_3_button.pack()

        # label = tk.Label(self, text="This is page 1", font=controller.title_font)
        # label.pack(side="top", fill="x", pady=10)
        # button = tk.Button(self, text="Go to the start page",
        #                    command=lambda: controller.show_frame("StartPage"))
        # button.pack()


class ObservationPage(tk.Frame):

    def __init__(self, parent, controller):
        self.counter = 0
        tk.Frame.__init__(self, parent, bg='skyblue', padx=10, pady=10)
        self.controller = controller

        # Bileşenler
        components_frame = tk.Frame(self, highlightbackground="green", highlightthickness=1)
        tk.Label(components_frame, text='BİLEŞENLER', font=controller.title_font).grid(row=0, column=0, columnspan=5,
                                                                                       pady=(0, 15))
        tk.Label(components_frame, text="Motorlar: ").grid(row=1, column=0)
        tk.Label(components_frame, text="Hazır", width=8, bg='papaya whip').grid(row=1, column=1, pady=(0, 2))
        tk.Label(components_frame, text="Lidarlar: ").grid(row=2, column=0)
        tk.Label(components_frame, text="Hazır", width=8, bg='papaya whip').grid(row=2, column=1, pady=(0, 2))
        tk.Label(components_frame, text="Kameralar: ").grid(row=3, column=0)
        tk.Label(components_frame, text="Hazır", width=8, bg='papaya whip').grid(row=3, column=1, pady=(0, 2))
        tk.Label(components_frame, text="Joystick: ").grid(row=4, column=0)
        self.joystick_value_label = tk.Label(components_frame, text="Kapalı", width=8, bg='papaya whip')
        self.joystick_value_label.grid(row=4, column=1, pady=(0, 2))
        tk.Label(components_frame, text="Robotik kol: ").grid(row=5, column=0)
        tk.Label(components_frame, text="Kapalı", width=8, bg='papaya whip').grid(row=5, column=1, pady=(0, 2))
        tk.Label(components_frame, text="Imu: ").grid(row=6, column=0)
        self.imu_state_label = tk.Label(components_frame, text="Kapalı", width=8, bg='papaya whip')
        self.imu_state_label.grid(row=6, column=1, pady=(0, 2))
        components_frame.grid(row=0, column=0, padx=10)

        # MOTOR durumları
        motors_frame = tk.Frame(self, highlightbackground="green", highlightthickness=1)
        tk.Label(motors_frame, text='MOTORLAR', font=controller.title_font).grid(row=0, column=0, columnspan=5,
                                                                                 pady=(0, 15))
        center_row, center_col = 1 + 2, 2
        tk.Label(motors_frame, text='MOTOR', font='Helvetica 14 bold').grid(row=center_row, column=center_col)
        motor_labels = {'xy': {}, 'z': {}}
        for key, row, col in [('fl', -1, -1), ('fr', -1, +1), ('bl', +1, -1), ('br', +1, +1)]:
            motor_labels['xy'][key] = tk.Label(motors_frame, text=str(randint(-10, 10)), bg='papaya whip')
            motor_labels['z'][key] = tk.Label(motors_frame, text=str(randint(0, 0)), bg='papaya whip')
            motor_labels['z'][key].grid(row=center_row + row, column=center_col + col)
            motor_labels['xy'][key].grid(row=center_row + 2 * row, column=center_col + 2 * col)
        motors_frame.grid(row=0, column=1, padx=10)

        # LiDaR verileri
        lidars_frame = tk.Frame(self, highlightbackground="green", highlightthickness=1)
        tk.Label(lidars_frame, text='LIDARLAR', font=controller.title_font).grid(row=0, column=0, columnspan=3,
                                                                                 pady=(0, 15))
        self.lidar_labels = {'xy': {}, 'z': {}}
        center_r, center_c = 1 + 2, 1
        tk.Label(lidars_frame, text=" ").grid(row=center_r, column=center_c)
        for key, r, c in [('front', -1, 0), ('left', +1, -1), ('bottom', +1, 0), ('right', +1, +1)]:
            f = tk.Frame(lidars_frame)
            tk.Label(f, text=key.capitalize()).grid(row=0)
            self.lidar_labels[key] = tk.Label(f, text=str(randint(30, 180)) + 'cm', width=8, bg='papaya whip')
            self.lidar_labels[key].grid(row=1)
            f.grid(row=center_r + r, column=center_c + c, padx=5)

        tk.Label(lidars_frame, text='IMU', font=controller.title_font).grid(row=5, column=0, columnspan=3,
                                                                            pady=(15, 10))
        self.imu_labels = {}
        for key, r, c in [('x', 0, 0), ('y', 0, 1), ('z', 0, 2)]:
            f = tk.Frame(lidars_frame)
            tk.Label(f, text=key.capitalize()).grid(row=0)
            self.imu_labels[key] = tk.Label(f, text='_', width=8, bg='papaya whip')
            self.imu_labels[key].grid(row=1)
            f.grid(row=6 + r, column=c, padx=5)

        lidars_frame.grid(row=0, column=2, padx=10)

        # # KAMERALAR
        # cameras_frame = tk.Frame(self, bg='skyblue')
        # tk.Label(cameras_frame, text="Ön Kamera", width=40, bg='skyblue').grid(row=0, column=0, padx=10, pady=5)
        # self.left_camera_label = tk.Label(cameras_frame, text=" ")
        # self.left_camera_label.grid(row=1, column=0, padx=10)
        # tk.Label(cameras_frame, text="Alt Kamera", width=40, bg='skyblue').grid(row=0, column=1, padx=10, pady=5)
        # self.right_camera_label = tk.Label(cameras_frame, text=" ")
        # self.right_camera_label.grid(row=1, column=1, padx=10)
        # cameras_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=(70, 10))
        #
        # self.left_camera = CSI_Camera(output_file="left.avi")
        # self.right_camera = CSI_Camera(output_file="right.avi")
        # self.fps = FPS()
        # self.update_camera_thread()

        ports = {
            # "front": "/dev/ttyUSB0",
            # "left": "/dev/ttyUSB1",
            # "right": "/dev/ttyUSB2",
            # "bottom": "/dev/ttyTHS1"
        }
        self.rov_lidars = None
        if ports:
            self.rov_lidars = RovLidars(ports=ports, output_file="lidars.txt")
            self.rov_lidars.start()
            self.update_lidars_values()

        # IMU
        self.imu = self.controller.rov_movement.imu
        self.update_imu_values()

    def baslat(self):
        self.joystick_value_label["text"] = "Açık"
        if self.imu:
            self.imu_state_label["text"] = "Açık"

    def update_lidars_values(self):
        values = self.rov_lidars.get_values()
        try:
            for key in values:
                self.lidar_labels[key]["text"] = values[key][0]
        except Exception as ee:
            print("\n\n\n\n")
            print("Exception in update_lidars_values():")
            print(ee)
            print("\n\n\n\n")
        self.after(50, self.update_lidars_values)

    def update_imu_values(self):
        x, y, _ = self.imu.get_degree().get()
        self.imu_labels['x']["text"] = x
        self.imu_labels['y']["text"] = y
        _, _, z = self.imu.get_direction(absolute=False).get()
        self.imu_labels['z']["text"] = z
        self.after(200, self.update_imu_values)

    def update_cameras(self):
        _, left_frame = self.left_camera.read()
        _, right_frame = self.right_camera.read()

        # left_frame = imutils.resize(left_frame, width=480, height=360)
        left_cv2image = cv2.cvtColor(left_frame, cv2.COLOR_BGR2RGBA)
        left_img = Image.fromarray(left_cv2image)
        left_imgtk = ImageTk.PhotoImage(image=left_img)
        self.left_camera_label.imgtk = left_imgtk
        self.left_camera_label.configure(image=left_imgtk)

        # right_frame = imutils.resize(right_frame, width=480, height=360)
        right_cv2image = cv2.cvtColor(right_frame, cv2.COLOR_BGR2RGBA)
        right_img = Image.fromarray(right_cv2image)
        right_imgtk = ImageTk.PhotoImage(image=right_img)
        self.right_camera_label.imgtk = right_imgtk
        self.right_camera_label.configure(image=right_imgtk)
        self.fps.update()
        self.after(10, self.update_cameras)

    def update_camera_thread(self):
        self.left_camera.open(
            gstreamer_pipeline(sensor_id=0, sensor_mode=3, flip_method=0, display_height=270, display_width=360, ))
        self.left_camera.start()
        self.right_camera.open(
            gstreamer_pipeline(sensor_id=1, sensor_mode=3, flip_method=0, display_height=270, display_width=360, ))
        self.right_camera.start()

        if not self.left_camera.is_opened() or not self.right_camera.is_opened():
            # Cameras did not open, or no camera attached
            print(Exception("Unable to open any cameras"))
            return
        self.fps.start()
        self.update_cameras()

    def destroy(self):
        if self.left_camera.is_running() or self.right_camera.is_running():
            print("Kameralar kapatılıyor...")
            self.fps.stop()
            print("[ARAYUZ] elasped time: {:.2f}".format(self.fps.elapsed()))
            print("[ARAYUZ] approx. FPS: {:.2f}".format(self.fps.fps()))
            self.left_camera.stop()
            self.left_camera.release()
            self.right_camera.stop()
            self.right_camera.release()
            print("Kameralar kapatıldı...")

        if self.rov_lidars:
            self.rov_lidars.stop()

        self.after(30, super().destroy)


def update_from_joystick(rov_movement):
    print("Thrade oluşturuldu")

    # Joystick variables are creating
    joystick_values = {}
    Joy_obj = Joystick()
    joystick_values.update(Joy_obj.shared_obj.ret_dict)
    # Joystick variables are created

    global arayuz_running
    while arayuz_running:
        Joy_obj.while_initializer()
        if Joy_obj.joystick_count:
            Joy_obj.for_initializer()
            Joy_obj.joysticks()
            joystick_values = Joy_obj.shared_obj.ret_dict

            if rov_movement:
                # Robotik kol hareketi
                arm_status = joystick_values["robotik_kol"]
                arm_status = True if arm_status == 1 else (False if arm_status == -1 else None)
                rov_movement.toggle_arm(arm_status)

                # XYZ hareketi
                pf = joystick_values["power_factor"]
                zpf = joystick_values["zpf"]
                xy_power = joystick_values["xy_plane"]["magnitude"] * pf * 100
                z_power = joystick_values["z_axes"] * pf * zpf * 60
                turn_power = joystick_values["turn_itself"] * pf * 100
                tilt_degree = joystick_values["tilt_degree"]
                if tilt_degree:
                    rov_movement.go_xyz_with_tilt(xy_power, z_power, turn_power, tilt_degree=tilt_degree)
                else:
                    xy_angle = joystick_values["xy_plane"]["angel"]
                    rov_movement.go_xy_and_turn(xy_power, xy_angle, turn_power)
                    rov_movement.go_z_bidirectional(z_power)

        sleep(0.04)
        Joy_obj.clock.tick(50)


if __name__ == "__main__":
    print("__main__")
    app = SampleApp()
    app.mainloop()
