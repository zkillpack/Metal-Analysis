import glob
import csv
import heapq
# Takes the weighted adjacency matrix csvs
# for INDIVIDUAL subreddits and creates a reduced csv for visualization in
# Gephi

# Best N paths are kept in graph
N = 5

for f in glob.glob("analyzed/*.csv"):
    r = csv.reader(open(f, "r"))
    w = csv.writer(open("gephi/" + f[9:-13] + "gephi.csv", "w"))
    w.writerow(["Source", "Target", "Weight"])

    pairs = set()
    vocab = []
    row_accum = []
    current_word = ""

    for i, row in enumerate(r):
        row_accum = []
        for j, val in enumerate(row):
            if i == 0:
                if j == 0:
                    continue
                vocab.append(val)
            else:
                if j == 0:
                    current_word = val
                    continue
                else:
                    heapq.heappush(row_accum, (1 - float(val), vocab[j - 1]))

        strongest_links = heapq.nlargest(N, row_accum, lambda x: x[0])

        for link in strongest_links:
            # not directed; ignore duplicates
            if(link[1], current_word) in pairs:
                continue
 
            pairs.add((current_word, link[1]))
            w.writerow([current_word, link[1], "%.3f" % link[0]])
