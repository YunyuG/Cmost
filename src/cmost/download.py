import os
import time
import threading
from http.client import HTTPResponse
from urllib.request import Request,urlopen


class FitsDownloader:
    def __init__(
        self,
        dr_version: str,
        sub_version: str,
        *,
        is_dev:bool = False,
        is_med:bool =False,
        save_dir: str | None = None,
        TOKEN: str | None = None,
    ):
        self.dr_version = dr_version
        self.sub_version = sub_version
        self.is_dev = is_dev
        self.TOKEN = TOKEN if TOKEN else ""
        self.is_med = is_med
        self.save_dir = f"{self.dr_version}_{self.sub_version}" if save_dir is None else save_dir
        self.band()

    def band(self):
        """
        The construction of the download link refers to the official LAMOST tool `pylamost`.
            https://github.com/fandongwei/pylamost

        """
        resolution = "mrs" if self.is_med else "lrs"
        base_url = (
            "https://www2.lamost.org/openapi"
            if self.is_dev
            else "https://www.lamost.org/openapi"
        )
        url = f"{base_url}/{self.dr_version}/{self.sub_version}/{resolution}/spectrum/fits"
        self.public_url = url

        if not os.path.exists(self.save_dir):
            os.mkdir(self.save_dir)
    
    def download_fits_use_MultThreading(self,obsid_list:list
                                        ,threading_nums:int = 4
                                        ,seq_time:float | int = 3):
        task_over_event = threading.Event()
        task_over_event.clear()
        remove_lock = threading.Lock()
        def download():
            step = 0
            while len(obsid_list) > 0 and task_over_event.is_set():
                with remove_lock:
                    obsid = obsid_list.pop()
                self.download_fits(obsid)
                time.sleep(step % seq_time)
                step += 1
                

        threads = []
        for _ in range(threading_nums):
            thread = threading.Thread(target=download
                                      ,daemon=False)
            threads.append(thread)
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()

    def download_fits(self,obsid: int) -> None:
        url = f"{self.public_url}?obsid={obsid}&TOKEN={self.TOKEN}"
        request = Request(url,method="GET")
        response:HTTPResponse = urlopen(request)
        fits_name = response.headers["Content-Disposition"].split("=")[1]

        fits_path = os.path.join(self.save_dir,fits_name)
        with open(fits_path,"wb+") as file:
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                file.write(chunk)