"""Facebook helper functions and data parsing functions"""

import facebook
import requests

from user_utils import User
from misc_utils import get_time_period

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


def check_post(post, stat, user_dict, fb_api):
    """Stat should be likes, comments, or sharedposts"""

    # Pull down the likes, comments or sharedposts
    items_found = fb_api.get_connections(post['id'], stat)['data']

    # likes results in an array of users, but comments and sharedposts
    # do not, so this ensures that we process user objects only
    if stat is 'likes':
        # Already a user list so OK to proceed
        users_found = items_found
    elif stat is 'comments':
        # List of comment objects so return the 'from' attribute
        users_found = [obj['from'] for obj in items_found]
    else:
        # List of posts, must check that post is from a user, not a page
        def process_post(obj):
            """Pulls profile out of post object if a user"""
            # Post initially does not include 'from', so fetch one that does
            obj_with_from = fb_api.get_object(
                obj['id'],
                metadata=1,
                fields='id,from'
            )
            # Now fetch the profile of the user with the type object inlcuded
            profile = fb_api.get_object(
                obj_with_from['from']['id'],
                metadata=1,
                fields='id,name,metadata{type}'
            )
            # Check type and only add if type is a user
            if profile['metadata']['type'] == 'user':
                return obj['from']
            else:
                # Profile is not a user, add a None
                return None

        # Apply the post processing function
        users_found = [process_post(obj) for obj in items_found]

        # Remove None items from list
        users_found = [obj for obj in users_found if obj is not None]

    # Tally points from each post
    for user in users_found:
        # Get plain text id
        userid = user['id']
        if userid in user_dict:
            # Incerement points in object
            # Uses geattr and setattr instead of obj.attr for generality
            prev_value = getattr(user_dict[userid], stat)
            setattr(user_dict[userid], stat, prev_value + 1)
        else:
            # Instanciate object
            userobj = User(user)
            # Add the like
            setattr(userobj, stat, 1)
            # Save to dict
            user_dict[userid] = userobj

    return user_dict


def tally_points(posts, fb_api):
    """Returns a map of userid to User objects with the likes tallied
    Accepts a list of posts (the 'data' attribute of a page object)
    """

    # maps userid to user object
    users = {}

    for post in posts:
        # Print out the time of each post
        print(post['created_time'] + " - " + post['id'])

        # Call check_post for each attribute (likes, comments, sharedposts)
        users = check_post(post, 'likes', users, fb_api)
        users = check_post(post, 'comments', users, fb_api)
        # Can only see public shared posts
        users = check_post(post, 'sharedposts', users, fb_api)

    return users

def get_users_with_data(pageid, month, fb_api):
    """Returns a sorted list of the users populated with point data"""
    # Get a tuple of datetime objects, one at the start of the month, one at the end
    time_period = get_time_period(month=month)

    # Get a list of the posts on the page within the two dates in time_period
    posts = fb_api.get_connections(
        pageid,
        'posts',
        # Round times to shorten request URL
        since=round(time_period[0].timestamp()),
        until=round(time_period[1].timestamp())
    )['data']

    # Count all the points up
    users = tally_points(posts, fb_api)

    # Sort the result
    sorted_users = sorted(users.values(), reverse=True)

    return sorted_users

