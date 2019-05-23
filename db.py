import peewee


DoesNotExist = peewee.DoesNotExist

db = peewee.SqliteDatabase("sqlite.db")


class Tweet(peewee.Model):
    id_ = peewee.CharField(null=False, index=True)
    user_id = peewee.CharField(null=False, index=True)
    screen_name = peewee.CharField(null=False, index=False)
    created_at = peewee.CharField(null=False, index=False)
    text_original = peewee.CharField(null=False, index=False)
    text_clean = peewee.CharField(null=False, index=False)
    link_type = peewee.CharField(null=False, index=False)
    lang = peewee.CharField(null=False, index=False)
    truncated = peewee.BooleanField(null=False)
    tweet_url = peewee.CharField(null=False, index=False)

    is_reply = peewee.BooleanField(null=False, index=False)
    is_retweeted = peewee.BooleanField(null=False, index=False)
    is_quoted = peewee.BooleanField(null=False, index=False)
    retweet_reply_quoted = peewee.CharField(null=True, index=False)

    still_available = peewee.BooleanField(null=True, index=False)
    group = peewee.CharField(null=True, index=False)
    relevancy_score = peewee.CharField(null=True, index=False)
    study_id = peewee.CharField(null=True, index=False)

    class Meta:
        database = db


class TweetOriginal(peewee.Model):
    id_ = peewee.CharField(null=False, index=True)
    user_id = peewee.CharField(null=False, index=False)
    screen_name = peewee.CharField(null=False, index=False)
    created_at = peewee.CharField(null=False, index=False)
    text_original = peewee.CharField(null=False, index=False)
    text_clean = peewee.CharField(null=False, index=False)
    link_type = peewee.CharField(null=False, index=False)
    lang = peewee.CharField(null=False, index=False)
    truncated = peewee.BooleanField(null=False)
    tweet_url = peewee.CharField(null=False, index=False)

    is_reply = peewee.BooleanField(null=False, index=False)
    is_retweeted = peewee.BooleanField(null=False, index=False)
    is_quoted = peewee.BooleanField(null=False, index=False)
    retweet_reply_quoted = peewee.CharField(null=True, index=False)

    class Meta:
        database = db


db.connect()
db.create_tables([Tweet, TweetOriginal])


