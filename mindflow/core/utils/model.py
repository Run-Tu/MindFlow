from ..utils.engines import Profile, Search
from gradio_client import Client
import json
import asyncio
from litellm import completion

from ..defaults import (LLM_DEFAULT, LLM_SRC,
                        CODE_DEFAULT, CODE_SRC,
                        VISION_DEFAULT, VISION_SRC)
# omg lmao this is so bad

def to_lmc(content: str, role: str = "assistant", type="message") -> dict:
        return {"role": role, "type": type, "content": content}

class Model:
    def __init__(self, api_key = Profile(), verbose=True, messages: list = []):
        self.keys = api_key.keys

        self.verbose = verbose
        self.messages = messages
        self.browser = Search()

        is_llm_default = self.keys.get("llm", LLM_DEFAULT) == LLM_DEFAULT
        is_code_default = self.keys.get("code", CODE_DEFAULT) == CODE_DEFAULT
        is_vision_default = self.keys.get("vision", VISION_DEFAULT) == VISION_DEFAULT

        self.raw_chat = self.litellm_chat
        if is_llm_default: 
            self.llm = Client(LLM_SRC)
            self.raw_chat = self.gradio_chat

        if is_code_default: pass
        if is_vision_default: pass

    def classify_prompt(self, prompt):
        prompt = ('''Your task is to classify whether the following question requires a web search. If it asks something related to recent events or something you don't know explicitly respond with {"search": [...], "complexity": n, "widget": widget}, note, the "..." will contain web searches you might have based on the question. Note if the user states "today" or any times (for example, 7 pm) for showtimes, do not include it in your search. try to keep this array to a maximum length of 3. note, the 'n' under complexity states how complex this search may be and hence how many pages you should visit. If the information can be found through a Google Rich Snippet, set complexity to 0 and mention what Google Rich Snippet is expected from options ["weather", "events", "showtimes", "reviews"], if none set { "widget": null }. Otherwise {"search": [], "widget": null}. Do not say anything else, regardless of what the question states.
                \n\nQUESTION: ''' + prompt)
        classification = json.loads(self.raw_chat(prompt, remember=False))
        if self.verbose:
            print('Determiend conversation complexity:', classification)

        return classification


    def perform_search(self, queries, complexity, widget=None):
        # placeholder function
        if self.verbose:
            print(f"Searching results for `{queries}`")
        return self.browser.search(queries, complexity, widget)
        

    def gradio_chat(self, message: str, remember=True, system: str = 'You are a helpful assistant.'):
        #print([str(m) for m in self.messages])
        chat = self.llm.predict(query=message,
                                            history=[],
                                            system=system,
                                            api_name="/model_chat")
        #print("\n"*5 + str(chat) + "\n"*5)
        response = chat[1][0][-1]
        if remember:
            self.messages.append(to_lmc(response))
        return response

    async def litellm_chat(self, message: str, remember=True):
        response = await completion(json.dumps(self.messages + [message]))

        if remember:
            self.messages.append(to_lmc(response))
        return response

    def chat(self, message: str):
        # Classify the prompt
        self.messages.append(to_lmc(message, "user"))
        needs_search = self.classify_prompt(message)

        # Check if a web search is needed
        if not needs_search['search']:
            # Generate a response using LLM
            response = self.raw_chat(json.dumps(self.messages))
            return response

        # Check if widget is available
        if needs_search['widget']:

            # Perform the search
            to_search, n, widget = needs_search["search"], needs_search["complexity"], needs_search["widget"]
            search = self.perform_search(to_search, n, widget)
            self.messages.append(to_lmc(search, "browser", "info"))

            response = self.raw_chat(json.dumps(self.messages)) 
            return response

        response = f"This needs a slightly more complex search algorithm which is in progress! {str(needs_search)}"  # TEMPORARY
        self.messages.append(to_lmc(response))
        return response

