#!/usr/bin/env python
from requests.exceptions import Timeout
import requests as req
import pandas as pd
import json
import time
import os
import logging


def foodrecordcheck(record, safe, index):
    try:
        for j in range(5):
            # Chemical is generally recognised as safe
            if record["Record"]["Section"][index]["Section"][j]["TOCHeading"] == \
                    "FDA Generally Recognized as Safe - GRAS Notices":
                print("Found! FDA GRAS!")
                safe.add(str(record["Record"]["RecordTitle"]) + ", FDA GRAS")
                return True
            # Chemical is added to food
            if record["Record"]["Section"][index]["Section"][j]["TOCHeading"] == "FDA Substances Added to Food":
                print("Found! FDA food usages!")
                safe.add(record["Record"]["RecordTitle"] + ", FDA food use")
                return True
            # chemical is added to food
            if record["Record"]["Section"][index]["Section"][j]["TOCHeading"] == "Food Additive Classes":
                print("Found! Food Additive!")
                safe.add(record["Record"]["RecordTitle"] + ", Food Additive")
                return True

    except IndexError:
        print("food record not found")
        return True


def toxicrecordcheck(record, toxic):
    print("toxic record check placeholder")
    toxic.add(record["Record"]["RecordTitle"] + " nan")
    # todo no scanning for toxic records
    return


def safetyhazardcheck(record, toxic, index):
    print("safety hazard check |", end=" ")
    try:
        for j in range(5):
            if record["Record"]["Section"][index]["Section"][0]["Section"][j]["TOCHeading"] \
                    == "Hazard Classes and Categories":
                # add hazard classes to file such as acute tox and irritability
                print("Found! Hazard classes added to file")
                toxic.add(record["Record"]["RecordTitle"] + "\t" +
                          str(record["Record"]["Section"][index]["Section"][0]["Section"]
                              [j]["Information"][0]["Value"]["StringWithMarkup"]))
                return True
    except IndexError:
        print("hazard class not found |", end="")
        return False


def request(cids, unknown, unchecked, timeout, toxic, safe):
    ids = cids["IdentifierList"]["CID"]
    for cid in ids:
        try:
            response = req.get(
                "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/".format(
                    cid=cid))  # request full record about chemical
            time.sleep(.2)  # wait to not overflow PubChem
            record = json.loads(response.text)
            checked = False  # whether record has been checked to not double count
            try:
                for i in range(100):
                    if checked:
                        continue
                    if record["Record"]["Section"][i]["TOCHeading"] == "Toxicity":
                        toxicrecordcheck(record, toxic)
                    elif record["Record"]["Section"][i]["TOCHeading"] == "Safety and Hazards":
                        checked = safetyhazardcheck(record, toxic, i)
            except Exception as e:
                logging.exception(e)
                pass
            for i in range(100):
                if checked:
                    return
                if record["Record"]["Section"][i]["TOCHeading"] == "Food Additives and Ingredients":
                    checked = foodrecordcheck(record, safe, i)

        except Timeout:
            print()
            print("------TIMEOUT-------")
            print(cids)
            print("------------------")
            timeout.add(cid)
            return
        except IndexError:  # record not classifiable
            print("not checked")
            unchecked.add(record["Record"]["RecordTitle"])
            return
        except Exception as e:
            logging.exception(e)
            unknown.add(cid)
            return


def processchems(compounds, unknown, unchecked, timeout, unfound, toxic, safe):
    for value in compounds:
        try:
            print("[" + str(value) + "]", end=" ")
            response = req.get(
                "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound}/cids/JSON".format(compound=value))
            time.sleep(.2)
            cids = json.loads(response.text)
            if response.status_code == 404:  # chemical not found in PubChem
                unfound.add(value)
                print("404 not found")
            else:
                request(cids, unknown, unchecked, timeout, toxic, safe)

        except Timeout:
            print()
            print("------TIMEOUT-------")
            print(value)
            print("------------------")
            timeout.add(value[1])
            return
        except Exception as e:
            logging.exception(e)
            unknown.add(value[1])
            return


def main(compound, sign):
    tox_names = set()
    toxic = set()
    safe = set()
    unknown = set()
    unchecked = set()
    timeout = set()
    unfound = set()
    esi = pd.read_csv(f'./{sign} {compound}.csv', encoding='unicode_escape')
    tox = pd.read_csv('./OpenFoodTox.csv', encoding='unicode_escape')\
        .dropna(axis=0, subset=['MOLECULARFORMULA', 'COM_NAME']).drop_duplicates()
    tox_names.update(tox.COM_NAME[tox.MOLECULARFORMULA.isin(esi.formula)])
    try:
        processchems(tox_names, unknown, unchecked, timeout, unfound, toxic, safe)
    finally:
        if not os.path.exists(f"./{compound}/"):    # create new directory for chem and move into it
            os.makedirs(f"./{compound}/")
        os.chdir(f"./{compound}/")
        # write main out with unknown, timeout, and safe categories
        with open(f"{sign} MainOut.txt", 'w+') as fOut:
            fOut.write("===================== Unknown =====================\n")
            for element in unknown:
                fOut.write(str(element))
                fOut.write("\n")
            fOut.write("===================== Timeout =====================\n")
            for element in timeout:
                fOut.write(str(element))
                fOut.write("\n")
            fOut.write("====================== Safe =======================\n")
            for element in safe:
                fOut.write(str(element))
                fOut.write("\n")
        # write set unchecked with unchecked records
        with open(f"{sign} SetUnchecked.txt", 'w+') as fUnchecked:
            for element in unchecked:
                fUnchecked.write(str(element))
                fUnchecked.write("\n")
        # write set unchecked with unfound records
        with open(f"{sign} SetUnfound.txt", 'w+') as fUnfound:
            for element in unfound:
                fUnfound.write(str(element))
                fUnfound.write("\n")
        # write set unchecked with toxic records
        with open(f"{sign} SetToxic.txt", 'w+') as fToxic:
            for element in toxic:
                fToxic.write(str(element).replace("\'", "\""))
                fToxic.write("\n")

    print(timeout)
    print("\n")
    print(unknown)
    print("\n")
    os.chdir("../src")


# debugging purposes
if __name__ == "__main__":
    main("YP", "-")
