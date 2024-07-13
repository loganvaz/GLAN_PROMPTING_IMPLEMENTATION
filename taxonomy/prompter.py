
import traceback
from joblib import Memory
# from openai import AsyncOpenAI
import openai
import os
import time


_dirname = os.path.dirname(__file__)

# openai.api_key = os.getenv("OPENAI_API_KEY")

memory = Memory(os.path.join(_dirname, "etc", "gpt_prompt_cache_dir"))
client = openai.AsyncOpenAI()

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
      except Exception as E:
         print("Exception is ", E)
         traceback.print_exc()
         print("recurse")
         if (cnt > 0):
            return await prompt(sysPrompt, text, model, verifier, cnt-1)
         raise Exception("BAD FORMAT TOO MANY TIMES")
      return toRet
   except Exception as E:
       print("bad gpt req of ", E)
       time.sleep(3 * (5-cnt))
       if (cnt > 0): 
          return await prompt(sysPrompt, text, model, verifier, cnt-1)
       print("bad text is ", text)
       print(E)
       traceback.print_exc()
       raise Exception("GPT ERROR")