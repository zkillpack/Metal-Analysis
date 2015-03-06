import praw
from praw.handlers import MultiprocessHandler
import json
from requests.exceptions import HTTPError
import re
import pickle

subs = """
folkmetal - 223
progmetal - 1,182
metalmusicians - 458
doommetal - 447
death_metal - 435
Metalcore - 359
TechnicalDeathMetal - 318
TrueMetal - 289
postmetal - 226
black_metal - 218
ClassicMetal - 174
BlackMetal - 151
melodicdeathmetal - 139
Heavymetal - 121
thrashmetal - 119
melodicmetal - 109
grindcore - 100
Deathcore - 84
Deathmetal - 84
numetal - 60
powerviolence - 59
heavy_metal - 54
hairmetal - 44
powermetal - 41
stonermetal - 29
atmosphericmetal - 27
thrash
NWOBHM - 20
symphonicblackmetal - 18
undergroundmetal - 17
symphonicmetal - 12
DLA - 12
modernmetal - 2
alternativemetal - 2"""

regex = re.compile("[A-Z|a-z|_]+")
subreddits = re.findall(regex, subs)

handler = MultiprocessHandler()

r = praw.Reddit(user_agent = 'folk_metal_data_scraper', handler=handler)
r.set_oauth_app_info(client_id='Sv9IBD6DaCujxA', client_secret = '6vKQ6IBvyXw-6b6k59NyS67gt44', redirect_uri='http://127.0.0.1:65010/authorize_callback')


# Get as many submissions for /r/folkmetal as the API will allow

for sub in subreddits:
    for attempt in range(3):
        try:
            subreddit = r.get_subreddit(sub)
            comments = {}
            submissions = {}
            print "Processing documents in %s..." % sub
            for i, submission in enumerate(subreddit.get_hot(limit=10000)):  
                try:
                    submission.replace_more_comments()
                    submission_comments = []
                    # Get text of each comment
                    for comment in praw.helpers.flatten_tree(submission.comments):
                        submission_comments.append(comment.body)
                    print "Processing document %d (%d comments)" % ((i+1), len(submission_comments))

                    try:
                        submissions[submission.title] = submission.selftext
                    except:
                        print "\nEmpty selftext for %d!\n" % (i+1)

                    try:
                        comments[submission.title] = submission_comments
                    except:
                        print "\nEmpty comments for %d!\n" % (i+1)


                except:
                    print "\nError getting data for %d!\n" % (i+1)
           
          

        except HTTPError as e:
            print "HTTP Error %d while processing %s! Retrying..." % (e.response.status_code, sub)


        print "Writing data for %s...\n\n\n" % sub

        with open("C:\\users\\dakota\\reddit_scraper\\"+sub+"_posts.pkl", "w") as f:
            pickle.dump(submissions,f)

        with open("C:\\users\\dakota\\reddit_scraper\\"+sub+"_comments.pkl", "w") as f:
            pickle.dump(comments,f)

        break