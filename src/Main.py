import PugRestCaller
import ToxicFilter
import UnfoundMatch
import Merge
import os
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: \n\tPugRest -h\n\tPugRest --help\n\tPugRest <path>")
        return

    if (sys.argv[1] == "-h") | (sys.argv[1] == "--help"):
        print("This program inputs the directory path to a set of .csv files containing the output from MFAssignR\n"
              "assignment and classifies them as different toxicity classes, safe, or other classifications\n"
              "related to the functioning of this program.\n")
        return

    os.chdir(sys.argv[1])

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
                # PugRestCaller.main(cmpd, sign)
                # ToxicFilter.toxfilter(cmpd, f"{sign} SetToxic")
                UnfoundMatch.match(cmpd, sign)
            except Exception as e:
                print(e)
                pass
    Merge.unfoundMerge()
    Merge.uncheckedMerge()
    Merge.toxicMerge()
    ToxicFilter.toxfilter(".", "totalTox")

if __name__ == "__main__":
    main()