import cv2

INPUT_FILENAME = 'video/cember.mp4'
OUTPUT_FILENAME = 'video/cember_gray.avi'

if __name__ == '__main__':

    reader = cv2.VideoCapture(INPUT_FILENAME)

    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    fps = reader.get(cv2.CAP_PROP_FPS)
    width, height = int(reader.get(3)), int(reader.get(4))
    writer = cv2.VideoWriter(OUTPUT_FILENAME, fourcc, fps, (width, height), 0)

    ret, frame = reader.read()
    counter = 1
    while ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        writer.write(frame)
        print(counter)
        ret, frame = reader.read()
        counter += 1

    reader.release()
    writer.release()
    print('Successfully completed')
