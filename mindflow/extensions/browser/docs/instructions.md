# BROWSER APP
browser = Browser()
results = browser.search(query, n=1) # Returns array of summaries based on results
showtimes = browser.widget_search("weather today", widget="weather") # Returns dictionary of Google Snippet for showtimes of query. Can be used with other Google Snippet options including ['showtimes', 'weather', 'events', 'reviews']
print(results) # Print out returned values
