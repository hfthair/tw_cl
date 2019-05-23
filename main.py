import pandas as pd
import db
import api
import core


def lookup(ids_):
    print('lookup', len(ids_))
    data = api.lookup(ids_.keys())
    print('get', len(data))
    for id_ in ids_:
        group, relevancy_score, study_id = ids_[id_]
        original_find = db.TweetOriginal.select().where(db.TweetOriginal.id_ == id_)
        tweet = data[id_]
        if not tweet:
            if original_find:
                ori = original_find.dicts()[0]
                # todo: fix me
                print(ori)
                _ = input('oriori >')
                try:
                    o = db.Tweet(**ori, still_available=False, group=group,
                                 relevancy_score=relevancy_score, study_id=study_id)
                    o.save()
                except:
                    print('db error', data['id_'])
            else:
                print('not found in original&twitter', id_)
        else:
            tweet_ex = core.process_tweet(tweet)
            try:
                o = db.Tweet(**tweet_ex, still_available=True, group=group,
                             relevancy_score=relevancy_score, study_id=study_id)
                if original_find:
                    o.truncated = original_find[0].truncated
                o.save()
            except:
                print('db error', data['id_'])


def main(src):
    keys = list(src.keys())
    print('total', len(keys))
    while keys:
        cur = keys[:100]

        lookup({k: src[k] for k in cur})

        del keys[:100]


if __name__ == '__main__':
    df = pd.read_excel('lib and con combined_gun.xlsx', header=0, skiprows=1)
    subset = df[['Link', 'Group', 'Relevancy score', 'Study_ID']]

    src = {}
    for idx, row in subset.iterrows():
        link = row['Link']
        group = row['Group']
        score = row['Relevancy score']
        study_id = row['Study_ID']

        id_ = link[link.rfind('/')+1:]
        id_ = id_.strip()

        src[id_] = (group, score, study_id)
        # print(id_, group, score, study_id, link)

    import datetime
    now = datetime.datetime.now()
    main(src)
    delta = datetime.datetime.now() - now
    print(delta)
