import os
import json
import db
import core


JSONDecodeError = ValueError
try:
    # python > 3.4
    JSONDecodeError = json.decoder.JSONDecodeError
except:
    pass


def main(ids_):
    folders = ['data/']
    res = {}
    for folder in folders:
        cnt = 0
        for path in os.listdir(folder):
            path = folder + path
            if not os.path.isfile(path):
                continue

            if cnt % 100 == 0:
                print(cnt, path)

            try:
                obj = json.load(open(path, 'r', encoding='utf8'))
                for tweet in obj:
                    id_str = tweet['id_str']
                    if id_str in ids_:
                        res[id_str] = tweet
                        ids_.remove(id_str)
            except JSONDecodeError:
                pass

            cnt = cnt + 1
            if not ids_:
                break

        if not ids_:
            break

    print('not found: ', len(ids_))

    return res

if __name__ == '__main__':
    import pandas as pd
    df = pd.read_excel('lib and con combined_gun.xlsx', header=0, skiprows=1)
    subset = df[['Link', 'Group', 'Relevancy score', 'Study_ID', 'Tweet']]

    src = {}
    for idx, row in subset.iterrows():
        link = row['Link']
        group = row['Group']
        score = row['Relevancy score']
        study_id = row['Study_ID']
        text = row['Tweet']

        id_ = link[link.rfind('/')+1:]
        id_ = id_.strip()

        src[id_] = (group, score, study_id, text)

    ids_ = list(src.keys())

    import datetime
    now = datetime.datetime.now()
    res = main(ids_)
    print(res)
    delta = datetime.datetime.now() - now
    print(delta)

