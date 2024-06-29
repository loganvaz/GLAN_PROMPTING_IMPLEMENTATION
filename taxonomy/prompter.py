
from joblib import Memory
from openai import AsyncOpenAI
import os
import traceback
import asyncio
import time


_dirname = os.path.dirname(__file__)

memory = Memory(os.path.join(_dirname, "etc", "gpt_prompt_cache_dir"))
client = AsyncOpenAI()

@memory.cache(ignore=["verifier", "cnt"])
async def prompt(sysPrompt: str, text:str, model:str="gpt-3.5-turbo", verifier=lambda x :x, cnt = 5)->str:
   try:
      completion = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": sysPrompt},
            {"role": "user", "content": text}
        ]
      )
      toRet = completion.choices[0].message.content
      try:
         verifier(toRet)
      except:
         print("recurse")
         return await prompt(sysPrompt, text, model, verifier)
      return toRet
   except Exception as E:
      #  print(E)
      #  traceback.print_exc()
       time.sleep(3 * (5-cnt))
       if (cnt != 0): 
          return await prompt(sysPrompt, text, model, verifier, cnt-1)
       print("bad text is ", text)
       raise Exception("GPT ERROR")