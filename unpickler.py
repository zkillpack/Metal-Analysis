import glob
import pickle
import csv

# Writes scraped data to CSVs
for f in glob.glob("*posts.pkl"):
    with open(f, "rb") as postfile:
        posts = pickle.load(postfile)
        with open(f[:-9] + "comments.pkl", "rb") as commentfile:
            comments = pickle.load(commentfile)
            w = csv.writer(open(f[:-3] + "csv", "w"))
            w.writerow(("Post", "Comment"))
            for k in comments.iterkeys():
                w.writerow([unicode.encode(s, "utf-8")for s in (k, posts[k])])
                for comment in comments[k]:
                    w.writerow([unicode.encode(s, "utf-8")
                                for s in (k, comment)])
