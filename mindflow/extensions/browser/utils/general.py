from markdownify import markdownify as md
from bs4 import BeautifulSoup
import numpy as np
import random
import string
import re

# might publish as a new module
def filter_markdown(markdown):
    filtered_lines = []
    consecutive_new_lines = 0
    rendered  = re.compile(r'.*\]\(http.*\)')
    embed_line = re.compile(r'.*\]\(.*\)')

    for line in markdown.split('\n'):
        line: str = line.strip()
        
        if embed_line.match(line) and not rendered.match(line):
            continue
        
        if '[' in line and ']' not in line:
            line = line.replace('[', '')
        elif ']' in line and '[' not in line:
            line = line.replace(']', '')
        
        if len(line) > 2:
            filtered_lines.append(line)
            consecutive_new_lines = 0
        elif line == '' and consecutive_new_lines < 1:
            filtered_lines.append('')
            consecutive_new_lines += 1
    
    return '\n'.join(filtered_lines)

def to_markdown(html, ignore=[], ignore_ids=[], ignore_classes=[], strip=[]): 
    #html = html.encode('utf-8', 'replace').decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove elements based on tags
    for tag in ignore:
        for element in soup.find_all(tag):
            element.decompose()
    
    # Remove elements based on IDs
    for id_ in ignore_ids:
        for element in soup.find_all(id=id_):
            element.decompose()
    
    # Remove elements based on classes
    for class_ in ignore_classes:
        for element in soup.find_all(class_=class_):
            element.decompose()
    
    markdown = filter_markdown(md(str(soup), strip=strip))
    return markdown

def get_relevant(document: dict, threshold: int = 1.125, clean=False):
    # temp, filter by distance
    # future, density based retrieval relavance 
    # https://github.com/chroma-core/chroma/blob/main/chromadb/experimental/density_relevance.ipynb

    mask = np.array(document['distances']) <= threshold
    keys = tuple(set(document) & set(('distances', 'documents', 'metadatas', 'ids')))
    for key in keys:
        document[key] = np.array(document[key])[mask].tolist()
        
    if document.get('ids'):
        _, unique_indices = np.unique(document['ids'], return_index=True)
        for key in ('distances', 'documents', 'metadatas', 'ids'):
            document[key] = np.array(document[key])[unique_indices].tolist()
            
    if clean:
        document = "\n\n".join(np.array(document["documents"]).flatten().tolist())
    return document

def uid(length=6):
    characters = string.ascii_letters + string.digits + '-'
    return ''.join(random.choice(characters) for _ in range(length))
