#!/usr/bin/env python
import pandas as pd
import os
import PubChem


class Match:
    source = PubChem
    set_unfound = set()
    set_safe = set()
    found_comp = set()

    def __init__(self, pub=PubChem):
        self.source = pub

    def match(self):
        print("---- UNFOUND MATCH ----")
        self.unfound = pd.DataFrame(list(Match.source.PubChemClass.unfound), columns=["name"])
        found = pd.read_csv("Remove.csv")

        self.unfound.name = self.unfound.name.astype(str)
        found.compound = found.compound.astype(str)
        self.found_comp = self.unfound.merge(found, right_on="compound", left_on="name", how="inner")
        self.set_safe = self.found_comp
        self.set_safe = self.set_safe[(self.set_safe.Safety == "safe") | (self.set_safe.Safety == "flavoring agent")
                                        | (self.set_safe.Safety == "fragrance") | (
                                                    self.set_safe.Safety == "supplement")]
        self.found_comp = self.found_comp[~self.found_comp.compound.isin(self.set_safe.compound)]
        self.set_unfound.update(self.unfound[~self.unfound.name.isin(found.compound)])

        # with open(f"./{compound}/{sign} SetFound.txt", "w+") as fSetFound:
        #     for index, value in found_comp.iterrows():
        #         fSetFound.write(str(value["compound"]) + ",\t" + str(value["alias"]) + ",\t" + str(value["Safety"]) + "\n")
        #     fSetFound.write("\n========= SAFE =========\n\n")
        #     for index, value in set_safe.iterrows():
        #         fSetFound.write(str(value["compound"]) + ",\t" + str(value["alias"]) + ",\t" + "\n")
        #
        # with open(f"./{compound}/{sign} SetUnfoundCopy.txt", "w+") as fSetUnfound:
        #     for element in set_unfound:
        #         fSetUnfound.write(element + "\n")

        # os.remove(f"./{compound}/{sign} SetUnfound.txt")
