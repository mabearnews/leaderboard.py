import facebook
import requests

from user_utils import User

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

def tally_points(posts, fb_api):
    """Returns a map of userid to User objects with the likes tallied
    Accepts a list of posts (the 'data' attribute of a page object)
    """

    # maps userid to user object
    users = {}

    def check_likes(post, user_dict):
        """Returns a dict with like data added to the existing dict"""
        likers = fb_api.get_connections(post['id'], 'likes',)['data']

        # Tally likes from each post
        for user in likers:
            # pull out plain text id
            userid = user['id']
            if userid in users:
                # increment one like
                user_dict[userid].likes += 1
            else:
                # instantiate Object
                userobj = User(user)
                # Add the like
                userobj.likes += 1
                # Save to dict
                user_dict[userid] = userobj
        return user_dict


    for post in posts:
        print(post['created_time'])
        users = check_likes(post, users)
    return users

