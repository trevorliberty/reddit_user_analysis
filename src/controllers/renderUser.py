from flask import redirect, request, url_for, render_template, Response
from flask.views import MethodView, View
import src.models as models
from .processUser import processUser, User


def renderUser(user):
    return render_template(
        'index.html',
        name=user.name,
        language=user.language,
        karma=user.karma,
        topSubreddits=user.topSubreddits,
        dominantSentiment=user.dominantSentiment,
        lowestRatedComment= {
            'contents' : user.lowestRatedComment.contents,
            'score' : user.lowestRatedComment.score,
            'subreddit' : user.lowestRatedComment.subreddit,
            'sentiment' : user.lowestRatedComment.sentiment,
        },
        topRatedComment= {
            'contents' : user.topRatedComment.contents,
            'score' : user.topRatedComment.score,
            'subreddit' : user.topRatedComment.subreddit,
            'sentiment' : user.topRatedComment.sentiment,
        },
        sentimentChangeRatios={
            'positiveToNegative': user.sentimentChangeRatios.positiveToNegative,
            'positiveToNeutral': user.sentimentChangeRatios.positiveToNeutral,
            'positiveToMixed': user.sentimentChangeRatios.positiveToMixed,
            'negativeToPositive': user.sentimentChangeRatios.negativeToPositive,
            'negativeToNeutral': user.sentimentChangeRatios.negativeToNeutral,
            'negativeToMixed': user.sentimentChangeRatios.negativeToMixed,
            'neutralToPositive': user.sentimentChangeRatios.neutralToPositive,
            'neutralToPositive': user.sentimentChangeRatios.neutralToPositive,
            'neutralToMixed': user.sentimentChangeRatios.neutralToMixed,
            'mixedToPositive': user.sentimentChangeRatios.mixedToPositive,
            'mixedToNegative': user.sentimentChangeRatios.mixedToNegative,
            'mixedToNeutral': user.sentimentChangeRatios.mixedToNeutral,
        },
        sentimentRatios={
            'positive': user.sentimentRatios.positive,
            'negative': user.sentimentRatios.negative,
            'neutral': user.sentimentRatios.neutral,
            'mixed': user.sentimentRatios.mixed
        },
    )


class userView(View):
    """
    View that handles a dispatch request that is overloaded
    """

    def dispatch_request(self, username):
        """
        Routes to the page of the user
        """
        model = models.init()
        user = model.getUser(username)
        if user:
            return renderUser(user)
        else:
            userObj = processUser(username)
            if userObj == 404:
                return Response(status=404)
            model.insertUser(userObj)
            return renderUser(userObj)
