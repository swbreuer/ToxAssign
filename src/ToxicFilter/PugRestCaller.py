from requests.exceptions import Timeout
import requests as req
import pandas as pd
import json
import time
import os

def foodRecordCheck(record, setSafe, index):
    try:
        for j in range(5):
            if(record["Record"]["Section"][index]["Section"][j]["TOCHeading"]=="FDA Generally Recognized as Safe - GRAS Notices"):
                print("Found! FDA GRAS!")
                setSafe.add(str(record["Record"]["RecordTitle"]) + ", FDA GRAS")
                return True
            if(record["Record"]["Section"][index]["Section"][j]["TOCHeading"]=="FDA Substances Added to Food"):
                print("Found! FDA food usages!")
                setSafe.add(record["Record"]["RecordTitle"] + ", FDA food use")
                return True
            if (record["Record"]["Section"][index]["Section"][j]["TOCHeading"] == "Food Additive Classes"):
                print("Found! Food Additive!")
                setSafe.add(record["Record"]["RecordTitle"] + ", Food Additive")
                return True

    except IndexError:
        print("food record not found")
        return True


def toxicRecordCheck(record, setToxic):
    print("toxic record check placeholder")
    setToxic.add(record["Record"]["RecordTitle"] + " nan")
    return


def safetyHazardCheck(record, setToxic, index):
    print("safety hazard check |", end=" ")
    try:
        for j in range(5):
            if record["Record"]["Section"][index]["Section"][0]["Section"][j]["TOCHeading"]\
                    =="Hazard Classes and Categories" :
                print("Found! Hazard classes added to file")
                setToxic.add(record["Record"]["RecordTitle"]+ "\t" +
                             str(record["Record"]["Section"][index]["Section"][0]["Section"][j]["Information"][0]
                                 ["Value"]["StringWithMarkup"]))
                return True

    except IndexError:
        print("hazard class not found |", end="")
        return False


def request(cids, setUnknown, setUnchecked, setTimeout, setToxic, setSafe):
    ids = cids["IdentifierList"]["CID"]
    for cid in ids:
        try:
            response = req.get(
                "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/".format(
                    cid=cid))
            time.sleep(.2)
            record = json.loads(response.text)
            checked = False
            try:
                for i in range(100):
                    if(checked):
                        continue
                    if record["Record"]["Section"][i]["TOCHeading"] == "Toxicity":
                        toxicRecordCheck(record, setToxic)
                    elif record["Record"]["Section"][i]["TOCHeading"] == "Safety and Hazards":
                        checked = safetyHazardCheck(record, setToxic, i)
            except Exception:
                pass
            for i in range(100):
                if checked:
                    return
                if record["Record"]["Section"][i]["TOCHeading"] == "Food Additives and Ingredients":
                    checked = foodRecordCheck(record, setSafe, i)

        except Timeout:
            print()
            print("------TIMEOUT-------")
            print(cids)
            print("------------------")
            setTimeout.add(cid)
            return
        except IndexError:
            print("not checked")
            setUnchecked.add(record["Record"]["RecordTitle"])
            return
        except Exception as e:
            print()
            print("------" + str(e) + "-------")
            print(cids)
            print("------------------")
            setUnknown.add(cid)
            return


def processChems(toxNames, setUnknown, setUnchecked, setTimeout, setUnfound, setToxic, setSafe):
    for value in toxNames:
        try:
            print("["+str(value)+"]", end=" ")
            response = req.get(
                "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound}/cids/JSON".format(compound=value))
            time.sleep(.2)
            cids = json.loads(response.text)
            if (response.status_code == 404):
                setUnfound.add(value)
                print("404 not found")
            else:
                request(cids, setUnknown, setUnchecked, setTimeout, setToxic, setSafe)

        except Timeout:
            print()
            print("------TIMEOUT-------")
            print(value)
            print("------------------")
            setTimeout.add(value[1])
            return
        except Exception as e:
            print()
            print("------" + str(e) + "-------")
            print(value)
            print("------------------")
            setUnknown.add(value[1])
            return


def main(compound, sign):
    esi = pd.read_csv(f'./{sign}ESI {compound}.csv', encoding='unicode_escape')
    tox = pd.read_csv('./OpenFoodTox.csv', encoding='unicode_escape').dropna(axis=0, subset=['MOLECULARFORMULA','COM_NAME']).drop_duplicates()
    #esiPos['Formula'] = esiPos['Formula'].str.replace(' ', '')
    #esiNeg['Formula'] = esiNeg['Formula'].str.replace(' ', '')
    posToxNames_Form = tox.COM_NAME[tox.MOLECULARFORMULA.isin(esi.formula)]
    toxNames = set()
    setToxic = set()
    setSafe = set()
    setUnknown = set()
    setUnchecked = set()
    setTimeout = set()
    setUnfound = set()
    toxNames.update(posToxNames_Form)
    try:
        processChems(toxNames, setUnknown, setUnchecked, setTimeout, setUnfound, setToxic, setSafe)
    finally:
        if not os.path.exists(f"./{compound}/"):
            os.makedirs(f"./{compound}/")
        os.chdir(f"./{compound}/")

        with open(f"{sign} MainOut.txt",'w+') as fOut:
            fOut.write("===================== Unknown =====================\n")
            for element in setUnknown:
                fOut.write(str(element))
                fOut.write("\n")
            fOut.write("===================== Timeout =====================\n")
            for element in setTimeout:
                fOut.write(str(element))
                fOut.write("\n")
            fOut.write("====================== Safe =======================\n")
            for element in setSafe:
                fOut.write(str(element))
                fOut.write("\n")
        with open(f"{sign} SetUnchecked.txt",'w+') as fUnchecked:
            for element in setUnchecked:
                fUnchecked.write(str(element))
                fUnchecked.write("\n")
        with open(f"{sign} SetUnfound.txt",'w+') as fUnfound:
            for element in setUnfound:
                fUnfound.write(str(element))
                fUnfound.write("\n")
        with open(f"{sign} SetToxic.txt", 'w+') as fToxic:
            for element in setToxic:
                fToxic.write(str(element).replace("\'", "\""))
                fToxic.write("\n")

    print(setTimeout)
    print("\n")
    print(setUnknown)
    print("\n")
    os.chdir("..")


if __name__=="__main__":
    main("YP","-")
