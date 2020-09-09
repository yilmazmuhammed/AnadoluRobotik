from time import sleep
from progressbar import progressbar, ProgressBar

# for i in progressbar(range(100)):
#     sleep(0.02)
if __name__ == '__main__':
    bar = ProgressBar(max_value=10)
    bar.update(0)
    bar.update(bar.value+1)
    sleep(3)
    bar.update(bar.value+1)
    sleep(3)
    bar.update(bar.value+1)
    sleep(3)
