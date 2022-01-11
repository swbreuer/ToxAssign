#!/usr/bin/env python
from ToxAssign import PubChemClass
from ToxAssign import Format
from ToxAssign import Match
from ToxAssign import Merge
from ToxAssign import Writer
import os
import logging
import PubChem

__author__ = "Samuel Breuer"
__copyright__ = "Copyright 2021, MOST"
__credits__ = ["Samuel Breuer", "Simeon Schum", "Joshua Pearce", "Lucy Toppen"]
__license__ = "MIT"
__version__ = "0.2.0"
__maintainer__ = "Samuel Breuer"
__email__ = "swbreuer@mtu.edu"
__status__ = "Development"


def automate(filepath):
    pub = PubChemClass()
    form = Format(pub)
    mat = Match(pub)
    os.chdir(filepath)
    # run against all data files in folder
    for root, subDirs, files in os.walk("."):
        for file in files:
            pub = PubChemClass()
            format = Format()
            match = Match()
            sign = file[0]
            cmpd = file.replace(f"{sign}ESI ", "").replace(".csv", "")

            # all data files are .csv and contain either - or + as their first character, all other files are not data
            if (file[-1] != "v") | ((sign != "-") & (sign != "+")):
                continue

            # create storage folder
            if not os.path.exists(cmpd):
                os.mkdir(cmpd)
            # call the pubchem record, classify, sort toxic records, match unfound records

            try:
                print(f"{sign}{cmpd}")
                pub.main(cmpd, sign)
                form.toxfilter()
                mat.match()
                Writer.write_chem(cmpd,sign, form, mat)

            except Exception as e:
                logging.exception(e)
                pass

    # collate all universal records into total files
    Merge.unfound_merge()
    Merge.unchecked_merge()
    Merge.toxic_merge()
    Format.toxfilter(".", "totalTox")


def main():
    automate("/test")


if __name__ == "__main__":
    automate("../test")
