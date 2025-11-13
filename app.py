from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# FREE BROWSER SCRAPER (bypass Amazon, Flipkart, Meesho)
def get_html(url):
    try:
        browser_url = "https://api.scrapingbrowser.com/scrape?url=" + url
        r = requests.get(browser_url, timeout=20)
        return r.text
    except:
        return None

# AMAZON
def scrape_amazon(query):
    url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    html = get_html(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    product = soup.select_one("div[data-component-type='s-search-result']")
    if not product:
        return None

    title = product.select_one("h2 a span")
    price = product.select_one("span.a-price-whole")
    img = product.select_one("img.s-image")

    return {
        "title": title.text.strip() if title else None,
        "price": price.text.replace(",", "") if price else None,
        "image": img["src"] if img else None
    }

# FLIPKART
def scrape_flipkart(query):
    url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
    html = get_html(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    product = soup.select_one("div._2kHMtA")
    if not product:
        product = soup.select_one("div._1AtVbE")

    title = product.select_one("div._4rR01T")
    price = product.select_one("div._30jeq3")
    img = product.select_one("img")

    return {
        "title": title.text.strip() if title else None,
        "price": price.text.replace("₹", "").replace(",", "") if price else None,
        "image": img["src"] if img else None
    }

# MEESHO
def scrape_meesho(query):
    url = f"https://www.meesho.com/search?q={query.replace(' ', '+')}"
    html = get_html(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    product = soup.select_one("div.SearchCard__CardWrap-sc-w3luhv-0")
    if not product:
        product = soup.select_one("div.sc-dkrFOg")

    title = product.select_one("p.SearchCard__Title-sc-w3luhv-7")
    price = product.select_one("h5.SearchCard__Price-sc-w3luhv-6")
    img = product.select_one("img")

    return {
        "title": title.text.strip() if title else None,
        "price": price.text.replace("₹", "").replace(",", "") if price else None,
        "image": img["src"] if img else None
    }

@app.route("/scrape")
def scrape_all():
    query = request.args.get("query", "")
    if not query:
        return jsonify({"error": "missing query"}), 400

    return jsonify({
        "amazon": scrape_amazon(query),
        "flipkart": scrape_flipkart(query),
        "meesho": scrape_meesho(query)
    })

@app.route("/")
def home():
    return "SavePaisa Scraper API is working!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
