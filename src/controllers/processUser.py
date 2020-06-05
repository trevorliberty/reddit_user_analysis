from apis.praw import instantiate
from apis.textAnalysis import getLanguage, getSentiment, getComplexity
from collections import Counter
import random
"""
Contains functionality for querying and processing reddit user information.
"""


class Parent():
    def __init__(self, score=0, contents=None, sentiment=None):
        self.score = score
        self.contents = contents
        self.sentiment = sentiment

    def display(self):
        print('*****')
        print(f'Score: {str(self.score)}')
        print(f'Contents: {self.contents}')
        print(f'Sentiment: {str(self.sentiment)}')
        print('*****')


class Comment():
    def __init__(self, score=0, contents=None, subreddit=None, sentiment=None, parent=None):
        self.score = score
        self.contents = contents
        self.subreddit = subreddit
        self.sentiment = sentiment
        self.parent = parent

    def display(self):
        print('-----')
        print(f'Score: {str(self.score)}')
        print(f'Contents: {self.contents}')
        print(f'Sentiment: {str(self.sentiment)}')
        print(f'Subreddit: {self.subreddit}')
        print(f'ParentComment')
        self.parent.display()
        print('-----')


class User():
    def __init__(self):
        #Raw data (data to be read from praw and assigned sentiment values)
        self.name = "UNDEFINED"
        self.language = "UNDEFINED"
        self.karma = 0
        self.comments = []
        self.commentCount = 0

        #Processed data (extracted from raw data):
        self.topSubreddits = []
        self.sentimentAverage = 0.0
        self.sentimentHighestComment = Comment()
        self.sentimentLowestComment = Comment()
        self.lowestRatedComment = Comment()
        self.topRatedComment = Comment()
        self.sentimentRatios = {}


def guessUserLanguage(comments):
    """
    Accepts a list of comments and guesses the language of the user who generated them based on 15 randomly selected comments.
    Only generates a guess if at least 15 comments are provided.
    This is problematic for actively multilingual users but saves a decent amount of processing time and drains API funds slower.

    :param comments: List of comments based upon which the guess is to be made.
    :returns: RFC 5646 language code of the best guess or 'UNDEFINED' if filed to make a guess for whatever reason.
    """
    langSampleList = list()
    commentCount = len(comments)
    guessedLanguage = 'UNDEFINED'

    if(commentCount < 15):
        return 'UNDEFINED'
    else:
        # Extracts 15 random comments from the comment pool and get their language.
        commentRandomIndexList = random.sample(range(commentCount), 15) 
        for index in commentRandomIndexList:
           langSampleList.append(getLanguage(comments[index]))
        
        # Determines the most commonly occuring language in random sample.
        rankedLanguages = Counter(langSampleList).most_common()
        if rankedLanguages[0][0] == "UNDEFINED" and len(rankedLanguages) > 1:
            return rankedLanguages[1][0]
        return rankedLanguages[0][0]


def generateUserWithRawData(username) -> User:
    """
    Accepts a username and returns a User with populated raw data fields.
    Reads User's information from praw api, assigns the user a language, and assigns sentiment scores to all relevant comments.

    :param username: Name of the user to be generated.
    :returns: User with 'raw data' filled in
    """

    prawData = instantiate(username)
    prawDataComments = prawData[1]

    constructedUser = User()
    constructedUser.name = username
    constructedUser.karma = prawData[0]
    constructedUser.commentCount = len(prawDataComments)
 
    if(constructedUser.topRatedComment >= 20):
        constructedUser.language = guessUserLanguage(prawDataComments)

    # Loops over comments retrieved from praw api and processes relevant values for original comment and parent comment.
    for comment in prawDataComments:

        parentObj = Parent(
            score=comment['parent']['score'],
            contents=comment['parent']['body'],
            sentiment=(comment['parent']['body'], constructedUser.language)
        )

        commentObj = Comment(
            subreddit = comment['subreddit'],
            sentiment = getSentiment(comment['body'], constructedUser.language),
            score = comment['score'],
            contents = comment['body'],
            parent = parentObj,
        )

        constructedUser.comments.append(commentObj)

    return constructedUser


def processRawUserData(user):
    """
    Accepts a user with filled in 'raw data' fields, processes them and fills in 'processed data' fields.

    :param user: User object with filled in 'raw data'
    :returns: User with all data filled in.
    """

    #Determines favorite subreddits with ratio of all comments posted on each one.
    subReddits = [c.subreddit for c in user.comments]
    c = Counter(subReddits)
    c = c.most_common(3)
    for subreddit in c:
        subreddit[1] = subreddit[1]/user.commentCount
    user.topSubreddits = c

    #Determiens best and worst rated comment
    commentsSortedByScore = sorted(user.comments, key=lambda x: x.score)
    user.topRatedComment = commentsSortedByScore[0]
    user.lowestRatedComment = commentsSortedByScore[user.commentCount]

    #And so on...
    

def processUser(username):
    user = generateUserWithRawData(username)
    processRawUserData(user)

#processUser('spez')
#print(guessUserLanguage("HI"))
