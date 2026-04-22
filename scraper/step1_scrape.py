import pandas as pd
from bs4 import BeautifulSoup
from scraper.utils import get_html

STATE_URLS = {
    "NSW": "https://www.realestate.com.au/buy/in-nsw/list-{}",
    "WA": "https://www.realestate.com.au/buy/in-wa/list-{}",
    "ACT": "https://www.realestate.com.au/buy/in-act/list-{}",
    "VIC": "https://www.realestate.com.au/buy/in-vic/list-{}",
    "SA": "https://www.realestate.com.au/buy/in-sa/list-{}",
    "NT": "https://www.realestate.com.au/buy/in-nt/list-{}",
    "QLD": "https://www.realestate.com.au/buy/in-qld/list-{}",
    "TAS": "https://www.realestate.com.au/buy/in-tas/list-{}"
}

def extract_property_links(html):
    soup = BeautifulSoup(html, "lxml")
    links = []
    
    for a in soup.select('a[href*="/property-"]'):
        href = a.get("href")
        if href and "realestate.com.au/property" in href:
            links.append(href)
    
    return list(set(links))


def extract_property_data(url):
    response = get_html(url)
    if not response or response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "lxml")

    data = {
        "Address": None,
        "Suburb": None,
        "Postcode": None,
        "State": None,
        "Hyperlink": url,
        "Property ID": None,
        "Date Published": None
    }

    # Extract JSON-LD structured data
    for script in soup.find_all("script", type="application/ld+json"):
        if "address" in script.text:
            text = script.text
            
            import json
            try:
                j = json.loads(text)
                
                if isinstance(j, dict) and "address" in j:
                    addr = j["address"]
                    data["Address"] = addr.get("streetAddress")
                    data["Suburb"] = addr.get("addressLocality")
                    data["Postcode"] = addr.get("postalCode")
                    data["State"] = addr.get("addressRegion")
                    
            except:
                pass

    # Property ID from URL
    if "property-" in url:
        data["Property ID"] = url.split("-")[-1]

    return data


def run(selected_states):
    all_rows = []

    for state in selected_states:
        print(f"Scraping {state}")
        page = 1

        while True:
            url = STATE_URLS[state].format(page)
            res = get_html(url)

            if not res or res.status_code != 200:
                break

            links = extract_property_links(res.text)

            if not links:
                break

            for link in links:
                data = extract_property_data(link)
                if data:
                    all_rows.append(data)

            page += 1

    df = pd.DataFrame(all_rows)
    df.to_csv("properties.csv", index=False)
    print("Saved properties.csv")


if __name__ == "__main__":
    import sys
    states = sys.argv[1].split(",")
    run(states)
