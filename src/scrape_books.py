"""books.toscrape.com の Travel カテゴリから書籍情報を取得し、Markdownに保存する。"""

import logging
import random
import sys
import time
from datetime import date
from pathlib import Path
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com"
TARGET_URL = "https://books.toscrape.com/catalogue/category/books/travel_2/index.html"
USER_AGENT = "python-automation-scraper/1.0"
OUTPUT_DIR = Path(__file__).resolve().parent.parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def is_allowed_by_robots(url: str) -> bool:
    """robots.txtを確認し、対象URLへのアクセスが許可されているか判定する。"""
    parser = RobotFileParser()
    parser.set_url(urljoin(BASE_URL, "/robots.txt"))
    try:
        parser.read()
    except OSError:
        # robots.txtを取得できない場合はアクセス許可とみなす
        return True
    return parser.can_fetch(USER_AGENT, url)


def fetch_html(url: str) -> str:
    """指定URLのHTMLを取得する。接続エラー時はログを出力して終了する。"""
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error("接続エラーが発生しました: %s", exc)
        sys.exit(1)
    response.encoding = response.apparent_encoding
    return response.text


def parse_books(html: str) -> list[dict[str, str]]:
    """書籍一覧HTMLからタイトル・価格・在庫状況を抽出する。"""
    soup = BeautifulSoup(html, "html.parser")
    books = []
    for article in soup.select("article.product_pod"):
        title = article.h3.a["title"].strip()
        price = article.select_one("p.price_color").get_text(strip=True)
        availability = article.select_one("p.instock.availability").get_text(strip=True)
        books.append({"title": title, "price": price, "availability": availability})
    return books


def write_markdown(books: list[dict[str, str]], output_path: Path) -> None:
    """取得した書籍情報をMarkdown形式で書き出す。"""
    lines = [
        "# Travel カテゴリ 書籍一覧",
        "",
        f"取得日: {date.today():%Y-%m-%d}",
        f"取得元: {TARGET_URL}",
        "",
        "| タイトル | 価格 | 在庫状況 |",
        "|---|---|---|",
    ]
    for book in books:
        lines.append(f"| {book['title']} | {book['price']} | {book['availability']} |")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not is_allowed_by_robots(TARGET_URL):
        logger.error("robots.txtによりアクセスが禁止されています: %s", TARGET_URL)
        sys.exit(1)

    # サーバー負荷軽減のため、リクエスト前にランダムな待機時間を設ける
    time.sleep(random.uniform(1, 3))

    html = fetch_html(TARGET_URL)
    books = parse_books(html)

    output_path = OUTPUT_DIR / f"books_{date.today():%Y%m%d}.md"
    write_markdown(books, output_path)
    logger.info("%d件の書籍情報を %s に保存しました", len(books), output_path.name)


if __name__ == "__main__":
    main()
