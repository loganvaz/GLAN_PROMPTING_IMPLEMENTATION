
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
seedList = []
#node general modifications
treeInstructions = [
    "Generate a list of different broad majors that students in college seek internships for. Keep it broad here.",
    "Break these down into specific majors, adding specificity",
    "Break these down into different skills that would almost resemble a tract within this"
]

treeExamples = [
    ("Engineering\nLiberal Arts\nBusiness", None),
    ("IB (Business)\nMarketting (Business)\nData Analyst (Business)", "Business"),
    ("Data Analyst Focused on Visualization (Data Analyst (Business))\nDouble Finance Data Analyst Major (Data Analyst (Business))\nClient Focused Data Analyst (Data Analyst (Business))", "Data Analyst (Business)")
]

treeNumber: List[int|None] = [10,4,6]

generalInstructions = """You are a part of university career services that is trying to categorize students who want internships. 
Generate a list, but remember you are restricted to the number of examples requested. Unless told otherwise, 
give only the name - not a description. Include in parenthesis only the topic stem provided. IE if provided with magical and generating unicorns 
I would have my entry be unicorns (magical). Your end goal is to create a graph of majors/specializations in a school that seek internships. Make sure all output is based on the input provided""".replace("\n", "")

#leaf general modifications
numClass = 4

#gpt
MODEL = "gpt-3.5-turbo"



#further construciton
assert(len(treeNumber) == len(treeExamples))
assert(len(treeInstructions) == len(treeExamples))

text = [instruction + "\nHere is an example :" + example[0] + ( ("  based on the input: " + example[1]) if example[1] else "") for example, instruction in zip(treeExamples, treeInstructions)]


classInstructionBase = "You will describe a few people at differnt levels of knowledge in this subejct. The list you will return will describe different levels of knowledge. Each entry of the list will have an overview which follows with a string describing the level of competence (very basic, basic, advanced, specialty, etc.). The instances array will describe projects/classes/lnowledge they ahve about this. This can include failing classes or just saying no skills for low level. For higher levels of knowledge, you should include details about projects they used."
classInstruction =classInstructionBase + "\nReponse should be a json list where each instance is of the form {'oveview': aforementioned overview, 'specifics': [list of specific instances in their life]}"
#these are what will be used by the driver
treePrompts = list(zip(text, treeNumber))

leafInstructions = (classInstruction, numClass)