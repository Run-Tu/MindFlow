from .. import macro
from ..extensions.browser.utils.general import get_relevant

from rich import print

def browser():
    query = input("search: ")
    summary = macro.extensions.browser.search(query, n=1)
    print(summary)
    
    # input("Press enter to continue...")
    # results = get_relevant(macro.collection.query(query_texts=[query], n_results=3))
    # for document in results['documents'][0]:
    #     print(Markdown(document))
    #     print("\n<END SECTION>\n")
    
browser()
