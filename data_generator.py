"""
this should generate training examples. Basically, it should utilize the taxonomy to create a series of Q/A pairs that the user can change based on modifications

I'm pretty sure the paper said to generate the Q/A in seperate requests. So the Q should just be what's generated based on the topic

First observation - there's a LOT of leaves and API requests are alr expensive af. So lets add a way to say - hey just generate k exaples (randomly select from the tree).

Second observation - we want consistent queries but randomness is also ideal if passing in examples to increase diversity. So we want to create some kind of text to example lookup.

Third observation - for any purpose, we will need a way to get all the children. From there, a way to sample (randomly) k of them. Ideally, this would all be seeded so we hit the GPT cache as much as possible.

Foruth observation - despite paper, lets use 3.5 for $ saving

Steps

  Function to randomly chose k children from tree s.t. they share same root at level n
    can generate combinatorical examples like they did in the paper

   Custom
    Data Generator to choose sample input for question formation
    Data Generator to choose sample output for answer formation
        Shared:
            hash for sample selection(s) for question
            hash for sample selection(s) for answers
"""

def TODO():
    raise Exception("not done yet")

import asyncio
from typing import List, Optional, Tuple, TypeVar
from data_generator_internshipConfig import getAnswerTextFromSample, getTextFromSample
from taxonomy.types import Node, Leaf
from taxonomy.prompter import prompt
from pathlib import Path
import os
import json
dir = os.path.dirname(__file__)
qDir = os.path.join(dir, "qas", "q")
aDir = os.path.join(dir, "qas", "a")
Path(qDir).mkdir(parents=True, exist_ok=True)
Path(aDir).mkdir(parents=True, exist_ok=True)

def getJson(path:str):
    if (os.path.exists(path)): 
        with open(path, 'r') as f:
            return json.load(f)
    return {}


questionsDir = os.path.join(qDir, "questions.json")
questions = getJson(questionsDir)
answersDir = os.path.join(aDir, "answers.json")
answers = getJson(answersDir)

class WeighedNode(Node['WeighedNode']):
    weight: int
    def __init__(self, children: List["WeighedNode"], topic: Optional[str], payload: Optional['Leaf'], weight:int):
        super().__init__(children=children, topic=topic, payload=payload)
        self.weight = weight
    

def make_weighed_node(node:Node)->WeighedNode:
    if (not len(node.children)):
        return WeighedNode(children=[], topic=node.topic, payload=node.payload, weight=1)
    else:
        children = [make_weighed_node(child) for child in node.children]
        return WeighedNode(children=children, topic=node.topic, payload=node.payload, weight=sum([child.weight for child in children]))


import random

random.seed(42)
#function to get k children s.t. they share same parent at least one level up

def get_k_children(graph:WeighedNode, k, level,  depth =-1)->Tuple[List[Leaf], WeighedNode]:
    """
        k: nuber of examples 
        depth: heihgt of tree
    """
    def choose_k_descendants(sharedAncestor:WeighedNode, numChoose)->List[Leaf]:
        """
        From here, randomly choose k leaves as descendents
        """
        assert(sharedAncestor.weight >= numChoose)
        #chosen leaf
        if (not len(sharedAncestor.children)):
            assert(sharedAncestor.payload)
            return [sharedAncestor.payload]

        allocations = [0]*len(sharedAncestor.children)
        idxs = list(range(len(sharedAncestor.children)))
        # Distribute the points
        weights = [child.weight for child in sharedAncestor.children]
        for _ in range(numChoose):
            # Choose a child randomly, with probability proportional to weight
            chosen_child_idx = random.choices(idxs, weights)[0]
            weights[chosen_child_idx] -= 1
            allocations[chosen_child_idx] += 1
        
        toRets = list()
        for (child, alloc) in zip(sharedAncestor.children, allocations):
            if (alloc):
                toRets += choose_k_descendants(child, alloc)

        return toRets

    #level should be at least 1
    assert(depth!=0)
    assert(level >=1)
    #we need to calculate the depth
    if (depth == -1):
        depth = 0
        temp = graph
        while (len(temp.children)):
            temp = temp.children[0]
            depth += 1

    #this children have payloads of leaves
    if (depth == level):
        #choose a shared ancestor here
        shared = random.choice(graph.children)
        return (choose_k_descendants(shared, k), shared)

    shared = random.choice(graph.children)
    return get_k_children(shared, k, level, depth-1)



#function to hash text to a list of numbers (honestly - lets take a hash, use random.seed, then shuffle and select first k want)
import hashlib
def hash_text(text:str):
    hash_object = hashlib.md5(text.encode())
    hash_int = int(hash_object.hexdigest(), 16)
    return hash_int
    # random.seed(hash_int)
    # return random.sample(toSample, k)

#for k in NUM_SAMPLES
NUM_SAMPLES = 256
NUM_LEAFS = 2
LEVEL = 2
BATCH_SIZE = 4

#question generation
pth = os.path.join(os.path.dirname(__file__), "taxonomy","storage", "createdTaxonomy.json" )
assert(os.path.exists(pth))
graph = Node.nodeFromJson(json.load(open(pth, 'r')))
weighedGraph = make_weighed_node(graph)
print("weighted graph is ", weighedGraph)

async def generate_samples()->None:
    samples:List[List[Leaf]] = list()
    for i in range(NUM_SAMPLES):
        samples.append(get_k_children(weighedGraph, NUM_LEAFS, LEVEL)[0])
        
    for i in range(0, len(samples), BATCH_SIZE):
        subSamples = samples[i:i+BATCH_SIZE] 
        promisedQs = list() 
        metas = list()
        print("question gen")
        for sample in subSamples:
            #user defined
            text, sysPrompt = getTextFromSample(sample, hash_text)
            metas.append({
                "text": text,
                "sysPrompt": sysPrompt
            })

            promisedQ = prompt(sysPrompt, text)
            promisedQs.append(promisedQ)
        
        batchQs = await asyncio.gather(*promisedQs)

        # answers = dict()
        answerPromises = list()
        answerMeta = list()

        print("answer gen")
        verifier = lambda x : x
        for aNum in range(1):
            #store our question info and generate our answe info
            for sample, meta, q in zip(samples, metas, batchQs):
                _id = len(questions)
                questions[_id] = {
                    "text": meta["text"],
                    "sysPrompt": meta["sysPrompt"],
                    "q": q
                }

                #now we can get the answers 
                #how many propmts / answer
                text, sysPrompt, verifier = getAnswerTextFromSample(sample, meta["text"], hash_text)

                # if (not _id in answers): answers[_id] = list()
                answer = prompt(sysPrompt, text, verifier=verifier)
                answerPromises.append(answer)
                answerMeta.append(
                    {
                        "id": _id,
                    }
                )
        
        batchAs = await asyncio.gather(*answerPromises)
        for a, aMeta in zip(batchAs, answerMeta):
            _id = aMeta["id"]
            if (not _id in answers): answers[_id] = list()
            if (not a in answers[_id]):
                answers[_id].append(verifier(a))
        
        with open(questionsDir, 'w') as f:
            json.dump(questions, f)

        #now, we can save our answers
        with open(answersDir, 'w') as f:
            json.dump(answers, f)

        break

        

asyncio.run(generate_samples())
#get data for children (list of selected leaves)

#take the list of selected leaves into a prompt for gpt 
    #list -> txt (user defined)
    #txt -> seed (us)
    #seed -> example -> final txt (user defined)

#iterate over answer generation instructions
    #for each answe instruction -> txt -> seed (us) -> new example (user) -> final txt (user)
    #prompt gpt for answer
    #store all answers in output