import pandas as pd
import db
df = pd.read_csv('C:/Users/zhang/Downloads/tweet_img_new_lib.csv', header=None)
libs = [i[-18:] for i in df[2]]

cnt = 0
for t in db.Tweet.select():
    if t.id_ in libs:
        t.group = 'lib'
        t.save()
        cnt += 1

print(cnt)


