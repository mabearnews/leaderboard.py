"""Main module"""
import configparser
import argparse
from datetime import date
import os.path

from user_utils import write_users_to_file
from facebook_utils import get_api_connection, get_users_with_data

def run(pageid, month, year, app_id, app_secret):
    """Runs data analysis"""
    # Connect to Facebook
    graph = get_api_connection(app_id, app_secret)

    # Retrieve data
    user_data = get_users_with_data(pageid, month, year, graph)

    # Write data to file
    write_users_to_file(user_data)

def read_api_config():
    """Returns a tuple of (appid, appsecret)"""
    config = configparser.ConfigParser()
    config.read('config.ini')
    api = config['API CONNECTION']
    return (api['AppID'], api['AppSecret'])


def main():
    """Main thread when run from cmd"""
    api_config = (None, None)
    if os.path.isfile('config.ini'):
        api_config = read_api_config()

    parser = argparse.ArgumentParser(
        description='Create CSV of Facebook page like, comment and share data'
    )
    parser.add_argument(
        'pageid',
        help='the name of the Facebook page from the url: facebook.com/[pageid]/'
    )
    parser.add_argument(
        '--month',
        help='the month to search in in integer form',
        choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        default=date.today().month,
        type=int
    )
    parser.add_argument(
        '--year',
        help='the integer year to search if not the current year',
        default=date.today().year,
        type=int
    )
    parser.add_argument(
        '--appid',
        help='override appid from config file',
        default=api_config[0]
    )
    parser.add_argument(
        '--appsecret',
        help='override appsecret from config file',
        default=api_config[1]
    )
    args = parser.parse_args()

    run(args.pageid, args.month, args.year, args.appid, args.appsecret)


if __name__ == "__main__":
    main()

