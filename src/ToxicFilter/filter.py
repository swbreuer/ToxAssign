#!/usr/bin/env python
from ToxicFilter import PugRestCaller
from ToxicFilter import ToxFormat
from ToxicFilter import UnfoundMatch
from ToxicFilter import Merge
import os
import logging

__author__ = "Samuel Breuer"
__copyright__ = "Copyright 2021, MOST"
__credits__ = ["Samuel Breuer", "Simeon Schum", "Joshua Pearce", "Lucy Toppen"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Samuel Breuer"
__email__ = "swbreuer@mtu.edu"
__status__ = "Development"


def main(filepath):
    os.chdir(filepath)
    # run against all data files in folder
    for root, subDirs, files in os.walk("."):
        for file in files:
            sign = file[0]
            cmpd = file.replace(f"{sign}ESI ", "").replace(".csv", "")
            # all data files are .csv and contain either - or + as their first character, al other files are not data
            if (file[-1] != "v") | ((sign != "-") & (sign != "+")):
                continue
            # create storage folder
            if not os.path.exists(cmpd):
                os.mkdir(cmpd)
            # call the pubchem record, classify, sort toxic records, match unfound records
            try:
                print(f"{sign}{cmpd}")
                PugRestCaller.main(cmpd, sign)
                ToxFormat.toxfilter(cmpd, f"{sign} SetToxic")
                UnfoundMatch.match(cmpd, sign)
            except Exception as e:
                logging.exception(e)
                pass
    # collate all universal records into total files
    Merge.unfoundMerge()
    Merge.uncheckedMerge()
    Merge.toxicMerge()
    ToxFormat.toxfilter(".", "totalTox")


if __name__ == "__main__":
    main()
