import praw
import re
import pickle
from requests.exceptions import HTTPError

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
hairmetal - 44
powermetal - 41
stonermetal - 29
atmosphericmetal - 27
thrash
NWOBHM - 20
symphonicblackmetal - 18
undergroundmetal - 17
symphonicmetal - 12
alternativemetal - 2"""

regex = re.compile("[A-Z|a-z|_]+")
subreddits = re.findall(regex, subs)

r = praw.Reddit(user_agent='folk_metal_data_scraper')

for sub in subreddits:
    for attempt in range(3):
        try:
            subreddit = r.get_subreddit(sub)
            comments = {}
            submissions = {}
            print "Processing documents in %s..." % sub
            for i, submission in enumerate(subreddit.get_hot(limit=1000)):
                try:
                    submission.replace_more_comments()
                    submission_comments = []
                    # Get text of each comment
                    for comment in praw.helpers.flatten_tree(submission.comments):
                        submission_comments.append(comment.body)
                    print "Processing document %d (%d comments)" % ((i + 1), len(submission_comments))

                    try:
                        submissions[submission.title] = submission.selftext
                    except:
                        print "\nEmpty selftext for %d!\n" % (i + 1)

                    try:
                        comments[submission.title] = submission_comments
                    except:
                        print "\nEmpty comments for %d!\n" % (i + 1)

                except:
                    print "\nError getting data for %d!\n" % (i + 1)

        except HTTPError as e:
            print "HTTP Error %d while processing %s! Retrying..." % (e.response.status_code, sub)

        print "Writing data for %s...\n\n\n" % sub

        with open("/unprocessed/" + sub + "_posts.pkl", "w") as f:
            pickle.dump(submissions, f)

        with open("/unprocessed/" + sub + "_comments.pkl", "w") as f:
            pickle.dump(comments, f)

        break
