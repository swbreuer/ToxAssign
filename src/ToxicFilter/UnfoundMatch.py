import pandas as pd
import os


def match(compound, sign):
    print("---- UNFOUND MATCH ----")
    unfound = pd.read_csv(f"./{compound}/{sign} SetUnfound.txt", delimiter="\t", engine='python', names=["name"])
    found = pd.read_csv("Remove.csv")

    setSafe = pd.DataFrame(columns=["compound", "alias", "safety"])
    unfound.name = unfound.name.astype(str)
    found.compound = found.compound.astype(str)
    foundComp = unfound.merge(found, right_on="compound", left_on="name", how="inner")
    setSafe = foundComp
    setSafe = setSafe[(setSafe.Safety == "safe") | (setSafe.Safety == "flavoring agent")
                      | (setSafe.Safety == "fragrance") | (setSafe.Safety == "supplement")]
    foundComp = foundComp[~foundComp.compound.isin(setSafe.compound)]
    setUnfound = set()
    setUnfound.update(unfound[~unfound.name.isin(found.compound)])

    with open(f"./{compound}/{sign} SetFound.txt", "w+") as fSetFound:
        for index, value in foundComp.iterrows():
            fSetFound.write(str(value["compound"]) + ",\t" + str(value["alias"]) + ",\t" + str(value["Safety"]) + "\n")
        fSetFound.write("\n========= SAFE =========\n\n")
        for index, value in setSafe.iterrows():
            fSetFound.write(str(value["compound"]) + ",\t" + str(value["alias"]) + ",\t" + "\n")

    with open(f"./{compound}/{sign} SetUnfoundCopy.txt", "w+") as fSetUnfound:
        for element in setUnfound:
            fSetUnfound.write(element+"\n")

    os.remove(f"./{compound}/{sign} SetUnfound.txt")

