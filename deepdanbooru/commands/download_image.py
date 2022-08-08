class dummy():
    def __init__(self):
        pass

from pathlib import Path
from time import sleep
from os import system
from threading import Thread

def thread_download(i, download_path_str, donecheck_path, queue, retry = False):
    if queue.exit: return
    download_path_str = download_path_str.replace("\\", "/")
    if download_path_str[-1] == "/": download_path_str = download_path_str[:-1]
    rtncode = system(f"rsync -avz --delete rsync://176.9.41.242:873/danbooru2021/original/{str(i).zfill(4)}/ {download_path_str}/{str(i).zfill(4)}/")
    if rtncode == 0:
        system(f"echo {str(i)} >> {donecheck_path}\n")
        queue.queue.pop(str(i))
    elif rtncode == 20:
        queue.exit = True
        return
    else:
        print(f"Error {i} :: {rtncode}")
        if retry: return
        thread_download(i, download_path_str, donecheck_path, queue, True)
    pass


def download_image(download_path_str, start_range, end_range=999, threads=5):
    """
    Download image from danbooru.
    """
    download_path = Path(download_path_str)
    download_path.mkdir(parents=True, exist_ok=True)
    donecheck_path = download_path / "donecheck.txt"
    donecheck_path.touch()
    queue = dummy()
    queue.queue = {}
    queue.exit = False
    for i in range(start_range, end_range+1):
        f = open(donecheck_path, "r")
        if str(i) in f.read():
            f.close()
            continue
        f.close()
        try:
            while True:
                if queue.exit: return
                if len(queue.queue) < threads:
                    thr = Thread(target=thread_download, args=(i, download_path_str, donecheck_path, queue))
                    thr.daemon = True
                    thr.start()
                    queue.queue.update({str(i): thr})
                    break
                else:
                    sleep(0.3)
        except KeyboardInterrupt:
            queue.exit = True
            return
        
    while True:
        if len(queue.queue) == 0:
            break
        sleep(0.3)
        
    pass

