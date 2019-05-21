import peewee

db = peewee.SqliteDatabase("sqlite.db")


class Tweet(peewee.Model):
    id_ = peewee.CharField(null=False, index=True)
    user = peewee.CharField(null=False, index=True)
    created_at = peewee.CharField(null=False, index=False)
    text = peewee.CharField(null=False, index=False)
    type_ = peewee.CharField(null=False, index=False)
    links = peewee.CharField(null=False, index=False)
    lang = peewee.CharField(null=False, index=False)
    truncated = peewee.BooleanField(null=False)

    debug_url = peewee.CharField(null=False, index=False)

    class Meta:
        database = db

db.connect()
db.create_tables([Tweet])


