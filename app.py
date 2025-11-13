from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

app = Flask(__name__)
ua = UserAgent()

# -------------------------------------------
# Helper function
# -------------------------------------------
def get_html(url):
    headers = {"User-Agent": ua.random}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r.text
    except:
        return None


# -------------------------------------------
# AMAZON SCRAPER (UPDATED & WORKING)
# -------------------------------------------
def scrape_amazon(query):
    url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    html = get_html(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    product = soup.select_one("div[data-component-type='s-search-result']")
    if not product:
        return None

    # Title
    title_tag = product.select_one("h2 a span")
    if not title_tag:
        title_tag = product.select_one("span.a-size-medium")

    # Price
    whole = product.select_one("span.a-price-whole")
    fraction = product.select_one("span.a-price-fraction")

    price = None
    if whole:
        price = whole.text.replace(",", "")
        if fraction:
            price += fraction.text

    # Image
    img_tag = product.select_one("img.s-image")

    return {
        "title": title_tag.text.strip() if title_tag else None,
        "price": price,
        "image": img_tag["src"] if img_tag else None
    }


# -------------------------------------------
# FLIPKART SCRAPER (UPDATED & WORKING)
# -------------------------------------------
def scrape_flipkart(query):
    url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
    html = get_html(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    # New main card
    product = soup.select_one("div._2kHMtA")
    if not product:
        product = soup.select_one("div._1AtVbE")

    if not product:
        return None

    title = product.select_one("div._4rR01T")
    if not title:
        title = product.select_one("a.s1Q9rs")

    price = product.select_one("div._30jeq3")
    image = product.select_one("img")

    return {
        "title": title.text.strip() if title else None,
        "price": price.text.replace("₹", "").replace(",", "") if price else None,
        "image": image["src"] if image else None
    }


# -------------------------------------------
# MEESHO SCRAPER (UPDATED & WORKING)
# -------------------------------------------
def scrape_meesho(query):
    url = f"https://www.meesho.com/search?q={query.replace(' ', '+')}"
    html = get_html(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    product = soup.select_one("div.SearchCard__CardWrap-sc-w3luhv-0")
    if not product:
        product = soup.select_one("div.sc-dkrFOg")

    if not product:
        return None

    title = product.select_one("p.SearchCard__Title-sc-w3luhv-7")
    price = product.select_one("h5.SearchCard__Price-sc-w3luhv-6")
    image = product.select_one("img")

    return {
        "title": title.text.strip() if title else None,
        "price": price.text.replace("₹", "").replace(",", "") if price else None,
        "image": image["src"] if image else None
    }


# -------------------------------------------
# FINAL API ENDPOINT
# -------------------------------------------
@app.route("/scrape")
def scrape_all():
    query = request.args.get("query", "")
    if not query:
        return jsonify({"error": "query missing"}), 400

    return jsonify({
        "amazon": scrape_amazon(query),
        "flipkart": scrape_flipkart(query),
        "meesho": scrape_meesho(query)
    })


@app.route("/")
def home():
    return "SavePaisa Free Scraper API is running successfully!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
