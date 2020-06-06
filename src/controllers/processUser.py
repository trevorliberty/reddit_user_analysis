from apis.praw import instantiate
from apis.textAnalysis import getLanguage, getSentiment, getComplexity
from collections import Counter
import random
"""
Contains functionality for querying and processing reddit user information.
"""

class Parent():
    """
        Used to store parent comment information inside 'Comment' objects.
    """
    def __init__(self, score=0, contents=None, sentiment=None):
        self.score = score
        self.contents = contents
        self.sentiment = sentiment

    def display(self):
        print('***** Parent *****')
        print(f'Score: {str(self.score)}')
        print(f'Contents: {self.contents}')
        print(f'Sentiment: {str(self.sentiment)}')
        print('*****')


class Comment():
    """
        Used to store comment information inside 'User' objects.
    """
    def __init__(self, score=0, contents=None, subreddit=None, sentiment=None, parent=None):
        self.score = score
        self.contents = contents
        self.subreddit = subreddit
        self.sentiment = sentiment
        self.parent = parent

    def display(self):
        print('***** Comment *****')
        print(f'Score: {str(self.score)}')
        print(f'Contents: {self.contents}')
        print(f'Sentiment: {str(self.sentiment)}')
        print(f'Subreddit: {self.subreddit}')
        print(f'ParentComment: ')
        self.parent.display()
        print('*****')


class SentimentChangeRatios():
    """
        Used to store information about sentiment change between parent comment and user comment inside 'User' objects.
    """
    def __init__(self):
        self.positiveToNegative = 0
        self.positiveToNeutral = 0
        self.positiveToMixed = 0
        self.negativeToPositive = 0
        self.negativeToNeutral = 0
        self.negativeToMixed = 0
        self.neutralToPositive = 0
        self.neutralToNegative = 0
        self.neutralToMixed = 0
        self.mixedToPositive = 0
        self.mixedToNegative = 0
        self.mixedToNeutral = 0
    def display(self):
        print('***** Sentiment change ratios: *****')
        print(self.positiveToNegative)
        print(self.positiveToNeutral)
        print(self.positiveToMixed)
        print(self.negativeToPositive)
        print(self.negativeToNeutral)
        print(self.negativeToMixed)
        print(self.neutralToPositive)
        print(self.neutralToNegative)
        print(self.neutralToMixed)
        print(self.mixedToPositive)
        print(self.mixedToNegative)
        print(self.mixedToNeutral)
        print('*****')


class SentimentRatios():
    """
        Used to store information about comment sentiment ratios inside 'User' objects.
    """
    def __init__(self):
        self.positive = 0
        self.negative = 0
        self.neutral = 0
        self.mixed = 0
    def display(self):
        print('***** Sentiment ratios: *****')
        print(self.positive)
        print(self.negative)
        print(self.neutral)
        print(self.mixed)
        print('*****')


class User():
    """
        Used object stores all information collected about a reddit user.
    """
    def __init__(self):
        #Raw data (data to be read from praw and assigned sentiment values)
        self.name = "UNDEFINED"
        self.language = "UNDEFINED"
        self.karma = 0
        self.comments = []
        self.commentCount = 0

        #Processed data (extracted from raw data):
        self.topSubreddits = []
        self.dominantSentiment = "UNDEFINED"
        self.lowestRatedComment = Comment()
        self.topRatedComment = Comment()
        self.sentimentChangeRatios = SentimentChangeRatios()
        self.sentimentRatios = SentimentRatios()

        def display(self):
            print('################# USER: #################')
            print("Name: " + self.name)
            print("Language: " + self.language)
            print("Karma: " + self.karma)
            print("Comment count: " + self.commentCount)

            #Processed data (extracted from raw data):
            print("Top subreddtis:")
            for subreddit in self.topSubreddits:
                print(subreddit)
            print("Sentiment Average: " + self.dominantSentiment)
            self.lowestRatedComment.display()
            self.topRatedComment.display()
            print('#########################################')



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

    constructedUser = User()
    constructedUser.comments = prawData[1]
    constructedUser.name = username
    constructedUser.karma = prawData[0]
    constructedUser.commentCount = len(constructedUser.comments)
 
    if(constructedUser.commentCount >= 20):
        rawCommentArray = []
        for comment in constructedUser.comments:
            rawCommentArray.append(comment['body'])
        constructedUser.language = guessUserLanguage(rawCommentArray)

    # Loops over comments retrieved from praw api and processes relevant values for original comment and parent comment.
    for comment in constructedUser.comments:
        print("***************************")
        print(comment)
        print("***************************")

        #Determines sentiment for comment and parent comment.
        print(type(comment))
        if isinstance(comment, Comment):
            print(comment.contents)
        else:
            commentSentiment = getSentiment(comment['body'], constructedUser.language)
        parentCommentSentiment = 'UNDEFINED'
        #Only determiens parent comment sentiment if child sentiment is defined since it won't be needed otherwise.
        if commentSentiment != 'UNDEFINED': 
            try:
                parentCommentSentiment = getSentiment(comment['parent']['body'], constructedUser.language)
            except:
                parentCommentSentiment = None


        parentObj = Parent(
            score=comment['parent']['score'],
            contents=comment['parent']['body'],
            sentiment=parentCommentSentiment
        )

        commentObj = Comment(
            subreddit = comment['subreddit'],
            sentiment = commentSentiment,
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
    user = User()

# Determine favorite subreddits with ratio of all comments posted on each one.
    subreddits = [c.subreddit for c in user.comments]
    c = Counter(subreddits)
    c = c.most_common(3)
    for subreddit in c:
        user.topSubreddits.append({subreddit[0], subreddit[1]/user.commentCount})

# Determine best and worst rated comment
    commentsSortedByScore = sorted(user.comments, key=lambda x: x.score)
    user.topRatedComment = commentsSortedByScore[0]
    user.lowestRatedComment = commentsSortedByScore[user.commentCount - 1]

# Process comment sentiment data. 
    commentsWithValidSentiment = 0
    commentPairsWithValidSentiment = 0
    for comment in user.comments:
        #Increment before operations
        commentPairsWithValidSentiment += 1
        commentsWithValidSentiment += 1

        if comment.sentiment == 'POSITIVE':
            comment.sentimentRatios.positive += 1
            if comment.parent.sentiment == 'NEGATIVE':
                user.sentimentChangeRatios.negativeToPositive += 1
            elif comment.parent.sentiment == 'NEUTRAL':
                user.sentimentChangeRatios.neutralToPositive += 1
            elif comment.parent.sentiment == 'MIXED':
                user.sentimentChangeRatios.mixedToPositive += 1
            else:
                commentPairsWithValidSentiment -= 1
        
        elif comment.sentiment == 'NEGATIVE':
            comment.sentimentRatios.negative += 1
            if comment.parent.sentiment == 'POSITIVE':
                user.sentimentChangeRatios.positiveToNegative += 1
            elif comment.parent.sentiment == 'NEUTRAL':
                user.sentimentChangeRatios.neutralToNegative += 1
            elif comment.parent.sentiment == 'MIXED':
                user.sentimentChangeRatios.mixedToNegative += 1
            else:
                commentPairsWithValidSentiment -= 1

        elif comment.sentiment == 'NEUTRAL':
            comment.sentimentRatios.neutral += 1
            if comment.parent.sentiment == 'POSITIVE':
                user.sentimentChangeRatios.positiveToNeutral += 1
            elif comment.parent.sentiment == 'NEGATIVE':
                user.sentimentChangeRatios.negativeToNeutral += 1
            elif comment.parent.sentiment == 'MIXED':
                user.sentimentChangeRatios.mixedToNeutral += 1
            else:
                commentPairsWithValidSentiment -= 1

        elif comment.sentiment == 'MIXED':
            comment.sentimentRatios.mixed += 1
            if comment.parent.sentiment == 'POSITIVE':
                user.sentimentChangeRatios.positiveToMixed += 1
            elif comment.parent.sentiment == 'NEGATIVE':
                user.sentimentChangeRatios.negativeToMixed += 1
            elif comment.parent.sentiment == 'NEUTRAL':
                user.sentimentChangeRatios.neutralToMixed += 1
            else:
                commentPairsWithValidSentiment -= 1

        else: #If the comment is 'UNDEFINED', then we've failed to fined either a valid comment or comment pair.
            commentPairsWithValidSentiment -= 1
            commentsWithValidSentiment -= 1

    if(commentsWithValidSentiment > 0):
        user.sentimentRatios.positive /= commentsWithValidSentiment
        user.sentimentRatios.negative /= commentsWithValidSentiment
        user.sentimentRatios.neutral /= commentsWithValidSentiment
        user.sentimentRatios.mixed /= commentsWithValidSentiment

        dominantSentimentCount = max([user.sentimentRatios.positive, user.sentimentRatios.negative, user.sentimentRatios.neutral, user.sentimentRatios.mixed])        
        if(dominantSentimentCount == user.sentimentRatios.positive):
            user.dominantSentiment = "POSITIVE"
        if(dominantSentimentCount == user.sentimentRatios.negative):
            user.dominantSentiment = "NEGATIVE"
        if(dominantSentimentCount == user.sentimentRatios.neutral):
            user.dominantSentiment = "NEUTRAL"
        if(dominantSentimentCount == user.sentimentRatios.mixed):
            user.dominantSentiment = "MIXED"


    if(commentPairsWithValidSentiment > 0):
        user.sentimentChangeRatios.positiveToNegative /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.positiveToNeutral /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.positiveToMixed /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.negativeToPositive /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.negativeToNeutral /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.negativeToMixed /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.neutralTkoPositive /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.neutralToNegative /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.neutralToMixed /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.mixedToPositive /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.mixedToNegative /= commentPairsWithValidSentiment
        user.sentimentChangeRatios.mixedToNeutral /= commentPairsWithValidSentiment


def processUser(username):
    user = generateUserWithRawData(username)
    processRawUserData(user)
    #user.display()

processUser('spez')
#print(guessUserLanguage("HI"))
