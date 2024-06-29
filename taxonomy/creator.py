#generate the taxonomy of reports
import types
from typing import Iterable, List, Tuple, TypedDict
from .prompter import prompt as prompt_gpt
import json
import asyncio

MODEL = "gpt-3.5-turbo"

class Leaf(TypedDict):
    overview: str
    specifics: List[str]
    parent: 'Node'

class Node(TypedDict):
    children: List['Node']
    topic: str|None
    payload: None|Leaf 

async def generateBranches(parent: Node, prompt: str, levelCreator: Tuple[str,int|None])->List[Node]:
    # construct our gpt prompt
    thisPrompt = levelCreator[0]
    if (parent["topic"]):
        thisPrompt += "Consider " + parent["topic"]
    if (levelCreator[1]):
        prompt += "\nYou should generate " + str(levelCreator[1]) + " examples."
    
    #use the gpt prompt 
    output = await prompt_gpt(prompt, thisPrompt,MODEL )
    #parse them into multiple topics
    # print("output is ", output)
    allTopics = [o for o in output.split("\n") if len(o.strip())]
    print("allTopics is ", allTopics)

    return [Node(children=[], topic= t, payload=None) for t in allTopics]
    
async def generateLeaves(parent: Node, levelCreator: Tuple[str, int])->List[Node]:
    
    sysPrompt = "You are an endpoint that will return a json object that is a list of dictionaries as described. Remember to format correctly. It is of the form [{overview: str, specifics: List[str]}] Given a topic, you will do the following: " + levelCreator[0] +"\nYou will generate " + str(levelCreator[1]) + " entires in this list. Remember, make sure the response is JSON serializable. Return nothing but the json string."
    #use the gpt prompt 

    def verifier(s:str):
        # print("s is ", s)
        _json = json.loads(s)
        if (not isinstance(_json, list)):
            raise Exception("Expected a list")
        for item in _json:
            # print("item is ", item)
            assert("overview" in item)
            assert("specifics" in item)
            assert(isinstance(item["overview"], str))
            assert(isinstance(item["specifics"], list))
             

    allLeaves = await prompt_gpt(sysPrompt, parent["topic"], MODEL, verifier)
    # print("allLeaves is ", allLeaves)
    #parse them into multiple leaves

    _json = json.loads(allLeaves)
    return [Node(children= [], topic=None, payload = leaf) for leaf in _json]


    #return all the Nodes
    return []

async def propogateTree(root: Node, generalTreePrompt: str, levelCreator:List[Tuple[str,int|None]], nodeCreator: Tuple[str, int]):
    #base case
    if (not len(levelCreator)):
        #generate leaves and add them 
        leaves = await generateLeaves(root, nodeCreator)
        for leaf in leaves:
            root["children"].append(leaf)
        return []
    
    #get all branches
    branches = await generateBranches(root, generalTreePrompt, levelCreator[0])
    for branch in branches:
        # propogateTree(branch, generalTreePrompt, levelCreator[1:], nodeCreator)
        root["children"].append(branch)
    return branches

    #propogare each of them



async def make_async(r):
    return [r]

async def createTaxonomy(generalTreePrompt: str, levelCreator:List[Tuple[str,int|None]], nodeCreator: Tuple[str, int])->Node:
    #create the root node
    root = Node(children=[], topic="", payload=None)

    Q:List[Tuple[types.Coroutine[List[Node]], List[Tuple[str,int|None]]]] = list()

    # firstItem = async lambda x : (root, levelCreator)
    Q.append((make_async(root), levelCreator))

    currentLength = len(levelCreator)
    toPrints:List[str] = list()
    while (len(Q)):
        print("len(Q) is ", len(Q), "currentLength is ", currentLength)
        
        promises = [item[0] for item in Q]  # Extract all promises from Q
        ls = [item[1] for item in Q]  # Extract all l values from Q
        Q.clear()  # Clear Q for the next batch of promises

        results = await asyncio.gather(*promises)  # Wait for all promises to resolve
        for rs, l in zip(results, ls):
            for r in rs:
                if (len(l) < currentLength):
                    currentLength = len(l)
                    print("\n".join(toPrints))
                    print("\n\n\n______next____level______\n\n\n")
                    input()
                    toPrints = list()

                if (r["topic"]): toPrints.append(r["topic"])
                result = propogateTree(r, generalTreePrompt, l, nodeCreator)
                Q.append((result, l[1:]))
                # r2 = result 
                # l2 = l[1:]

                # if (len(r2)):
                #     for rnext in r2:
                #         Q.append((rnext, l2))

    return root