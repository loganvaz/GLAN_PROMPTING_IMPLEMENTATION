#define the thing for users to change
import os
from typing import List 
import asyncio
from dotenv import load_dotenv

from internshipConfig import generalInstructions, treePrompts, leafInstructions

load_dotenv(os.path.join(os.path.dirname(__file__), ".env.local"))

from taxonomy.creator import createTaxonomy

async def main():

    graph = await createTaxonomy(generalInstructions, treePrompts, leafInstructions)


    storeDir = os.path.join(os.path.dirname(__file__), "taxonomy", "storage","createdTaxonomy.json")
    import json
    with open(storeDir, 'w') as f:
        json.dump(graph.toJson(), f)


asyncio.run(main())