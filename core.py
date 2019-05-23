import json
import os
import re
import html
import db
import api

pattern = re.compile(r'https?://\S+', flags=re.IGNORECASE)


def process_tweet(tweet):
    id_str = tweet['id_str']
    user_id = tweet['user']['id_str']
    screen_name = tweet['user']['screen_name']
    created_at = tweet['created_at']
    text_original = tweet.get('text', '')
    if 'full_text' in tweet:
        text_original = tweet['full_text']
    text_clean = text_original
    truncated = tweet['truncated']
    lang = tweet['lang']

    is_reply = False
    is_retweeted = False
    is_quoted = False
    additional = ''

    if 'retweeted_status' in tweet:
        is_retweeted = True
        additional = tweet['retweeted_status']['id_str']
    elif 'quoted_status' in tweet:
        is_quoted = True
        additional = tweet['quoted_status']['id_str']
    elif 'in_reply_to_status_id_str' in tweet and tweet['in_reply_to_status_id_str']:
        is_reply = True
        additional = tweet['in_reply_to_status_id_str']

    medias = set()

    if 'entities' in tweet:
        entities = tweet['entities']

        if 'media' in entities:
            for i in entities['media']:
                url = i['url']
                if url in text_clean:
                    media_type = i['type'].upper()
                    text_clean = text_clean.replace(url, '[{}]'.format(media_type))
                    medias.add(media_type)

        if 'urls' in entities:
            for i in entities['urls']:
                url = i['url']
                if url in text_clean:
                    media_type = 'LINK'
                    text_clean = text_clean.replace(url, '[{}]'.format(media_type))
                    medias.add(media_type)

    if 'extended_entities' in tweet:
        entities = tweet['extended_entities']

        if 'media' in entities:
            for i in entities['media']:
                url = i['url']
                if url in text_clean:
                    media_type = i['type'].upper()
                    text_clean = text_clean.replace(url, '[{}]'.format(media_type))
                    medias.add(media_type)

        if 'urls' in entities:
            for i in entities['urls']:
                url = i['url']
                if url in text_clean:
                    media_type = 'LINK'
                    text_clean = text_clean.replace(url, '[{}]'.format(media_type))
                    medias.add(media_type)

    if 'http' in text_clean.lower():
        text_clean = pattern.sub('[LINK2]', text_clean)
        medias.add('LINK2')

    pattern_str = '|'.join('\['+i+'\]' for i in medias)
    url_types = re.findall(pattern_str, text_clean)
    url_types = '|'.join(i[1:-1] for i in url_types if i)

    text_clean = html.unescape(text_clean)

    return dict(id_=id_str, user_id=user_id, screen_name=screen_name, created_at=created_at,
                text_original=text_original, text_clean=text_clean, link_type=url_types,
                lang=lang, truncated=truncated, tweet_url='{}/status/{}'.format(screen_name, id_str),
                is_reply=is_reply, is_retweeted=is_retweeted, is_quoted=is_quoted,
                retweet_reply_quoted=additional)
