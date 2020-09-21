import glob
import os

from PIL import Image


def resize_image(input_file_name, output_file_name, size):
    """
    :param input_file_name:
    :param output_file_name:
    :param size: width, height
    :return:
    """
    try:
        im = Image.open(input_file_name)
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(output_file_name, "JPEG")
    except IOError as ioe:
        print("cannot create thumbnail for '%s'" % input_file_name)
        raise ioe


if __name__ == '__main__':
    directory = "/home/myilmaz/İndirilenler/BBox-Label-Tool-multi-class/Images/011/"
    file_list = glob.glob(directory + '*.jpg')
    file_list.sort()
    for file_name in file_list:
        file_name = os.path.basename(file_name)
        output_name = os.path.splitext(file_name)[0] + ".JPG"
        print("Input:", file_name, "\t->\t", output_name)
        resize_image(directory + file_name, directory + output_name, (900, 550))
