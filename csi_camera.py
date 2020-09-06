from datetime import datetime
from pathlib import Path
from time import time

import cv2
import threading

from imutils.video import FPS


class CSI_Camera:
    def __init__(self, output_file=""):
        # Initialize instance variables
        # OpenCV video capture element
        self.video_capture = None
        # The last captured image from the camera
        self.frame = None
        self.grabbed = False
        # The thread where the video capture runs
        self.read_thread = None
        self.read_lock = threading.Lock()
        self.running = False

        self.output = None
        self.output_file_name = None
        self.output_thread = None
        self.output_lock = threading.Lock()
        if output_file != "":
            Path("logs").mkdir(parents=True, exist_ok=True)
            self.output_file_name = "logs/" + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + "_camera_" + output_file

    def open(self, camera, is_gstreamer=True):
        try:
            if is_gstreamer:
                # For save video
                # https://forums.developer.nvidia.com/t/how-to-save-video-with-2-camera-pi-with-jeston-nano/145882
                # gst-launch-1.0 nvarguscamerasrc sensor-id=0 num-buffers=300 !
                # 'video/x-raw(memory:NVMM), width=1280, height=720, framerate=30/1' ! nvtee !
                # omxh264enc bitrate=20000000 ! qtmux ! filesink location=video.mp4
                self.video_capture = cv2.VideoCapture(camera, cv2.CAP_GSTREAMER)
            else:
                self.video_capture = cv2.VideoCapture(camera)
            if self.output_file_name:
                self.output = cv2.VideoWriter(
                    self.output_file_name, cv2.VideoWriter_fourcc(*'XVID'), 20.0,
                    (int(self.video_capture.get(3)), int(self.video_capture.get(4)))
                )

        except RuntimeError:
            self.video_capture = None
            print("Unable to open camera")
            print("Pipeline: " + camera)
            return
        # Grab the first frame to start the video capturing
        self.grabbed, self.frame = self.video_capture.read()

    def start(self):
        if self.running:
            print('Video capturing is already running')
            return None
        # create a thread to read the camera image
        if self.video_capture is not None:
            self.running = True
            self.read_thread = threading.Thread(target=self.read_from_camera)
            self.read_thread.start()

            if self.output:
                self.output_thread = threading.Thread(target=self.write_to_file)
                self.output_thread.start()

        return self

    def stop(self):
        self.running = False
        if self.read_thread:
            self.read_thread.join()
        if self.output_thread:
            self.output_thread.join()

    def read_from_camera(self):
        # This is the thread to read images from the camera
        fps_ = FPS().start()
        while self.running:
            try:
                grabbed_, frame_ = self.video_capture.read()
                with self.read_lock:
                    self.grabbed = grabbed_
                    self.frame = frame_
                    if self.output_lock.locked():
                        self.output_lock.release()
                fps_.update()
            except RuntimeError:
                print("Could not read image from camera")
            # sleep(0.01)
        fps_.stop()
        print("[KAMERA] elasped time: {:.2f}".format(fps_.elapsed()))
        print("[KAMERA] approx. FPS: {:.2f}".format(fps_.fps()))

    def write_to_file(self):
        if not self.output:
            return
        fps_ = FPS().start()
        a = time()
        while self.running:
            self.output_lock.acquire()
            frame_ = self.frame.copy()
            b = time()
            fps2_ = 1 / (b - a)
            cv2.putText(frame_, str(datetime.now()), (5, 15), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 1,
                        cv2.LINE_AA)
            cv2.putText(frame_, "FPS: " + str(fps2_), (5, 30), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 1,
                        cv2.LINE_AA)
            a = time()
            self.output.write(frame_)
            fps_.update()
        fps_.stop()
        print("[KAYDETME] elasped time: {:.2f}".format(fps_.elapsed()))
        print("[KAYDETME] approx. FPS: {:.2f}".format(fps_.fps()))

    def read(self):
        with self.read_lock:
            frame_ = self.frame.copy()
            grabbed_ = self.grabbed
        return grabbed_, frame_

    def release(self):
        if self.video_capture is not None:
            self.video_capture.release()
            if self.output:
                self.output.release()
            self.video_capture = None
        # Now kill the thread
        if self.read_thread is not None:
            self.read_thread.join()
        if self.output_thread:
            self.output_thread.join()

    def is_opened(self):
        return self.video_capture and self.video_capture.isOpened()

    def is_running(self):
        return self.running and self.is_opened()

# Currently there are setting frame rate on CSI Camera on Nano through gstreamer
# Here we directly select sensor_mode 3 (1280x720, 59.9999 fps)
def gstreamer_pipeline(
        sensor_id=0,
        sensor_mode=3,
        capture_width=1280,
        capture_height=720,
        display_width=1280,
        display_height=720,
        framerate=30,
        flip_method=0,
):
    return (
            "nvarguscamerasrc sensor-id=%d sensor-mode=%d ! "
            "video/x-raw(memory:NVMM), "
            "width=(int)%d, height=(int)%d, "
            "format=(string)NV12, framerate=(fraction)%d/1 ! "
            "nvvidconv flip-method=%d ! "
            "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
            "videoconvert ! "
            "video/x-raw, format=(string)BGR ! appsink"
            % (
                sensor_id,
                sensor_mode,
                capture_width,
                capture_height,
                framerate,
                flip_method,
                display_width,
                display_height,
            )
    )


if __name__ == '__main__':
    # Create a VideoCapture object and read from input file
    # If the input is the camera, pass 0 instead of the video file name
    cap = CSI_Camera(output_file="out_thread.avi")
    # cap.open("http://192.168.1.36:4747/mjpegfeed?640x480", is_gstreamer=False)
    cap.open(gstreamer_pipeline())
    cap.start()

    # Check if camera opened successfully
    if not cap.video_capture.isOpened():
        print("Error opening video stream or file")

    fps = FPS().start()

    # Read until video is completed
    while cap.video_capture.isOpened():
        # Capture frame-by-frame
        grabbed, frame = cap.read()
        if not grabbed:
            break

        # Display the resulting frame
        cv2.imshow('Frame', frame)

        # Press Q on keyboard to  exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

        fps.update()

    # stop the timer and display FPS information
    fps.stop()
    print("[GORUNTULEME] elasped time: {:.2f}".format(fps.elapsed()))
    print("[GORUNTULEME] approx. FPS: {:.2f}".format(fps.fps()))

    # When everything done, release the video capture object
    cap.stop()
    cap.release()
    # output.release()

    # Closes all the frames
    cv2.destroyAllWindows()
