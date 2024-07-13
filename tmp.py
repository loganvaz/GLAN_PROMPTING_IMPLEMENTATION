import json
import os

allQs = list()
allAs = list()
#load user profiles
dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "functions","databases", "profiles")
jsonPath = os.path.join(dir, "just_resume.json")
with open(jsonPath, 'r') as f:
    data = json.load(f)
    for k, v in data.items():
        del v["embedding"]
        data[k] = v
qDict = data


getPostingLookup = dict()
def get_posting(postingId:str):
    dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "functions","databases", "postings", "just_posting.json")
    if ((dir, postingId) in getPostingLookup): return getPostingLookup[(dir, postingId)]
    with open(dir, 'r') as f:
        data = json.load(f)
        selectedPosting = data[postingId]
        print("selectedPosting is ", selectedPosting)
        del selectedPosting["embedding"]
        getPostingLookup[(dir, postingId)] = selectedPosting
        return selectedPosting



#for each of these, we can make a better/worse tuple
dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "functions","training_examples", "train", "hand_labeled")
jsonPath = os.path.join(dir, "results.json")
with open(jsonPath, 'r') as f:
    data = json.load(f)
    for uid, metaDatas in data.items():
        print("\n"*10)
        for metaData in metaDatas:
            print(metaData)
            orderedPostings = metaData["postingIds"]
            for idx, postingId in enumerate(orderedPostings):
                for betterPostingId in orderedPostings[idx+1:]:
                    allAs.append({
                        "worse": get_posting(postingId),
                        "better": get_posting(betterPostingId)
                    })
                    allQs.append(qDict[uid])

print("allQs is ", len(allQs))
print("allAs is ", len(allAs))