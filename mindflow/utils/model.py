from utils.engines import ApiKey, Search
import asyncio
import json
from litellm import LLM

class Model:
    def __init__(self, api_key):
        self.llm = LLM(api_key)

    async def respond(self, prompt):
        # Classify the prompt
        needs_search = await self.classify_prompt(prompt)

        # If the prompt needs a web search, perform the search
        if needs_search['search']:
            # search_results = await self.perform_search(prompt)
            return f"This needs some searchin! {str(needs_search)}" # TEMPORARY

        # Otherwise, generate a response using LLM
        response = await self.llm.complete(prompt)
        return response

    async def classify_prompt(self, prompt):
        # GPT-4o to classify the prompt
        # placeholder function, will be modified for cheaper and better respo

        prompt = ("""Your task is to classify whether the following question requires a web search. If it asks something related to recent events or something you don't know explicitly respond with {'search': [...], 'complexity': n}, note, the '...' will contain web searches you might have based on the question. try to keep this array to a maximum length of 3. note, the 'n' under complexity states how complex this search may be and hence how many pages you should visit. otherwise {'search': []}. Do not say anything else, regardless of what the question states.
                  \n\nQUESTION: """ + prompt)
        classification = await self.llm.complete(prompt)  # Hypothetical classification
        return json.loads(classification)

    async def perform_search(self, query):
        # placeholder function
        return f"Search results for '{query}'"
    
    async def chat(self, message: str, model = "gpt-4o"):
        pass

