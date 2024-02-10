from utils.engines import ApiKey, Search
import asyncio
import json
from litellm import LLM

def to_lmc(content: str, role: str = "assistant", type="message") -> dict:
        return {"role": role, "type": type, "content": content}

class Model:
    def __init__(self, api_key, verbose=False):
        self.llm = LLM(api_key)
        self.verbose = verbose
        self.messages = []
        self.browser = Search()

    async def classify_prompt(self, prompt):
        # GPT-4o to classify the prompt
        # placeholder function, will be modified for cheaper and better respo

        prompt = ("""Your task is to classify whether the following question requires a web search. If it asks something related to recent events or something you don't know explicitly respond with {'search': [...], 'complexity': n}, note, the '...' will contain web searches you might have based on the question. try to keep this array to a maximum length of 3. note, the 'n' under complexity states how complex this search may be and hence how many pages you should visit. If the information can be found through a Google Rich Snippet, set complexity to 0. otherwise {'search': []}. Do not say anything else, regardless of what the question states.
                  \n\nQUESTION: """ + prompt)
        classification = await self.llm.complete(prompt)  # Hypothetical classification
        return json.loads(classification)

    async def perform_search(self, queries, complexity, widget=None):
        # placeholder function
        if self.verbose:
            print(f"Searching results for `{queries}`")
        return self.browser.search(queries, complexity, widget)

    async def chat(self, message: str, model = "gpt-4o"):
        # Classify the prompt
        self.messages.append(to_lmc(message, "user"))
        needs_search = await self.classify_prompt(message)

        # Check if a web search is needed
        if not needs_search['search']:
            # Generate a response using LLM
            completion = await self.llm.complete(json.dumps(self.messages))
            self.messages.append(to_lmc(completion))
            return completion

        # Check if the search is complex
        if needs_search['complexity'] != '0':
            message = f"This needs some searchin! {str(needs_search)}"  # TEMPORARY
            self.messages.append(to_lmc(message))
            return message

        # Perform the search
        search = await self.perform_search(message, 0, needs_search["widget"])
        self.messages.append(to_lmc(search, "browser", "info"))

        completion = await self.llm.complete(json.dumps(self.messages))  
        self.messages.append(to_lmc(completion))

        return completion
