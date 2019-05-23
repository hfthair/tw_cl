import time
import json
import requests
import requests_oauthlib
import config

auth = requests_oauthlib.OAuth1(config.consumer_key, config.consumer_secret,
                                config.access_tk, config.access_tk_secret)


class StatusLookup(object):
    def __init__(self, callback_, callback_unavailable):
        self.cache = {}
        self.callback = callback_
        self.callback_unavailable = callback_unavailable

    def pending(self, tweet):
        if 'retweeted_status' in tweet:
            return
        lang = tweet['lang']
        if lang != 'en':
            # print('not en, it is', lang)
            return
        id_ = tweet['id_str']
        if id_ in self.cache:
            return
        if ',' in id_:
            return

        user = tweet['user']['id_str']
        user_name = tweet['user']['screen_name']
        self.cache[id_] = (user, user_name)

        if len(self.cache.keys()) >= 100:
            self.do()

    def do(self):
        if not self.cache:
            return
        while True:
            res = requests.get('https://api.twitter.com/1.1/statuses/lookup.json',
                               params={
                                   'id': ','.join(self.cache.keys()[:100]),
                                   'include_entities': True,
                                   'trim_user': False,
                                   'map': True,
                                   'tweet_mode': 'extended'
                               }, auth=auth)
            if res.status_code == 200:
                data = json.loads(res.text)['id']
                for i in self.cache:
                    tweet = data[i]
                    if tweet:
                        self.callback(tweet)
                    else:
                        if self.callback_unavailable:
                            self.callback_unavailable(i, self.cache[i][0], self.cache[i][1])
                self.cache.clear()
                break
            else:
                print(res, res.text)
                if 'errors' in res.text:
                    if 'Rate limit exceeded' in res.text:
                        print('wait 33.3s...')
                        time.sleep(30)
                time.sleep(3.3)
                print('retry...')


def lookup(ids_):
    while True:
        res = requests.get('https://api.twitter.com/1.1/statuses/lookup.json',
                           params={
                               'id': ','.join(ids_),
                               'include_entities': True,
                               'trim_user': False,
                               'map': True,
                               'tweet_mode': 'extended'
                           }, auth=auth)
        if res.status_code == 200:
            data = json.loads(res.text)['id']
            return data
        else:
            print(res, res.text)
            if 'errors' in res.text:
                if 'Rate limit exceeded' in res.text:
                    print('wait 33.3s...')
                    time.sleep(30)
                print(ids_)
            time.sleep(3.3)
            print('retry...')


