import pandas as pd
import json
import os


def toxfilter(compound, filename):
    print("---- TOXIC FILTER ----")

    toxic = pd.read_csv(f"./{compound}/{filename}.txt", delimiter="\t",
                        engine='python', names=["name", "toxicity"])

    set1 = set()
    set2 = set()
    set3 = set()
    set4 = set()
    setElse = set()
    dictElse = dict()

    for index, value in toxic.iterrows():

        toxfound = 5
        try:
            data = json.loads(value["toxicity"])
            for i in range(5):

                if data[i]["String"][0:12] == "Acute Tox. 1":
                    set1.add(value["name"])
                    toxfound = 1

                elif data[i]["String"][0:12] == "Acute Tox. 2" and toxfound > 1:
                    set2.add(value["name"])
                    toxfound = 2

                elif data[i]["String"][0:12] == "Acute Tox. 3" and toxfound > 2:
                    set3.add(value["name"])
                    toxfound = 3

                elif data[i]["String"][0:12] == "Acute Tox. 4" and toxfound > 3:
                    set4.add(value["name"])
                    toxfound = 4

        except Exception as a:
            if toxfound > 4:
                dictElse[value["name"]] = value["toxicity"]

    f = open(f"./{compound}/{filename}Filtered.txt", "w+")

    f.write("    ---------Toxic 1---------\n")
    for element in set1:
        f.write(str(element))
        f.write("\n")

    f.write("    ---------Toxic 2---------\n")
    for element in set2:
        f.write(str(element))
        f.write("\n")

    f.write("    ---------Toxic 3---------\n")
    for element in set3:
        f.write(str(element))
        f.write("\n")

    f.write("    ---------Toxic 4---------\n")
    for element in set4:
        f.write(str(element))
        f.write("\n")

    f.write("    ---------Else---------\n")
    for key in dictElse:
        f.write(key)
        f.write("\t")
        try:
            f.write(dictElse[key])
        except:
            1
        f.write("\n")

    f.close()
