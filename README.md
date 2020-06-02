430project
    praw reddit
        CommentForrest
pull in analysis of user comments
    we stream all of their comments (limited to the last 1000, we can probably get older comments if we go from back)
        stream the parent comments as well 
        see the ratio of parent sentiment against user sentiment
            go through parent comment store what sentiment that 
    subreddits that host their most negative comments
    subreddits that host their most positive comments
    time of day for each comment
    average length per comment
    each of the above should analyze the parent comments 
user
    most commented subreddit
    general sentiment of the reddit user
    sentiment over time

analyze subreddits
    Text sentiment analysis
        https://rapidapi.com/insights-ml-insights-ml-default/api/google-text-analysis?endpoint=apiendpoint_622af2ed-9fd0-420f-b39c-5d89d7dc0df7
repository for reddit user information
add users you want to track and identify
route can be via the url for the user
    website.com/api/<username>
