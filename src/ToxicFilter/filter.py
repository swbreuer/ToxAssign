from ToxicFilter import PugRestCaller
from ToxicFilter import ToxFormat
from ToxicFilter import UnfoundMatch
from ToxicFilter import Merge
import os
import sys

def main(filepath):

    os.chdir(filepath)

    for root, subDirs, files in os.walk("."):
        for file in files:

            sign = file[0]
            cmpd = file.replace(f"{sign}ESI ", "").replace(".csv", "")

            if (file[-1] != "v") | ((sign != "-") & (sign != "+")):
                continue

            if not os.path.exists(cmpd):
                os.mkdir(cmpd)

            try:
                print(f"{sign}{cmpd}")
                PugRestCaller.main(cmpd, sign)
                ToxicFilter.toxfilter(cmpd, f"{sign} SetToxic")
                UnfoundMatch.match(cmpd, sign)
            except Exception as e:
                print(e)
                pass
    Merge.unfoundMerge()
    Merge.uncheckedMerge()
    Merge.toxicMerge()
    ToxFormat.toxfilter(".", "totalTox")

if __name__ == "__main__":
    main()
