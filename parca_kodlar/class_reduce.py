import os
import pathlib

INPUT_LABELS_DIRECTORY = "YoloLabels/002"
OUTPUT_LABELS_DIRECTORY = "YoloLabels/002_reduced"

if __name__ == '__main__':
    pathlib.Path(OUTPUT_LABELS_DIRECTORY).mkdir(parents=True, exist_ok=True)
    file_names = os.listdir(INPUT_LABELS_DIRECTORY)
    file_names.sort()
    for txt_name in file_names:
        rf = open(INPUT_LABELS_DIRECTORY + "/" + txt_name, "r")
        line = rf.readline().split()
        print(line)
        if line:
            line[0] = "0"
            print(line)
            print(" ".join(line))
        rf.close()
        wf = open(OUTPUT_LABELS_DIRECTORY + "/" + txt_name, "w")
        wf.write(" ".join(line))
        wf.close()
