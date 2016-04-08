import facebook
import requests
import csv
import operator
from datetime import date, timedelta

APP_ID = '918318618262430'
APP_SECRET = '53bfcc093081bf5ed480f49550238031'

AUTHURL = ('https://graph.facebook.com/oauth/access_token?' +
           'client_id=' + APP_ID +
           '&client_secret=' + APP_SECRET +
           '&grant_type=client_credentials'
          )

r = requests.get(AUTHURL)
ACCESS_TOKEN = r.text.split('=')[1]

print(ACCESS_TOKEN)

graph = facebook.GraphAPI(access_token=ACCESS_TOKEN, version='2.2')

MACHRONICLE_PAGEID = 'machronicle/posts'

START_DATE = date.today()

class User:
    """Holds like, comment and post stats for a student."""

    def __init__(self, userid):
        self.userid = userid
        # get name
        self.name = graph.get_object(id=userid)['name']
        # No data yet
        self.likes = 0
        self.comments = 0
        self.shares = 0

    def get_total_score(self):
        # TODO: Add point factors for each count
        return self.likes + self.comments + self.shares

    def __eq__(self, other):
        return self.get_total_score() == other.get_total_score()

    def __lt__(self, other):
        return self.get_total_score() < other.get_total_score()

    def __str__(self):
        return (self.userid + ': ' +
                self.likes + ' likes,' +
                self.comments + 'comments and' +
                self.shares + 'shares'
                )



post = graph.get_object(id=MACHRONICLE_PAGEID)

posts = post['data']

# maps userid to user object
users = {}

for post in posts:
    postid = post['id'] + '/likes'
    likers = graph.get_object(id=postid)['data']
    for user in likers:
        # pull out plain text id
        userid = user['id']
        if userid in users:
            # increment one like
            users[userid].likes += 1
        else:
            # instantiate Object
            userobj = User(userid)
            # Add the like
            userobj.likes += 1
            # Save to dict
            users[userid] = userobj

sorted_users = sorted(users.items(), key=operator.itemgetter(1), reverse=True)

with open('data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',',
                        quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['userid', 'name', 'likes', 'comments', 'shares'])
    for (userid, user) in sorted_users:
        writer.writerow([userid, user.name, user.likes, user.comments, user.shares])

