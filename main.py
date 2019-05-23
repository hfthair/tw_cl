import pandas as pd
import db
import api
import core


def lookup(ids_, origin):
    print('lookup', len(ids_))
    data = api.lookup(ids_.keys())
    print('get', len(data))
    for id_ in ids_:
        group, relevancy_score, study_id, text_= ids_[id_]
        original_find = origin.get(id_)
        tweet = data[id_]
        if not tweet:
            tmp = None
            if original_find:
                tmp = core.process_tweet(original_find)
            else:
                print('not found in original&twitter', id_)
                text_clean, url_types = core.text_only(text_)
                tmp = dict(id_=id_, user_id='', screen_name='', created_at='',
                           text_original=text_, text_clean=text_clean, link_type=url_types,
                           lang='', truncated=0, tweet_url='a/status/{}'.format(id_),
                           is_reply=False, is_retweeted=False, is_quoted=False,
                           retweet_reply_quoted='')
            try:
                o = db.Tweet(**tmp)
                o.still_available = False
                o.group = group
                o.relevancy_score = relevancy_score
                o.study_id = study_id
                o.save()
            except:
                print('db error', data['id_'])

        else:
            tweet_ex = core.process_tweet(tweet)
            try:
                o = db.Tweet(**tweet_ex)
                o.still_available = True
                o.group = group
                o.relevancy_score = relevancy_score
                o.study_id = study_id
                if original_find:
                    o.truncated = original_find.get('truncated', False)
                o.save()
            except:
                print('db error', data['id_'])


def main(src):
    keys = list(src.keys())
    print('total', len(keys))
    origin = search_by_id.main(keys)
    while keys:
        cur = keys[:100]

        lookup({k: src[k] for k in cur}, origin)

        del keys[:100]
        print('left', len(keys))


if __name__ == '__main__':
    import search_by_id

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
        # print(id_, group, score, study_id, link)


    import datetime
    now = datetime.datetime.now()
    main(src)
    delta = datetime.datetime.now() - now
    print(delta)
