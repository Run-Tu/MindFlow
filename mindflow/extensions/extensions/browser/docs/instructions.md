results = extensions.browser.search(query, n=3) # Returns dictionary of top 3 results from Google Search. Dictionary has fields {"title", "description", "link"}.
contents = extensions.browser.load_searches(results) # Returns dictionary of page contents of previous search. NOTE, this uses a lot of context window, only use this when essential.
showtimes = extensions.browser.search("Inside Out 2 showtimes", 0, "showtimes") # Returns dictionary of Google Snippet for showtimes of query. Can be used with other Google Snippet options including ['showtimes', 'weather', 'events', 'reviews']
