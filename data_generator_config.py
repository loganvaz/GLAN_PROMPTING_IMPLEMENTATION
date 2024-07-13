import json
import os
import random
from typing import Callable, Dict, List, Tuple

from taxonomy.types import Leaf

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

newline = "\n"

def choseQ(seed:int)->str:
    """
    given a seed, return a post
    """
    random.seed(seed)
    return random.choice(allQs)

def choseA(seed:int)->Dict[str,any]:
    """
    given a seed, return a post
    """
    random.seed(seed)
    q = random.choice(allQs)
    idx = allQs.index(q)
    return allAs[idx]

def getTextFromSample(sample:List[Leaf], seedGenerator: Callable[[str], int])->Tuple[str, str, Callable[[str], any]]:
    """
    given a list of leafs and a function to get ranodm seed, return tuple of (basePrompt, sysPrompt)
    """

    skillSets = "\n".join([s["overview"] for s in sample])
    # print("sample is ", sample)
    projects = "\n".join([ "\n".join([str(s_) for s_ in s.get("specifics", s.get("instances"))]) for s in sample])

    basePrompt = f"""
        Consider the following person with the following skill sets: {skillSets}
        They have worked on the following projects: {projects}

        You will use this base knowledge to create a profile for them (similar to the one you will be provided as an example). Output should be a json of the correct format. Make sure to make the resume about the same length as provided.
    """

    sysPrompt = f"""
        You are a data generator generating sample profiles for users in a job searching database. Here is an example below:
        {choseQ(seedGenerator(basePrompt))}
    """
    def verifier(s):
        print("s is ", s)
        j = json.loads(s)
        assert("userId" in j)
        #assert type is string
        assert(isinstance(j["userId"], str))
        assert("major" in j)
        assert(isinstance(j["major"], str))
        assert("gradYear" in j)
        # j["gradYear"] = int(j["gradYear"])
        # assert(isinstance(j["gradYear"], int))
        assert("positionInterestList" in j)
        assert(isinstance(j["positionInterestList"], list))
        for item in j["positionInterestList"]:
            assert(isinstance(item, str))
        assert("resume" in j)
        assert(isinstance(j["resume"], str))
        return j

    return basePrompt, sysPrompt, verifier

def getAnswerTextFromSample(sample: List[Leaf], qText: str, seedGenerator: Callable[[str], int], input: any)->Tuple[str,str,Callable[[str],any]]:
    """
    given baseText, qText, and a function to get random seed, return tuple of (basePrompt, sysPrompt, verifier)
    """

    open = "{"
    close = "}"
    
    A = choseA(seedGenerator(qText))
    Q = choseQ(seedGenerator(qText))

    sysPrompt = f"""
        You are to come up with two job postings for an input user. One will be a better fit for them. The other will be a worse fit for them.
                
        There can be a variety of reasons for better/worse fit. The candidate might be overqualified for one position, the pay might be wrong, the skill set might not align, etc. But one should be a better fit (i.e. one if they can only apply to one, there is one they should apply to).

        Here is a sample input/output pair:

        Input: {Q}
        Return two responses from a therapist to the input (a worse one and a better one) along with an explanation why. Make each look like a proper posting as passed in but change the data. Make sure one is the better choice and explain why the one under the "better" key is better than the one under the "worse" key. Use the exact key words.:
        {open}
            "worse": {A["worse"]},
            "better":{A["better"]},
            "why": "enter an explanation on why one is better or worse here"
        {close}"""


    thisPrompt = str(input)

    def verifier(txt):
        print("txt is ", txt)
        _json = json.loads(txt)
        print("loaded")
        assert(isinstance(_json, dict))
        print("Asserted dict")
        assert(len(_json) == 3 or len(_json) == 2)
        print("asserted len")
        for item in _json.keys():
            assert(item in ["worse", "better", "why"])
        return _json
    
    return thisPrompt, sysPrompt, verifier