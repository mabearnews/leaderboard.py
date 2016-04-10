import csv

class User:
    """Holds like, comment and post stats for a student."""

    def __init__(self, userobject):
        self.userid = userobject['id']
        self.name = userobject['name']

        # No data yet
        self.likes = 0
        self.comments = 0
        self.shares = 0

    def get_total_score(self):
        """Returns the total number of Facebook actions"""
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

