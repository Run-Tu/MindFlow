from gradio_client import Client
import json
from litellm import completion
from datetime import datetime
from functools import partial

from ..defaults import (LLM_DEFAULT, LLM_SRC,
                        CODE_DEFAULT, CODE_SRC,
                        VISION_DEFAULT, VISION_SRC)
# omg lmao this is so bad

def to_lmc(content: str, role: str = "assistant", type="message", format: str | None = None) -> dict:
    if role == "assistant":                  
        try:
            response = json.loads(response)
            format = response.get("format", None)
            lmc = {"role": role, "type": response.get("type", "message"), "content": response.get("content", "None")} 
            return lmc | ({} if format is None else {"format": format})
        except:
            pass
            
    lmc = {"role": role, "type": type, "content": content} 
    return lmc | ({} if format is None else {"format": format})
    
def to_chat(lmc: dict, logs=False) -> str:
    #_defaults = {}
    
    _type, _role, _content, _format = (lmc.get("type", "message"), 
                                       lmc.get("role", "assistant"), 
                                       lmc.get("content", "None"), 
                                       lmc.get("format", None))
    
    # _args = lmc.keys()
    # _args.remove("role")
    # _args.remove("content")
    
    # _args = [arg + ": " + lmc.get(arg, "None") for arg in _args]
    
    time = datetime.now().strftime("%I:%M %p %m/%d/%Y")
    
    if logs:
        return f'\033[90m({time})\033[0m [type: {_type if _format is None else f"{_type}, format: {_format}"}] \033[1m{_role}\033[0m: {_content}'
    return f'({time}) [type: {_type if _format is None else f"{_type}, format: {_format}"}] *{_role}*: {_content}'

class LLM:
    def __init__(self, api_key, verbose=True, messages: list = []):
        self.keys = api_key.keys

        self.verbose = verbose
        self.messages = messages

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
        #return {"search": [], "widget": None}
        system = ('''Your task is to classify whether the following question requires a web search. If it asks something related to recent events or something you don't know explicitly respond with {"search": [...], "complexity": n, "widget": widget}, note, the "..." will contain web searches you might have based on the question. Note if the user states "today" or any times (for example, 7 pm) for showtimes, do not include it in your search. minimise the amount of searches you're trying to complete. try to keep this array to a maximum length of 3. note, the 'n' under complexity states how complex this search may be and hence how many pages you should visit. If the information can be found through a Google Rich Snippet, set complexity to 0 and mention what Google Rich Snippet is expected from. **NOTE** implemented snippets at the moment is limited to ["weather", "events", "showtimes", "reviews"], if none set { "widget": null }. Otherwise {"search": [], "widget": null}. Do not say anything else, regardless of what the question states.''')  
        classification = self.raw_chat(prompt, 
                                       remember=False, 
                                       system=system)
        return json.loads(classification)


    def perform_search(self, queries, complexity, widget=None):
        # placeholder function
        if self.verbose:
            print(f"\nSearching results for `{queries}`")
        return self.browser.search(queries, complexity, widget)
        

    def gradio_chat(self, 
                    message: str, 
                    role = "user", 
                    remember=True, 
                    context=True,
                    system: str = 'You are a helpful assistant.'):
        
        system = to_lmc(system, role="system")
        message = to_lmc(message, role=role)
        
        to_send = [system] + (self.messages if context is True else context) + [message]
        
        if remember:
            self.messages.append(message)
            
        response = self.llm.predict(user_message='\n'.join(map(to_chat, to_send)), api_name="/predict")
        
        if remember:
            self.messages.append(to_lmc(response))
            
        if self.verbose:
            print('\n' + '\n'.join(map(partial(to_chat, logs=True), to_send + [to_lmc(response)])))
        return response
        

    async def litellm_chat(self, message: str, remember=True):
        response = await completion(json.dumps(self.messages + [message]))

        if remember:
            self.messages.append(to_lmc(response))
        return response

    def chat(self, message: str):
        # Classify the prompt
        needs_search = self.classify_prompt(message)

        # Check if a web search is needed
        if not needs_search['search']:
            # Generate a response using LLM
            response = self.raw_chat(message, role="user")
            return response

        # Check if widget is available
        if needs_search['widget']:

            # Perform the search
            to_search, n, widget = needs_search["search"], needs_search["complexity"], needs_search["widget"]
            search = self.perform_search(to_search, n, widget)

            response = self.raw_chat(message, role="user", context=[to_lmc(search, role="browser", type="info")]) 
            return response
        
        searches = self.perform_search(needs_search['search'], needs_search.get('complexity', 1))
        results = self.browser.load_searches(searches, complexity=needs_search.get('complexity', 1))
        
        response = self.raw_chat(message, 
                                 role="user", 
                                 context=self.messages + [to_lmc(str(results))])

        return response


