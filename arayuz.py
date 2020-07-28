import tkinter as tk
from random import randint
from tkinter import font  as tkfont


class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

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

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def remove_frame(self, page_name):
        '''Remove a frame for the given page name'''
        self.frames.pop(page_name, None)


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
        self.control_status_label['text'] = "Lidarlar kontrol ediliyor..."
        if self.count == self.limit:  # TODO control
            self.completion_bar_label['text'] += ":::"
            self.count = 0
            self.after(5, self.is_active_motors)
            return
        self.count += 1
        self.after(30, self.is_active_lidars)

    def is_active_motors(self):
        print("is_active_motors")
        self.control_status_label['text'] = "Motorlar kontrol ediliyor..."
        if self.count == self.limit:  # TODO control
            self.completion_bar_label['text'] += ":::"
            self.count = 0
            self.after(5, self.controls_completed)
            return
        self.count += 1
        self.after(30, self.is_active_motors)

    def controls_completed(self):
        print("controls_completed")
        self.control_status_label['text'] = "Bütün kontroller tamamlandı."
        if self.count == self.limit:  # TODO control
            self.completion_bar_label['text'] += ":::"
            self.count = 0
            self.controller.show_frame("SelectMissionPage")
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
                                     command=lambda: controller.show_frame("ObservationPage"))
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
                                     command=lambda: controller.show_frame("ObservationPage"))
        mission_2_button.image = mission_2_image
        mission_2_button.pack()

        mission_3_frame = tk.Frame(self, bg="skyblue")
        mission_3_frame.pack(side='right', fill="x", padx=10, pady=10)
        mission_3_image = tk.PhotoImage(file="mission_3.png")
        mission_3_button = tk.Button(mission_3_frame, text="Görev 3", image=mission_3_image, compound="top",
                                     command=lambda: controller.show_frame("ObservationPage"))
        mission_3_button.image = mission_3_image
        mission_3_button.pack()

        # label = tk.Label(self, text="This is page 1", font=controller.title_font)
        # label.pack(side="top", fill="x", pady=10)
        # button = tk.Button(self, text="Go to the start page",
        #                    command=lambda: controller.show_frame("StartPage"))
        # button.pack()


class ObservationPage(tk.Frame):

    def __init__(self, parent, controller):
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
        tk.Label(components_frame, text="Kapalı", width=8, bg='papaya whip').grid(row=4, column=1, pady=(0, 2))
        tk.Label(components_frame, text="Robotik kol: ").grid(row=5, column=0)
        tk.Label(components_frame, text="Kapalı", width=8, bg='papaya whip').grid(row=5, column=1, pady=(0, 2))
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
        lidar_labels = {'xy': {}, 'z': {}}
        center_r, center_c = 1 + 2, 1
        tk.Label(lidars_frame, text=" ").grid(row=center_r, column=center_c)
        for key, r, c in [('front', -1, 0), ('left', +1, -1), ('bottom', +1, 0), ('right', +1, +1)]:
            f = tk.Frame(lidars_frame)
            tk.Label(f, text=key.capitalize()).grid(row=0)
            lidar_labels[key] = tk.Label(f, text=str(randint(30, 180)) + 'cm', width=8, bg='papaya whip')
            lidar_labels[key].grid(row=1)
            f.grid(row=center_r + r, column=center_c + c, padx=5)
        lidars_frame.grid(row=0, column=2, padx=10)

        # KAMERALAR
        cameras_frame = tk.Frame(self, bg='skyblue')
        tk.Label(cameras_frame, text="Ön Kamera", width=40, bg='skyblue').grid(row=0, column=0, padx=10, pady=5)
        tk.Label(cameras_frame, text=" ", width=40, height=16).grid(row=1, column=0, padx=10)
        tk.Label(cameras_frame, text="Alt Kamera", width=40, bg='skyblue').grid(row=0, column=1, padx=10, pady=5)
        tk.Label(cameras_frame, text=" ", width=40, height=16).grid(row=1, column=1, padx=10)
        cameras_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=(70, 10))


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
