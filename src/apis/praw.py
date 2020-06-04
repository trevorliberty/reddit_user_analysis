import json
import requests
import praw
reddit = praw.Reddit(client_id="zcpKwNZG8DvpMg",
                     client_secret="urYURxN7NEao8TlE-gB_33f3ANE", user_agent="trevor")

seenEpochs = {1: 1}


def getComments(username, start_epoch):
    query = f'http://api.pushshift.io/reddit/search/comment/?after={start_epoch}&author={username}&size=1000&sort=asc'
    arr = requests.get(query).json()['data']
    if not len(arr):
        return 302
    val = arr[len(arr)-1]
    x = val['created_utc']
    if x in seenEpochs:
        return 302
    else:
        return [x, arr]


def instantiate(username, start_epoch, commentArr):
    retObj = getComments(username, start_epoch)
    if retObj == 302:
        return commentArr
    else:
        new_epoch = retObj[0]
        comments = retObj[1]
        commentArr += getNewComments(comments)
        return instantiate(username, new_epoch, commentArr)


def retrieveUser(username):
    return reddit.redditor(name=username)


def getParentComment(parent_id, is_comment):
    p_id = parent_id[parent_id.find("_")+1]
    if is_comment:
        comm = reddit.comment(id=p_id)
        body = comm.body

    else:
        comm = reddit.submission(id=p_id)
        body = comm.selftext

    username = comm.author.name
    score = comm.score
    return {
        'username': username,
        'score': score,
        'body': body
    }


def getNewComments(comment_list):
    comments = []
    for comment in comment_list:
        seenEpochs[comment['created_utc']] = 1
        try:
            if comment['link_id'] == comment['parent_id']:
                parent = getParentComment(comment['parent_id'], False)
            else:
                parent = getParentComment(comment['parent_id'], True)
        except:
            parent = {
                'body': '',
                'username': '',
                'score': ''
            }

        commentObj = {
            'id': comment['id'],
            'body': comment['body'],
            'parent': parent,
            'subreddit': comment['subreddit'],
            'score': comment['score']
        }
        comments.append(commentObj)

    return comments


def init(username):
    user = retrieveUser(username)
    karma = user.comment_karma
    query = f'http://api.pushshift.io/reddit/search/comment/?author={username}&size=1&sort=asc'
    initUTC = requests.get(query)\
        .json()['data'][0]['author_created_utc']

    commentArr = []
    instantiate(username, initUTC, commentArr)
    return [karma, commentArr]
