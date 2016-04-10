from datetime import datetime, timedelta
import operator

from user_utils import write_users_to_file
from facebook_utils import get_api_connection, tally_points

APP_ID = '918318618262430'
APP_SECRET = '53bfcc093081bf5ed480f49550238031'

MACHRONICLE_PAGEID = 'machronicle/posts'


graph = get_api_connection(APP_ID, APP_SECRET)


def get_time_period(year=datetime.today().year, month=datetime.today().month):
    """Returns a tuple containing the first of the month and the first of the next month,
    capturing the entire month. Times are datetime objects"""

    start = datetime(year, month, 1)

    # Wrap month around to January from December
    end = datetime(year, month + 1, 1) if month < 12 else datetime(year, 1, 1)

    print(str(start) + "  " + str(end))

    return (start, end)

time_period = get_time_period(month=3)

posts = graph.get_object(
    id=MACHRONICLE_PAGEID,
    since=round(time_period[0].timestamp()),
    until=round(time_period[1].timestamp())
)['data']

users = tally_points(posts, graph)

sorted_users = sorted(users.items(), key=operator.itemgetter(1), reverse=True)

sorted_users = [ tup[1] for tup in sorted_users ]

write_users_to_file(sorted_users) 
