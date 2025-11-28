import os
import shutil
import pytest
import cmost as cst


@pytest.fixture(scope="session")
def obsid_txts():
    with open("tests/data/obsids.txt") as f:
        list = [i.strip() for i in f.readlines()]
        return list


@pytest.mark.skip("ci/ci is not supported")
def test_download_fits(obsid_txts):
    obsid_txts: list
    fits_downloader = cst.FitsDownloader("dr7", "v2.0")

    for o in obsid_txts:
        fits_downloader.download_fits(o)

    assert os.path.exists("dr7_v2.0")
    assert len(os.listdir("dr7_v2.0")) == len(obsid_txts)
    shutil.rmtree("dr7_v2.0")


@pytest.mark.skip("ci/ci is not supported")
def test_download_fits_MultThread(obsid_txts):
    obsid_txts: list
    fits_downloader = cst.FitsDownloader("dr7", "v2.0")

    fits_downloader.download_fits_use_MultiThreading(obsid_txts)

    assert os.path.exists("dr7_v2.0")
    assert len(os.listdir("dr7_v2.0")) == len(obsid_txts)
    shutil.rmtree("dr7_v2.0")
