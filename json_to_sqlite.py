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


def main():
    folders = ['data/']
    for folder in folders:
        cnt = 0
        for path in os.listdir(folder):
            path = folder + path
            if not os.path.isfile(path):
                continue
            print(cnt, path)

            try:
                obj = json.load(open(path, 'r', encoding='utf8'))
                print(path, len(obj))
                bulk = []
                for tweet in obj:
                    data = core.process_tweet(tweet)
                    bulk.append(data)

                try:
                    db.TweetOriginal.insert_many(bulk).execute()
                except:
                    print('db error', data['id_'])
            except JSONDecodeError:
                print('decode error: ', path)

            cnt = cnt + 1

if __name__ == '__main__':
    import datetime
    now = datetime.datetime.now()
    main()
    delta = datetime.datetime.now() - now
    print(delta)

