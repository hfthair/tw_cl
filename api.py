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

        user = tweet['user']['id_str']
        user_name = tweet['user']['screen_name']
        self.cache[id_] = (user, user_name)

        if len(self.cache) >= 100:
            self.do()

    def do(self):
        if not self.cache:
            return
        while True:
            res = requests.get('https://api.twitter.com/1.1/statuses/lookup.json',
                               params={
                                   'id': ','.join(self.cache.keys()),
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

if __name__ == '__main__':
    src = [828438540891602945, 828408931777130496, 828393981130186752, 828379052163620864, 828364443939639306, 828333887432642560, 828061484202807298, 828031757001818114, 828016902291222534, 828002349834702851, 827654335530225664, 827624154669187072, 827609133759201280, 827579253961146369, 827366232747827201, 827354717286187010, 827336804428808193, 827307081422274560, 826899644148019200, 826854382700523520, 826641568547352577, 826596996555345920, 826159661070090242, 825901888998690821, 825872210657165314, 825812050584694784, 825554359261990913, 825509715887132672, 825465580857724929, 825435064821547014, 825162291335352322, 825117653215875072, 825103138478817281, 825072998059237383, 823335864092790785, 823320533513175040, 823305821689942016, 823291114866245632, 823276002650554369, 823260639137304576, 823245273162022914, 823230484616450048, 819349231894929408, 819319548218372098, 819289957441343488, 818261972835848194, 818247040329273345, 818232265801076738, 818217438949023748, 818202474578399233, 818187027149651968, 818171588696743936, 818157128963780608, 810696408424710144, 810666626525855745, 810654745631354880, 809957092115316736, 809927697564626944, 808795966191104000, 808765632141475840, 808735568293138433, 808478147993800705, 808448257949106180, 808418628022534150, 808085731365310464, 808072869150359552, 808056128047316992, 808040322584420352, 807738074151141376, 807723524773253122, 807693393941975041, 807680095699816449, 807013439486959617, 806998886942441472, 806969307968262144, 806651275370708993, 806333665018019840, 806318302037426176, 806303962517344256, 806288787731087360, 806275835359596544, 805578878345498624, 805563788908961792, 805549029341929472, 805534295251107840, 805519085127790592, 805503995133513728, 805488334902534146, 805473788162932736, 803449102931525633, 803434842595688449, 803419185040805888, 803405348329680896, 803390307752706048, 803375711671242763, 803361529768902656, 803346271297736709, 803330609187790848, 803315165273923584, 803301064124547073]

