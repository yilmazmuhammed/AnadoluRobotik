from datetime import datetime

import cv2
import numpy


def mavi_silme(frame):
    ret = frame.copy()
    mavi_bgr = (215, 205, 140)
    for y in range(480):
        for x in range(720):
            m = ret[y][x][2] + (255-mavi_bgr[2])
            n = ret[y][x][1] + (255-mavi_bgr[1])
            o = ret[y][x][0] + (255-mavi_bgr[0])
            m = 255 if m > 255 else m
            n = 255 if n > 255 else n
            o = 255 if o > 255 else o
            ret[y][x][0] = m
            ret[y][x][1] = n
            ret[y][x][2] = o
    return ret


def gri(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def thresh(frame):
    # ret,th1 = cv2.threshold(frame,127,255,cv2.THRESH_BINARY)
    # th2 = cv2.adaptiveThreshold(frame,255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,7,5)
    # ret, thresh = cv2.threshold(frame,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    th1 = cv2.adaptiveThreshold(frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return th1


if __name__ == '__main__':
    frame: numpy.ndarray = cv2.imread("img/circle/100.jpg")
    # t = datetime.now()
    # frame2 = mavi_silme(frame)
    # gurultusuz = cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 13, 15)
    # gray_img = cv2.cvtColor(gurultusuz, cv2.COLOR_BGR2GRAY)
    # gurultusuz2 = mavi_silme(gurultusuz)
    # print("Süre:", datetime.now() - t)
    #
    cv2.imshow("Frame", frame)
    cv2.imshow("Frame2", frame[40:-3, 65:-90])
    # cv2.imshow("frame_mavisiz", frame2)
    # cv2.imshow("gurultusuz", gurultusuz)
    # cv2.imshow("gurultusuz_mavisiz", gurultusuz2)
    # cv2.imshow("gurultusuz_gri", gray_img)
    # cv2.imshow("gurultusuz_mavisiz_thresh", thresh(gri(gurultusuz2)))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
