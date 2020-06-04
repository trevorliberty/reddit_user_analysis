from flask import redirect, request, url_for, render_template, Response
from flask.views import MethodView, View
import models
from .processUser import processUser


def renderUser(user):
    return render_template(
        karma=user['karma'],
        lowestRatedComment=user['lowestRatedComment'],
        topRatedComment=user['topRatedComment'],
        sentimentAverage=user['sentimentAverage'],
        sentimentHighestComment=user['sentimentHighestComment'],
        sentimentLowestComment=user['sentimentLowestComment'],
        sentimentRatios=user['sentimentRatios'],  # object
        topSubreddits=user['topSubreddits']  # object
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
            model.insertUser(userObj)
            return renderUser(userObj)
