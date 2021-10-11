import requests
import time
import random
import datetime
import json
try:
    import lzma as xz
except ImportError:
    import pylzma as xz
subreddits = ['legaladvice', 'legaladviceofftopic']
maxThings = -1
printWait = 2
requestSize = 100
from profanity_check import predict, predict_prob


def requestJSON(url):
    while True:
        try:
            r = requests.get(url)
            if r.status_code != 200:
                print('error code', r.status_code)
                time.sleep(5)
                continue
            else:
                break
        except Exception as e:
            print(e)
            time.sleep(5)
            continue
    return r.json()
overwrite = False
open_type = 'w' if overwrite else 'a'
train_f = xz.open("./cache/train.r_legaladvice.xz", open_type)
val_f = xz.open("./cache/validation.r_legaladvice.xz", open_type)

for subreddit in subreddits:

    meta = requestJSON('https://api.pushshift.io/meta')
    limitPerMinute = meta['server_ratelimit_per_minute']
    requestWait = 60 / limitPerMinute

    print('server_ratelimit_per_minute', limitPerMinute)



    things = ('submission',)
    def get_comments_for_post(post_id):
        url = 'https://api.pushshift.io/reddit/comment/search?link_id='\
            + post_id \
            + f'&metadata=true&limit=20000&subreddit={subreddit}'
        jsond = requestJSON(url)
        time.sleep(requestWait)
        return jsond['data']

    for thing in things:
        i = 0

        print('\n[starting', thing + 's]')

        if maxThings < 0:

            url = 'https://api.pushshift.io/reddit/search/'\
                    + thing + '/?subreddit='\
                    + subreddit\
                    + '&metadata=true&size=0'
            
            jsond = requestJSON(url)

            totalResults = jsond['metadata']['total_results']
            print('total ' + thing + 's', 'in', subreddit,':', totalResults)
        else:
            totalResults = maxThings
            print('downloading most recent', maxThings)


        created_utc = '1612822911' if subreddit == 'legaladvice' else ''

        startTime = time.time()
        timePrint = startTime
        while True:
            url = 'http://api.pushshift.io/reddit/search/'\
                    + thing + '/?subreddit=' + subreddit\
                    + '&size=' + str(requestSize)\
                    + '&before=' + str(created_utc)

            jsond = requestJSON(url)

            if len(jsond['data']) == 0:
                break

            doneHere = False
            for post in jsond['data']:
                created_utc = post["created_utc"]
                # f.write(str(post) + '\n')
                i += 1
                comments = get_comments_for_post(post['id'])
                
                filtered_comments = [comment for comment in comments if comment['score'] >= 8 \
                                            and predict_prob([comment['body']])[0] < .8 \
                                            and '[removed]' \
                                            not in comment['body'] \
                                            and '[deleted]' \
                                            not in comment['body'] \
                                            and post['id'] in comment['parent_id']
                                            ]

                if len(filtered_comments) == 0:
                    continue

                if 'selftext' in post:
                    selector = 'selftext'
                elif 'text' in post:
                    selector = 'text'
                elif 'body' in post:
                    selector = 'body'
                else:
                    print("Couldn't find a selector for post text, continuing")
                    print(post)
                    continue
                post_text = post[selector]
                text = f"Title: {post['title']}\nQuestion:{post_text}\n"
                if 'link_flair_text' in post and post['link_flair_text']:
                    text += f"Topic:\n{post['link_flair_text']}\n"
                elif 'link_flair_richtext' in post and post['link_flair_richtext']:
                    text += f"Topic:\n{post['link_flair_text']}\n"
                
                for q, comment in enumerate(sorted(filtered_comments, key=lambda x: x['score'], reverse=True)):
                    text += f'Answer #{q+1}: {comment["body"]}'
                
                datapoint = {
                    "url" : post['url'],
                    "text" : text,
                    "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
                    "created_timestamp" : datetime.datetime.fromtimestamp(created_utc).strftime("%m-%d-%Y")
                }
                if random.random() > .75:
                    val_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))
                else:
                    train_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))

                if i >= totalResults:
                    doneHere = True
                    break

            if doneHere:
                break
            
            if time.time() - timePrint > printWait:
                timePrint = time.time()
                percent = i / totalResults * 100
                
                timePassed = time.time() - startTime
                
                print('{:.2f}'.format(percent) + '%', '|',
                        time.strftime("%H:%M:%S", time.gmtime(timePassed)))


            time.sleep(requestWait)

train_f.close()
val_f.close()
