#!/usr/bin/env python
import pandas as pd
import os


def match(compound, sign):
    print("---- UNFOUND MATCH ----")
    unfound = pd.read_csv(f"./{compound}/{sign} SetUnfound.txt", delimiter="\t", engine='python', names=["name"])
    found = pd.read_csv("Remove.csv")

    unfound.name = unfound.name.astype(str)
    found.compound = found.compound.astype(str)
    found_comp = unfound.merge(found, right_on="compound", left_on="name", how="inner")
    set_safe = found_comp
    set_safe = set_safe[(set_safe.Safety == "safe") | (set_safe.Safety == "flavoring agent")
                        | (set_safe.Safety == "fragrance") | (set_safe.Safety == "supplement")]
    found_comp = found_comp[~found_comp.compound.isin(set_safe.compound)]
    set_unfound = set()
    set_unfound.update(unfound[~unfound.name.isin(found.compound)])

    with open(f"./{compound}/{sign} SetFound.txt", "w+") as fSetFound:
        for index, value in found_comp.iterrows():
            fSetFound.write(str(value["compound"]) + ",\t" + str(value["alias"]) + ",\t" + str(value["Safety"]) + "\n")
        fSetFound.write("\n========= SAFE =========\n\n")
        for index, value in set_safe.iterrows():
            fSetFound.write(str(value["compound"]) + ",\t" + str(value["alias"]) + ",\t" + "\n")

    with open(f"./{compound}/{sign} SetUnfoundCopy.txt", "w+") as fSetUnfound:
        for element in set_unfound:
            fSetUnfound.write(element + "\n")

    os.remove(f"./{compound}/{sign} SetUnfound.txt")
