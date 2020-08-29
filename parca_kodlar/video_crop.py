import cv2


def crop_frame(frame, new_area):
    return frame[new_area[0][0]:new_area[0][1], new_area[1][0]:new_area[1][1]]


def cropped_size(video, new_area):
    return int(video.get(3) - (new_area[1][0] - new_area[1][1])), int(video.get(4) - (new_area[0][0] - new_area[0][1]))


if __name__ == '__main__':
    new_area = ((40, -3), (65, -90))
    video = cv2.VideoCapture("video/cember.mp4")

    # print(video.get(cv2.CAP_PROP_FPS))
    # print(cropped_size(video, new_area))
    writer = cv2.VideoWriter(
        "video/cember_crop.mp4", cv2.VideoWriter_fourcc(*'mp4v'), video.get(cv2.CAP_PROP_FPS),
        cropped_size(video, new_area)
    )

    # PROGRESS BAR
    try:
        from progressbar import ProgressBar

        bar = ProgressBar(max_value=int(video.get(cv2.CAP_PROP_FRAME_COUNT)))
    except:
        pass

    ret, frame = video.read()
    # print(crop_frame(frame, new_area).shape)
    while ret:
        writer.write(crop_frame(frame, new_area))
        ret, frame = video.read()

        # PROGRESS BAR
        try:
            bar.update(bar.value + 1)
        except:
            pass

    video.release()
    writer.release()
