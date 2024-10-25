from ..core import MindFlow
from rich import print
import asyncio
import os

os.environ["API_KEY"] = "e8e85d70-74cd-43f7-bd5e-fd8dec181037"
macro = MindFlow()

def browser():
    query = input("search: ")
    summary = macro.extensions.browser.search(query, n=1)
    print(summary)
    
    # input("Press enter to continue...")
    # results = get_relevant(macro.collection.query(query_texts=[query], n_results=3))
    # for document in results['documents'][0]:
    #     print(Markdown(document))
    #     print("\n<END SECTION>\n")
    
def perplexity():
    query = input("search: ")
    summary = macro.extensions.browser.perplexity_search(query)
    print(summary)
    
    # input("Press enter to continue...")
    # results = get_relevant(macro.collection.query(query_texts=[query], n_results=3))
    # for document in results['documents'][0]:
    #     print(Markdown(document))
    #     print("\n<END SECTION>\n")
    
perplexity()
#browser()
