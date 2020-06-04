###General notes
- pull in analysis of user comments
  -    we stream all of their comments (limited to the last 1000, we can probably get older comments if we go from back)
  - stream the parent comments as well 
- see the ratio of parent sentiment against user sentiment 


- if the parent is a submission, could generate a sentiment for that submission
    - start with text based submissions (self posts)
    - for articles
      - could generate a sentiment for the article
    - not text based:
      - generate a sentiment for the submission from all of the comments
- each of the above should analyze the parent comments 

add users you want to track and identify
route can be via the url for the user
    `website.com/api/<username>`

##Todos
- [ ] subreddits that host their most negative comments
- [ ] subreddits that host their most positive comments
- [ ] time of day for each comment
- [ ] average length per comment

###user analysis
- [ ]    most commented subreddit
- [ ]    general sentiment of the reddit user
- [ ]    sentiment over time