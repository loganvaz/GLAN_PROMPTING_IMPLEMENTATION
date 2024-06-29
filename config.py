
from typing import List

"""
You will want to set the following variables to get started (and can obviously change more as you see fit)
    treeInstructions: List[str] - a list of instructions for the tree prompts. The first one generates the first layer of the tree. From each item generated from the previous layer the next layer is applied.

    treeExamples: List[str] - a list of examples for the tree prompts. These should be examples of what the treeInstructions would generate.

    treeNumber: List[int|None] - a list of the number of examples to generate for each tree prompt. If None, GPT will decide. Based on prompting if gives (3,4,3) tree will be of size (3,12,36, leafSize)

    generalInstructions: the system prompt to give gpt. Basically, just tell it what you're using this for.

    classInstructionBase: What you want each leaf to represent. The return will be a list of the form {"overview": string, "specifics": List[]}[] so instruct gpt to fill it out as you would.

    numClass: the number of leavees to generate
"""

#the initial list to base the tree off - in general case, leave blank and make the first tree instruction what generates this
seedList = []# ["depression", "relation", "family", "romantic", "trauma", "anger-management", "addiction", "sexuality", "behavior"]
#node general modifications
treeInstructions = [
    "Generate a list of mental health disorders/things that contribute to bad mental health. This can be life circumstances (e.g. loss of loved one), mental (e.g. body dismorphia), or some combination. Try to keep each of these discrete from each other but overlap them as necessary",
    "Break this into more specifics. This should still be a general category. Try to cover as much space as possible with as little overlap as possible. Remember to include the prior topic in this description as well",
    "Break this down one level further, getting more specific. Remember to still include previous categories. Try to cover as much space as possible (as little overlap as possible)"
]

treeExamples = [
    "PTSD\nOCD\nAcademic Failure",
    "Physical Assult (PTSD)\nWar (PTSD)\nSexual Assult (PTSD)",
    "WW1 shellshock (War (PTSD))\nWW2 shellshock (War (PTSD))\nVietnam War (War (PTSD))\nMedical Trauma (War (PTSD))"
]

treeNumber: List[int|None] = [5,3,3]

generalInstructions = "You are a mental health professional tasked with breaking things down into broad yet distinct categories and specifying them with more time. Generate a list, but remember you are restricted to the number of examples requested. Unless told otherwise, give only the name - not a description. Include in parenthesis only the topic stem provided. IE if provided with magical and generating unicorns I would have my entry be unicorns (magical). Your goal is to take different topics and break them down into further mental health categories. Remember, add the end of the day this is about breaking things down into mental health conditions where a therapist could give helpful advice."

#leaf general modifications
numClass = 5

#gpt
MODEL = "gpt-3.5-turbo"



#further construciton
assert(len(treeNumber) == len(treeExamples))
assert(len(treeInstructions) == len(treeExamples))

text = [instruction + "\nHere is an example:" + example for example, instruction in zip(treeExamples, treeInstructions)]


classInstructionBase ="Describe different people suffering from this. Mix in broad and specific. Include demographic inforamtion, genral affects of this, how long its been going on, where it stems from, how its affected their social/economic life, etc. Mix in a few specific examples for each person. Each person should be an entry in the list (describe them in some detail in 'overview'. Then give 3 different specific instances of this impacting their life in 'specifics')\n\n"
#DO NOT MODIFY THE BELOW LINE - if you do, you should also modify the leaf verifier function in taxonomy/creator.py
classInstruction =classInstructionBase + "\nReponse should be a json list where each instance is of the form {'oveview': aforementioned overview, 'specifics': [list of specific instances in their life]}"

#these are what will be used by the driver
treePrompts = list(zip(text, treeNumber))

leafInstructions = (classInstruction, numClass)