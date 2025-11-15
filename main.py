# !/usr/bin/env python3
# Copyright (C) 2025 YunyuG
import cmost as cst


f = cst.FitsDownloader("dr7","v2.0")


with open("obsids.txt") as file:
    table = [i.strip() for i in file.readlines()]

f.download_fits_use_MultThreading(obsid_list=table,threading_nums = 6)