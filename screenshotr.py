import facebook
import requests
import csv
import operator
from datetime import datetime, timedelta

APP_ID = '918318618262430'
APP_SECRET = '53bfcc093081bf5ed480f49550238031'

MACHRONICLE_PAGEID = 'machronicle/posts'

def get_api_connection(appid, app_secret):
    """Return a facebook-sdk object authenticated
    with the given app id and secret"""

    # Place the appid and app_secret in the authentication url
    authurl = ('https://graph.facebook.com/oauth/access_token?' +
               'client_id=' + appid +
               '&client_secret=' + app_secret +
               '&grant_type=client_credentials'
              )
    # Ask Facebook for an authentication token
    response = requests.get(authurl)

    # Clean up Facebook's repsonse (Token comes after an equals sign)
    auth_token = response.text.split('=')[1]

    # Create the graph object
    graph = facebook.GraphAPI(access_token=auth_token, version='2.2')

    return graph

graph = get_api_connection(APP_ID, APP_SECRET)

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

def get_time_period(year=datetime.today().year, month=datetime.today().month):
    """Returns a tuple containing the first of the month and the first of the next month,
    capturing the entire month. Times are datetime objects"""

    start = datetime(year, month, 1)

    # Wrap month around to January from December
    end = datetime(year, month + 1, 1) if month < 12 else datetime(year, 1, 1)

    print(str(start) + "  " + str(end))

    return (start, end)


def tally_points(pageid, time_period):
    """Returns a map of userid to User objects with the likes tallied
    Accepts:
       pageid of the Facebook page
       time_period: a tuple of datetime objects to look for likes between
    """
    posts = graph.get_object(
        id=pageid,
        since=round(time_period[0].timestamp()),
        until=round(time_period[1].timestamp())
    )['data']

    # maps userid to user object
    users = {}

    def check_likes(post, user_dict):
        """Returns a dict with like data added to the existing dict"""
        likers = graph.get_connections(post['id'], 'likes',)['data']

        # Tally likes from each post
        for user in likers:
            # pull out plain text id
            userid = user['id']
            if userid in users:
                # increment one like
                user_dict[userid].likes += 1
            else:
                # instantiate Object
                userobj = User(userid)
                # Add the like
                userobj.likes += 1
                # Save to dict
                user_dict[userid] = userobj
        return user_dict


    for post in posts:
        print(post['created_time'])
        users = check_likes(post, users)
    return users


users = tally_points(MACHRONICLE_PAGEID, get_time_period(month=3))

sorted_users = sorted(users.items(), key=operator.itemgetter(1), reverse=True)

sorted_users = [ tup[1] for tup in sorted_users ]

def write_users_to_file(userlist, filename='data.csv'):
    """Takes the data from a list of users and dumps it to a rank-ordered csv file"""
    
    with open(filename, 'w', newline='') as csvfile:
        # Instanciate writer and set CSV settings
        writer = csv.writer(
                csvfile,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL
        )
        
        # Write a header row with titles for data
        writer.writerow(['userid', 'name', 'likes', 'comments', 'shares', 'total score'])

        # Loop though list of users and write a row of CSV for each
        for user in userlist:
            writer.writerow([
                user.userid,
                user.name,
                user.likes,
                user.comments,
                user.shares,
                user.get_total_score()
            ])
write_users_to_file(sorted_users)
