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
    bulk = []
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
                # print(path, len(obj))
                for tweet in obj:
                    try:
                        data = core.process_tweet(tweet)
                        bulk.append(data)
                    except KeyError:
                        print('key error')
                    if len(bulk) >= 5000:
                        try:
                            with db.db_origin.atomic():
                                for idx in range(0, len(bulk), 50):
                                    rows = bulk[idx:idx + 50]
                                    db.TweetOriginal.insert_many(rows).on_conflict(action='IGNORE').execute()
                        except Exception as e:
                            print('db error', e)
                        finally:
                            bulk.clear()
            except JSONDecodeError:
                try:
                    db.DecodeError(path=path).save()
                except:
                    print('db error when handling decode error', e)

            cnt = cnt + 1

    if bulk:
        try:
            with db.db_origin.atomic():
                for idx in range(0, len(bulk), 50):
                    rows = bulk[idx:idx + 50]
                    db.TweetOriginal.insert_many(rows).on_conflict(action='IGNORE').execute()
        except Exception as e:
            print('db error', e)

if __name__ == '__main__':
    import datetime
    now = datetime.datetime.now()
    main()
    delta = datetime.datetime.now() - now
    print(delta)

