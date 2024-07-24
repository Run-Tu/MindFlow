async def get_events(page):
    classnames = {
        "title": "div.YOGjf",
        "location": "div.zvDXNd",
        "time": "div.SHrHx > div.cEZxRc:not(.zvDXNd)"
    }

    button = "div.MmMIvd"
    expanded = "div#Q5Vznb"
    popup = "g-raised-button.Hg3NO"
    #await page.wait_for_selector(popup)
    #buttons = await page.query_selector_all(popup)
    #await buttons[1].click()

    await page.click(button)
    await page.wait_for_selector(expanded)

    keys = {key: None for key in classnames}
    events = []
    for key, selector in classnames.items():
        elements = await page.query_selector_all(selector)
        if events == []:
            events = [dict(keys) for _ in range(len(elements))]

        for index, elem in enumerate(elements):
            if key == "location" :
                if index % 2: # odd
                    n = await elem.inner_text()
                    events[index // 2][key] = temp + ', ' + n
                else:
                    temp = await elem.inner_text()
            else:
                events[index][key] = await elem.inner_text()

    return events

async def get_showtimes(page):
    classnames = {
        "venue": "div.YS9glc > div:not([class])",
        "location": "div.O4B9Zb"
    }

    container = "div.Evln0c"
    subcontainer = "div.iAkOed"
    plans = "div.swoqy"
    times_selector = "div.std-ts"

    keys = {key: None for key in classnames}
    events = []
    for key, selector in classnames.items():
        elements = await page.query_selector_all(selector)
        if events == []:
            events = [dict(keys) for _ in range(len(elements))]

        for index, elem in enumerate(elements):
            if key == 'location':
                location = await elem.inner_text()
                events[index][key] = location.replace("·", " away, at ")
            else:
                events[index][key] = await elem.inner_text()

    elements = await page.query_selector_all(container)
    for index, element in enumerate(elements):
        sub = await element.query_selector_all(subcontainer)
        for plan in sub:
            mode = await plan.query_selector(plans)
            
            if mode: mode_text = await mode.inner_text()
            else: mode_text = 'times'
            
            times = await plan.query_selector_all(times_selector)
            events[index][mode_text] = [await time.inner_text() for time in times]

    return events


async def get_reviews(page):
    classnames = {
        "site": "span.rhsB",
        "rating": "span.gsrt"
    }

    rating_class = "div.xt8Uw"

    keys = {key: None for key in classnames}
    events = []
    for key, selector in classnames.items():
        elements = await page.query_selector_all(selector)
        if not events:
            events = [dict(keys) for _ in range(len(elements))]

        for index, elem in enumerate(elements):
            events[index][key] = await elem.inner_text()

    rating = await page.query_selector(rating_class)
    events.append({"site": "Google Reviews", "rating": await rating.inner_text() + "/5.0"})

    return events

async def get_weather(page):
    classnames = {
        "condition": "span#wob_dc",
        "time": "div#wob_dts",
        "temperature": "span#wob_tm",
        "unit": "div.wob-unit > span[style='display:inline']",
        "precipitation": "span#wob_pp",
        "humidity": "span#wob_hm",
        "wind": "span#wob_ws"
    }

    info = {key: None for key in classnames}
    for key, selector in classnames.items():
        element = await page.query_selector(selector)
        info[key] = await element.inner_text()

    return info
