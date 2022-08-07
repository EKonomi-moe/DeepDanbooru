from pathlib import Path
from time import sleep
from os import system
from threading import Thread

def thread_download(i, download_path, donecheck_path, queue):
    system(f"rsync --recursive --verbose rsync://176.9.41.242:873/danbooru2021/original/{str(i).zfill(4)}/ {download_path}/{str(i).zfill(4)}/")
    system(f"echo {str(i)} >> {donecheck_path}\n")
    queue.pop(str(i))
    pass


def download_image(download_path, start_range, end_range=999, threads=5):
    """
    Download image from danbooru.
    """
    download_path = Path(download_path)
    download_path.mkdir(parents=True, exist_ok=True)
    donecheck_path = download_path / "donecheck.txt"
    donecheck_path.touch()
    queue = {}
    for i in range(start_range, end_range+1):
        f = open(donecheck_path, "r")
        if str(i) in f.read():
            f.close()
            continue
        f.close()

        while True:
            if len(queue) < threads:
                thr = Thread(target=thread_download, args=(i, download_path, donecheck_path, queue))
                thr.daemon = True
                thr.start()
                queue.update({str(i): thr})
                break
            else:
                sleep(0.3)
    pass

