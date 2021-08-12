#!/usr/bin/env python
import pandas as pd
import json
import logging


def toxfilter(compound, filename):
    print("---- TOXIC FILTER ----")

    toxic = pd.read_csv(f"./{compound}/{filename}.txt", delimiter="\t",
                        engine='python', names=["name", "toxicity"])

    set1 = set()
    set2 = set()
    set3 = set()
    set4 = set()
    dict_else = dict()

    for index, value in toxic.iterrows():
        toxfound = 5  # only mark highest toxicity
        try:
            data = json.loads(value["toxicity"])
            for i in range(20):
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
        except Exception as e:
            logging.exception(e)
            if toxfound > 4:
                dict_else[value["name"]] = value["toxicity"]  # if not an acute toxic compound dump it in "other"
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
    for key in dict_else:
        f.write(key)
        f.write("\t")
        try:
            f.write(dict_else[key])
        except Exception as e:
            logging.exception(e)
            pass
        f.write("\n")

    f.close()
