import os
import json
import pandas as pd
from playwright.sync_api import sync_playwright

STATE_URLS = {
    "NSW": "https://www.realestate.com.au/buy/in-nsw/list-{}",
    "QLD": "https://www.realestate.com.au/buy/in-qld/list-{}",
}

os.makedirs("debug", exist_ok=True)


def run(states, max_properties):
    all_rows = []
    collected = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for state in states:
            page_num = 1

            while collected < max_properties:
                url = STATE_URLS[state].format(page_num)
                print(f"Loading {url}")

                page.goto(url, timeout=60000)

                # wait for listings to render
                page.wait_for_timeout(5000)

                # save debug HTML + screenshot
                html = page.content()
                with open(f"debug/list_{state}_{page_num}.html", "w", encoding="utf-8") as f:
                    f.write(html)

                page.screenshot(path=f"debug/list_{state}_{page_num}.png")

                # extract links
                links = page.eval_on_selector_all(
                    "a[href*='/property-']",
                    "els => els.map(e => e.href)"
                )

                links = list(set(links))
                print(f"Found {len(links)} links")

                # save debug links
                pd.DataFrame({"links": links}).to_csv(
                    f"debug/links_{state}_{page_num}.csv", index=False
                )

                if not links:
                    break

                for link in links:
                    if collected >= max_properties:
                        break

                    try:
                        page.goto(link, timeout=60000)
                        page.wait_for_timeout(3000)

                        # screenshot property page
                        safe_id = link.split("-")[-1]
                        page.screenshot(path=f"debug/property_{safe_id}.png")

                        html = page.content()
                        with open(f"debug/property_{safe_id}.html", "w", encoding="utf-8") as f:
                            f.write(html)

                        data = {
                            "Address": None,
                            "Suburb": None,
                            "Postcode": None,
                            "State": None,
                            "Hyperlink": link,
                            "Property ID": safe_id,
                            "Date Published": None
                        }

                        # extract JSON-LD
                        scripts = page.locator("script[type='application/ld+json']").all_text_contents()

                        for s in scripts:
                            try:
                                j = json.loads(s)
                                if isinstance(j, dict) and "address" in j:
                                    addr = j["address"]
                                    data["Address"] = addr.get("streetAddress")
                                    data["Suburb"] = addr.get("addressLocality")
                                    data["Postcode"] = addr.get("postalCode")
                                    data["State"] = addr.get("addressRegion")
                            except:
                                pass

                        all_rows.append(data)
                        collected += 1
                        print(f"Collected {collected}")

                    except Exception as e:
                        print(f"Error on property: {e}")

                page_num += 1

        browser.close()

    df = pd.DataFrame(all_rows)
    df.to_csv("properties.csv", index=False)
    print("Saved properties.csv")


if __name__ == "__main__":
    import sys
    states = sys.argv[1].split(",")
    max_props = int(sys.argv[2])
    run(states, max_props)
