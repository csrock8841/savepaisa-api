from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

app = Flask(__name__)
ua = UserAgent()

def get_html(url):
    headers = {"User-Agent": ua.random}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r.text
    except:
        return None

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
    price = product.select_one(".a-price-whole")
    image = product.select_one("img.s-image")

    return {
        "title": title.text.strip() if title else None,
        "price": price.text.replace(",", "") if price else None,
        "image": image["src"] if image else None
    }

def scrape_flipkart(query):
    url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
    html = get_html(url)
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")

    product = soup.select_one("div._1AtVbE")
    if not product:
        return None

    title = product.select_one("div.KzDlHZ")
    price = product.select_one("div._30jeq3")
    image = product.select_one("img")

    return {
        "title": title.text.strip() if title else None,
        "price": price.text.replace("₹", "").replace(",", "") if price else None,
        "image": image["src"] if image else None
    }

def scrape_meesho(query):
    url = f"https://www.meesho.com/search?q={query.replace(' ', '+')}"
    html = get_html(url)
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")

    product = soup.select_one("div.sc-dkrFOg")
    if not product:
        return None

    title = product.select_one("p.sc-eDvSVe")
    price = product.select_one("h5.sc-eqUAAy")
    image = product.select_one("img")

    return {
        "title": title.text.strip() if title else None,
        "price": price.text.replace("₹", "").replace(",", "") if price else None,
        "image": image["src"] if image else None
    }

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
    return "SavePaisa API is running successfully!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
