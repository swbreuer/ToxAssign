#!/usr/bin/env python
import pandas as pd
from ToxAssign import Format
import os
import logging


# collate unfound files together
def unfound_merge():
    merge_main("UnfoundCopy", "Unfound")


# collate unchecked files together
def unchecked_merge():
    print("---- UNCHECKED MERGE ----")
    merge_main("Unchecked", "Unchecked")


# collate toxic files together
def toxic_merge():
    print("---- TOXIC MERGE ----")
    checked = pd.DataFrame(columns=['name', 'toxicity'])

    for subDir in os.scandir("."):
        # track whether directory has changed
        chdir = False
        # merge files into one object
        try:
            os.chdir(f"./{subDir.name}")
            chdir = True
            # read in toxic file
            unfound = pd.read_csv(f"./+ SetToxic.txt", delimiter="\t",
                                  engine='python', names=["name", "toxicity"])
            # merge unfound into checked
            checked = unfound.merge(checked, how="outer", on="name")
            # read in toxic file
            unfound = pd.read_csv(f"./+ SetToxic.txt", delimiter="\t",
                                  engine='python', names=["name", "toxicity"])
            # repeat
            checked = unfound.merge(checked, how="outer", on="name")
            os.chdir("../src")
            chdir = False
        except Exception as e:
            logging.exception(e)
            if chdir:
                os.chdir("../src")

    # write new collated object to file

    with open(f"./totalTox.txt", "w+") as fTotalTox:
        for index, value in checked.iterrows():
            fTotalTox.write(str(value["name"]) + "\t" + str(value["toxicity"]) + "\n")
    # format new collated file
    Format.toxfilter(".", "totalTox")


def merge_main(infile, outfile):
    checked = pd.DataFrame(columns=['Compound'])

    for subdir in os.scandir("."):

        # merge files into one object
        try:
            os.chdir(f"./{subdir}")
            # read in toxic file
            unfound = pd.read_csv(f"./+ Set{infile}.txt", delimiter="\t", engine='python', names=["Compound"])
            # merge unfound into checked
            checked = unfound.merge(checked, how="outer")
            # repeat
            unfound = pd.read_csv(f"./- Set{infile}.txt", delimiter="\t", engine='python', names=["Compound"])
            checked = unfound.merge(checked, how="outer")
        finally:
            # move out of dir at end
            os.chdir("../src")

    # write object to file
    print(os.getcwd())
    with open(f"./total{outfile}.txt", "w+") as fTotalUnfound:
        for index, value in checked.iterrows():
            fTotalUnfound.write(str(value["Compound"]) + "\n")
