import glob
import os
import pathlib

import cv2


def crop_frame(img, crop):
    return img[crop[0][0]:crop[0][1], crop[1][0]:crop[1][1]]


def change_range(value, new_range):
    return (value - new_range[0]) / (new_range[1] - new_range[0])


def crop_label(coordinates, crop, size):
    yatay_s = change_range(crop[1][0], (0, size[1] - 1))
    yatay_f = change_range((size[1] - 1) - abs(crop[1][1]), (0, size[1] - 1))
    dikey_s = change_range(crop[0][0], (0, size[0] - 1))
    dikey_f = change_range((size[0] - 1) - abs(crop[0][1]), (0, size[0] - 1))
    # print(yatay_s, yatay_f, dikey_s, dikey_f)

    merkez_yatay, merkez_dikey, yatay_uzunluk, dikey_uzunluk = coordinates
    sol = change_range(merkez_yatay - yatay_uzunluk / 2, (yatay_s, yatay_f))
    sag = change_range(merkez_yatay + yatay_uzunluk / 2, (yatay_s, yatay_f))
    ust = change_range(merkez_dikey - dikey_uzunluk / 2, (dikey_s, dikey_f))
    alt = change_range(merkez_dikey + dikey_uzunluk / 2, (dikey_s, dikey_f))
    # print(sol, sag, ust, alt)

    koseler = [sol, sag, ust, alt]
    koseler = [0 if i < 0 else i for i in koseler]
    koseler = [1 if i > 1 else i for i in koseler]
    # print(koseler)

    sol, sag, ust, alt = koseler
    ret = [(sag - sol) / 2 + sol, (alt - ust) / 2 + ust, (sag - sol), (alt - ust)]
    # print(ret)
    return ret


if __name__ == '__main__':
    new_area = ((40, -3), (65, -90))
    old_size = (480, 720)

    photo_extension = "jpg"
    # read_photos_directory = os.path.abspath("img/circle")
    # read_labels_directory = os.path.abspath("img/circle")
    # write_photos_directory = os.path.abspath("img/circle_crop")
    # write_labels_directory = os.path.abspath("img/circle_crop/Label")
    # photo_extension = input("Extension of photos:")
    read_photos_directory = os.path.abspath(input("Directory to read photos:"))
    read_labels_directory = os.path.abspath(input("Directory to read labels:"))
    write_photos_directory = os.path.abspath(input("The directory to save photos:"))
    write_labels_directory = os.path.abspath(input("The directory to save labels:"))

    pathlib.Path(write_photos_directory).mkdir(parents=True, exist_ok=True)
    pathlib.Path(write_labels_directory).mkdir(parents=True, exist_ok=True)
    os.chdir(read_photos_directory)
    photos = glob.glob('*.' + photo_extension)
    photos.sort()

    try:
        from progressbar import ProgressBar
        bar = ProgressBar(max_value=len(photos))
    except:
        pass
    for photo in photos:
        frame = cv2.imread(read_photos_directory + "/" + photo, cv2.IMREAD_COLOR)
        cv2.imwrite(write_photos_directory + "/" + photo, crop_frame(frame, new_area))

        txt_name = photo.split("." + photo_extension)[0] + ".txt"
        coordinates = open(read_labels_directory + "/" + txt_name,
                           "r").readline()

        if len(coordinates):
            coordinates = coordinates.split(" ")
            new_values = [str(round(i, 6)) for i in
                          crop_label([float(i) for i in coordinates[1:]], new_area, old_size)]
            new_values = coordinates[0] + new_values
        else:
            new_values = [""]

        wf = open(write_labels_directory + "/" + txt_name, "w")
        wf.write(" ".join(new_values))
        wf.close()

        try: bar.update(bar.value+1)
        except: pass
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
