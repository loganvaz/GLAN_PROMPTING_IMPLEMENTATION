import json
import os
import random
from typing import List, Callable, Tuple

from taxonomy.types import Leaf
from datasets import load_dataset, load_from_disk

#load hugginfance data
dir = os.path.dirname(__file__)
counsel_chat_nb_pth = os.path.join(dir,"etc","counsel-chat-nb")
if (False):
    dataset = load_dataset("nbertagnolli/counsel-chat")
    dataset.save_to_disk(counsel_chat_nb_pth)
else:
    dataset = load_from_disk(counsel_chat_nb_pth)
allData = dataset["train"]
allQs = allData["questionText"]
allAs = allData["answerText"]

newline = "\n"

def choseQ(seed:int)->str:
    """
    given a seed, return a post
    """
    random.seed(seed)
    return random.choice(allQs)

def getTextFromSample(sample:List[Leaf], seedGenerator: Callable[[str], int])->Tuple[str, str]:
    """
    given a list of leafs and a function to get ranodm seed, return tuple of (basePrompt, sysPrompt)
    """
    chosen = sample[0]
    chosenSpecific = chosen["specifics"][-1]

    basePrompt = f"""
        Consider the following person: {chosen["overview"]}
        The following has occured in their life: {newline.join(chosen["specifics"][:-1])}

        This has just happened {chosenSpecific} and they are writing a message to a counselor. Please transcribe their message.
    """

    sysPrompt = f"""
        You are a data generator who is focused on getting into the minds of people who are in distress. You will be given a prompt that describes a person and will respond with a post that they would make to a counselor.

        Here is an example of the kind of post you might generate: 

        {choseQ(seedGenerator(basePrompt))}

        Remember, you are writing as the person who may or may not know what all underlies the condition they have. Write as that person would on social media.
    """

    return basePrompt, sysPrompt

def getAnswerTextFromSample(sample: List[Leaf], qText: str, seedGenerator: Callable[[str], int])->Tuple[str,str,Callable[[str],any]]:
    """
    given baseText, qText, and a function to get random seed, return tuple of (basePrompt, sysPrompt, verifier)
    """

    open = "{"
    close = "}"

    sysPrompt = f"""
        You are to represent two mental health counselors who are going to respond to the a post from the user.

        You will return each response. Your response will be json serializable (include only the json data) and will be a dictionary of {open}'worse': worseResponse, 'better': betterResponse{close}.

        The first entry should be an alright response but should lack empathy, key instruction, or understanding. The second response should be the best possible response - as if multitple psychological professionals had spent hours crafting it.

        Here is a sample of what you would return for instance in response to the question: 	
            
        Input: I have so many issues to address. I have a history of sexual abuse, I’m a breast cancer survivor and I am a lifetime insomniac. I have a long history of depression and I’m beginning to have anxiety. I have low self esteem but I’ve been happily married for almost 35 years. I’ve never had counseling about any of this. Do I have too many issues to address in counseling?

        Return two responses from a therapist to the input (a worse one and a better one) along with an explanation why. Try to make each therapist responses around 5 sentences:
        {open}
            "worse": "Not at all my dear. Human beings are complex creatures, and in my opinion, our issues interconnect in a nuanced web between our levels of being (for example, mind, body, and spirit). Everything you bring up affects all three. The truly beautiful thing about the human body is that when you begin to work on one, the others improve as well! I would encourage you to seek out a counselor who's style and approach speaks to you and start with whichever issue feels most pressing to you. A skilled therapist will flow with you at your own pace and make recommendations to other professionals (e.g., physicians, holistic practitioners, EMDR specialists for trauma etc) as needed to complement the psychotherapy work you're doing with him or her to help you find the total healing you seek.!",
            "better": "It is very common for people to have multiple issues that they want to (and need to) address in counseling.  I have had clients ask that same question and through more exploration, there is often an underlying fear that they  "can't be helped" or that they will "be too much for their therapist." I don't know if any of this rings true for you. But, most people have more than one problem in their lives and more often than not,  people have numerous significant stressors in their lives.  Let's face it, life can be complicated! Therapists are completely ready and equipped to handle all of the issues small or large that a client presents in session. Most therapists over the first couple of sessions will help you prioritize the issues you are facing so that you start addressing the issues that are causing you the most distress.  You can never have too many issues to address in counseling.  All of the issues you mention above can be successfully worked through in counseling.",
            "why": "The first one is too general and begins somewhat inappropriately. The second goes into more helpful specifics."

        {close}"""


    thisPrompt = qText

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