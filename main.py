import json
import os
import re
import html
import db
import api


pattern = re.compile(r'https?://\S+', flags=re.IGNORECASE)

LINK = '[LINK]'

def process_tweet(tweet):
    id_str = tweet['id_str']
    user = tweet['user']['id_str']
    user_name = tweet['user']['screen_name']
    status_url = '{}/status/{}'.format(user_name, id_str)
    created_at = tweet['created_at']
    text = tweet.get('text', '')
    if 'full_text' in tweet:
        text = tweet['full_text']
    truncated = tweet['truncated']
    lang = tweet['lang']

    type_ = 'tweet'
    # is_quote_status = tweet['is_quote_status']
    if 'retweeted_status' in tweet:
        type_ = 'retweet'
        return
    elif 'quote_status' in tweet:
        type_ = 'quote'
        # quoted_status_id_str = tweet['quoted_status_id_str']
        # quoted_status = tweet['quoted_status']
    elif 'in_reply_to_status_id_str' in tweet and tweet['in_reply_to_status_id_str']:
        type_ = 'reply'
        # in_reply_to_status_id_str = tweet['in_reply_to_status_id_str']
        # in_reply_to_user_id_str = tweet['in_reply_to_user_id_str']
        # in_reply_to_screen_name = tweet['in_reply_to_screen_name']

    # if truncated:
    #     lookup.pending(id_str, (user, user_name), process_tweet)
    #     return

    links = []

    if 'entities' in tweet:
        entities = tweet['entities']

        if 'media' in entities:
            for i in entities['media']:
                url = i['url']
                if url in text:
                    text = text.replace(url, LINK)
                    media_type = i['type']
                    links.append(media_type)

        if 'urls' in entities:
            for i in entities['urls']:
                url = i['url']
                if url in text:
                    text = text.replace(url, LINK)
                    links.append('url')

    if 'extended_entities' in tweet:
        entities = tweet['extended_entities']

        if 'media' in entities:
            for i in entities['media']:
                url = i['url']
                if url in text:
                    text = text.replace(url, LINK)
                    media_type = i['type']
                    links.append(media_type)

        if 'urls' in entities:
            for i in entities['urls']:
                url = i['url']
                if url in text:
                    text = text.replace(url, LINK)
                    links.append('url')

    if 'http' in text.lower():
        text = pattern.sub(LINK, text)
        links.append('url_ex')


    text_unescaped = html.unescape(text)

    try:
        o = db.Tweet(id_=id_str, user=user, created_at=created_at,
                     text=text_unescaped, truncated=truncated, lang=lang,
                     type_=type_, links='|'.join(links), debug_url=status_url)
        o.save()
    except:
        print('db error: ', id_str)


def process_unavailable(id_, user, screen_name):
    try:
        db.Unavailable(id_=id_, user=user, screen_name=screen_name).save()
    except:
        pass


def main():
    lookup = api.StatusLookup(process_tweet, process_unavailable)

    def process_file(path):
        try:
            obj = json.load(open(path, 'r', encoding='utf8'))
            print(path, len(obj))
            for tweet in obj:
                lookup.pending(tweet)
        except: # json.decoder.JSONDecodeError:
            print('decode error: ', path)

    folder = 'data/'
    cnt = 0
    for path in os.listdir(folder):
        path = folder + path
        if os.path.isfile(path):
            print(cnt, path)
            process_file(path)
            cnt = cnt + 1

    lookup.do()

if __name__ == '__main__':
    import datetime
    now = datetime.datetime.now()
    main()
    delta = datetime.datetime.now() - now
    print(delta)
