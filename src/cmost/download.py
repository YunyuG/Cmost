# Copyright(C) YunyuG 2025. All rights reserved.
# Created at Sat Nov 15 21:14:23 CST 2025.

__all__ = ["FitsDownloader"]

import os
import threading
from http.client import HTTPResponse
from urllib.request import Request, urlopen


class FitsDownloader:
    def __init__(
        self,
        dr_version: str,
        sub_version: str,
        *,
        is_dev: bool = False,
        is_med: bool = False,
        save_dir: str | None = None,
        TOKEN: str | None = None,
    ):
        self.dr_version = dr_version
        self.sub_version = sub_version
        self.is_dev = is_dev
        self.TOKEN = TOKEN if TOKEN else ""
        self.is_med = is_med
        self.save_dir = (
            f"{self.dr_version}_{self.sub_version}" if save_dir is None else save_dir
        )
        self.band()

    def band(self):
        # The construction of the download link refers to the official LAMOST tool `pylamost`.
        # https://github.com/fandongwei/pylamost
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

    def download_fits_use_MultThreading(
        self, obsid_list: list, threading_nums: int = 4
    ):
        threads: list[_FitsDownloaderThread] = []
        every_block_task_num, change_task_num = divmod(len(obsid_list), threading_nums)

        for i in range(threading_nums):
            start_index = i * every_block_task_num
            end_index = (
                (i + 1) * every_block_task_num + change_task_num
                if i == threading_nums - 1
                else (i + 1) * every_block_task_num
            )
            thread = _FitsDownloaderThread(self, obsid_list[start_index:end_index])
            threads.append(thread)

        try:
            for thread in threads:
                thread.start()

            for thread in threads:
                while thread.is_alive():
                    thread.join(timeout=1)

        except KeyboardInterrupt:
            for thread in threads:
                thread.shutdown()
            for thread in threads:
                thread.join(timeout=2)

    def download_fits(self, obsid: int) -> None:
        url = f"{self.public_url}?obsid={obsid}&TOKEN={self.TOKEN}"
        request = Request(url, method="GET",unverifiable=True)
        # FIXME: The ftp server of LAMOST may occurs some errors.
        response: HTTPResponse = urlopen(request)
        # You should set timeout whether the thread will be locked
        fits_name = response.headers["Content-Disposition"].split("=")[1]

        fits_path = os.path.join(self.save_dir, fits_name)
        with open(fits_path, "wb+") as file:
            while True:
                chunk = response.read(8192 * 4)
                if not chunk:
                    break
                file.write(chunk)


class _FitsDownloaderThread(threading.Thread):
    def __init__(self, fits_downloader: "FitsDownloader", obsid_list: list[str]):
        self.fits_downloader = fits_downloader
        self.obsid_list = obsid_list
        self.is_run = True

        super().__init__(daemon=True)

    def run(self):
        for obsid in self.obsid_list:
            if not self.is_run:
                break
            self.fits_downloader.download_fits(obsid)

    def shutdown(self):
        self.is_run = False
