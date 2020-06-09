import praw
import os

key = 'urYURxN7NEao8TlE-gB_33f3ANE'
clientId = 'zcpKwNZG8DvpMg'
'''
clientId = os.environ['praw_client_id']
key = os.environ['praw_key']
'''
reddit = praw.Reddit(client_id=clientId,
                     client_secret=key, user_agent="trevor")


blanketUser = {
    'body': '',
    'score': 0,
    'username': '',
}


def instantiate(username):
    user = retrieveUser(username)
    try:
        karma = user.comment_karma
        comments = getNewComments(user)
        if not len(comments):
            raise Exception('no comments')
        return [karma, comments]
    except Exception as e:
        return 404


def retrieveUser(username):
    return reddit.redditor(name=username)


def getIcon(subredditName):
    return reddit.subreddit(subredditName).icon_img


def getNewComments(user):
    comments = []
    for comment in user.comments.new(limit=40):  # TODO change to 100
        parent = comment.parent()
        if comment.is_root:
            if parent.author:
                try:
                    par = {
                        'body': parent.selftext,
                        'score': parent.score,
                        'username': parent.author.name
                    }
                except Exception as e:
                    print(f"{e}: top level comment")
                    par = blanketUser
                    print(comment.id)

        else:
            try:
                par = {
                    'body': parent.body,
                    'score': parent.score,
                    'username': parent.author.name
                }

            except Exception as e:
                print(f"{e}: nested comment")
                par = blanketUser
                print(comment.id)

        commentObj = {
            'id': comment.id,
            'body': comment.body,
            'parent': par,
            'subreddit': comment.subreddit.display_name,
            'score': comment.score,
            'created_utc': comment.created_utc,
        }

        comments.append(commentObj)

    return comments
