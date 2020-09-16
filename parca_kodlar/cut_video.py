import cv2

INPUT_FILENAME = 'video/cember_gray.avi'
OUTPUT_FILENAME = 'video/ccember.mp4'
START_SECONDS = 10
FINISH_SECOND = 20

if __name__ == '__main__':

    reader = cv2.VideoCapture(INPUT_FILENAME)

    # fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = reader.get(cv2.CAP_PROP_FPS)
    width, height = int(reader.get(3)), int(reader.get(4))
    writer = cv2.VideoWriter(OUTPUT_FILENAME, fourcc, fps, (width, height))

    ret, frame = reader.read()
    counter = 1

    for i in range(int(fps)*START_SECONDS):
        if not ret:
            break
        ret, frame = reader.read()
        print(counter)
        counter += 1

    for i in range(int(fps)*(FINISH_SECOND-START_SECONDS)):
        writer.write(frame)
        if not ret:
            break
        ret, frame = reader.read()
        print(counter)
        counter += 1

    reader.release()
    writer.release()
    print('Successfully completed')
