"""quotes.toscrape.com/js（JS描画ページ）から名言・著者情報を取得し、
Markdownとスクリーンショットを保存する。"""

import logging
import random
import sys
import time
from datetime import date
from pathlib import Path
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

BASE_URL = "https://quotes.toscrape.com"
TARGET_URL = "https://quotes.toscrape.com/js"
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


def scrape(screenshot_path: Path) -> list[dict[str, str]]:
    """ブラウザを表示してページを開き、名言・著者を取得しスクリーンショットを保存する。"""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        try:
            page = browser.new_page(user_agent=USER_AGENT)

            # サーバー負荷軽減のため、リクエスト前にランダムな待機時間を設ける
            time.sleep(random.uniform(1, 3))

            page.goto(TARGET_URL, wait_until="networkidle", timeout=15000)
            page.wait_for_selector(".quote")

            quotes = [
                {
                    "text": quote.query_selector(".text").inner_text().strip(),
                    "author": quote.query_selector(".author").inner_text().strip(),
                }
                for quote in page.query_selector_all(".quote")
            ]

            page.screenshot(path=str(screenshot_path), full_page=True)
            return quotes
        finally:
            browser.close()


def write_markdown(quotes: list[dict[str, str]], output_path: Path, screenshot_name: str) -> None:
    """取得した名言・著者をMarkdown形式で書き出す。"""
    lines = [
        "# 名言一覧（quotes.toscrape.com/js）",
        "",
        f"取得日: {date.today():%Y-%m-%d}",
        f"取得元: {TARGET_URL}",
        f"スクリーンショット: {screenshot_name}",
        "",
        "| 名言 | 著者 |",
        "|---|---|",
    ]
    for quote in quotes:
        text = quote["text"].replace("|", "\\|")
        lines.append(f"| {text} | {quote['author']} |")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not is_allowed_by_robots(TARGET_URL):
        logger.error("robots.txtによりアクセスが禁止されています: %s", TARGET_URL)
        sys.exit(1)

    today = date.today()
    md_path = OUTPUT_DIR / f"quotes_{today:%Y%m%d}.md"
    png_path = OUTPUT_DIR / f"quotes_{today:%Y%m%d}.png"

    try:
        quotes = scrape(png_path)
    except PlaywrightError as exc:
        logger.error("接続エラーが発生しました: %s", exc)
        sys.exit(1)

    write_markdown(quotes, md_path, png_path.name)
    logger.info(
        "%d件の名言を %s に保存しました（スクリーンショット: %s）",
        len(quotes),
        md_path.name,
        png_path.name,
    )


if __name__ == "__main__":
    main()
