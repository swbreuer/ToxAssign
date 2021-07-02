import pandas as pd
import os


def unfoundMerge():
    mergeMain("UnfoundCopy", "Unfound")

def uncheckedMerge():
    print("---- UNCHECKED MERGE ----")
    mergeMain("Unchecked", "Unchecked")

def toxicMerge():
    print("---- TOXIC MERGE ----")
    checked = pd.DataFrame(columns=['name', 'toxicity'])

    for root, subDirs, files in os.walk("."):
        for subdir in subDirs:

            if len(subdir) > 3:
                continue

            try:
                os.chdir(f"./{subdir}")
                unfound = pd.read_csv(f"./+ SetToxic.txt", delimiter="\t",
                                    engine='python', names=["name", "toxicity"])
                checked = unfound.merge(checked, how="outer", on="name")
                unfound = pd.read_csv(f"./+ SetToxic.txt", delimiter="\t",
                                    engine='python', names=["name", "toxicity"])
                checked = unfound.merge(checked, how="outer", on="name")
                #os.remove(f"./+ SetToxic.txt")
                #os.remove(f"./- SetToxic.txt")
                os.chdir("..")
            except FileNotFoundError:
                os.chdir("..")


    print(os.getcwd())
    with open(f"./totalTox.txt", "w+") as fTotalTox:
        for index, value in checked.iterrows():
            fTotalTox.write(str(value["name"])+"\t"+str(value["toxicity"])+"\n")

def mergeMain(infile, outfile):
    checked = pd.DataFrame(columns=['Compound'])

    for root, subDirs, files in os.walk("."):
        for subdir in subDirs:

            try:
                os.chdir(f"./{subdir}")
                unfound = pd.read_csv(f"./+ Set{infile}.txt", delimiter="\t", engine='python', names=["Compound"])
                checked = unfound.merge(checked, how="outer")
                unfound = pd.read_csv(f"./- Set{infile}.txt", delimiter="\t", engine='python', names=["Compound"])
                checked = unfound.merge(checked, how="outer")
                os.chdir("..")
            except FileNotFoundError:
                os.chdir("..")

    print(os.getcwd())
    with open(f"./total{outfile}.txt", "w+") as fTotalUnfound:
        for index, value in checked.iterrows():
            fTotalUnfound.write(str(value["Compound"]) + "\n")