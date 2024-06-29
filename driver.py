#define the thing for users to change
import os
from typing import List 
import asyncio
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env.local"))

from taxonomy.creator import createTaxonomy

async def main():
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

    treeNumber: List[int|None] = [
        3,
        3,
        3
    ]

    assert(len(treeNumber) == len(treeExamples))
    assert(len(treeInstructions) == len(treeExamples))

    text = [instruction + "\nHere is an example:" + example for example, instruction in zip(treeExamples, treeInstructions)]
    treePrompts = list(zip(text, treeNumber))

    generalInstructions = "You are a mental heatlh professional tasked with breaking things down into broad yet distinct categories and specifying them with more time. Generate a list, but remember you are restricted to the number of examples requested. Unless told otherwise, give only the name - not a description. Include in parenthesis only the topic stem provided. IE if provided with magical and generating unicorns I would have my entry be unicorns (magical)"
    # treePrompts = [
    #     ("Generate a list of mental health disorders/things that contribute to bad mental health. This can be life circumstances (e.g. loss of loved one), mental (e.g. body dismorphia), or some combination. Try to keep each of these discrete from each other but overlap them as necessary", 3), 
    #     ("Break this down into more specifics (ex: PTSD-sexual-assult, OCD-washing-hands, etc.). These should still be broad categories but more specific now. ", 3), 
    #     ("Break this down into different levels (normal stress response PTSD from sexual assult, acute stress disorder PTSD from war, etc.)", 3)
    # ]


    classInstruction ="Describe different people suffering from this. Mix in broad and specific. Include demographic inforamtion, genral affects of this, how long its been going on, where it stems from, how its affected their social/economic life, etc. Mix in a few specific examples for each person. Reponse should be a json list where each instance is of the form {'oveview': aforementioned overview, 'specifics': [list of specific instances in their life]}"
    numClass = 5

    graph = await createTaxonomy(generalInstructions, treePrompts, (classInstruction, numClass))


    storeDir = os.path.join(os.path.dirname(__file__), "taxonomy", "storage","createdTaxonomy.json")
    import json
    with open(storeDir, 'w') as f:
        json.dump(graph, f)


asyncio.run(main())