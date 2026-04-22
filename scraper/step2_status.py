import pandas as pd
from scraper.utils import get_html
from datetime import datetime

def run(input_file):
    df = pd.read_csv(input_file)

    statuses = []
    today = datetime.today().strftime("%Y-%m-%d")

    for url in df["Hyperlink"]:
        res = get_html(url)
        if res:
            statuses.append(res.status_code)
        else:
            statuses.append("ERROR")

    df[f"Status_{today}"] = statuses
    df.to_csv("properties_updated.csv", index=False)

    print("Saved properties_updated.csv")


if __name__ == "__main__":
    import sys
    run(sys.argv[1])
