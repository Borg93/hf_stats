import scrapy
import yaml
import sqlite3
from datetime import datetime


class HuggingFaceSpider(scrapy.Spider):
    name = "huggingface"

    def start_requests(self):
        self.scrape_timestamp = datetime.now()

        with open("hf.yaml", "r") as f:
            data = yaml.safe_load(f)

        base_url = "https://huggingface.co/"

        for repo in data.get("models", []):
            full_url = f"{base_url}{repo}"
            yield scrapy.Request(
                url=full_url, callback=self.parse, meta={"repo": repo, "type": "model"}
            )

        for repo in data.get("datasets", []):
            full_url = f"{base_url}datasets/{repo}"
            yield scrapy.Request(
                url=full_url,
                callback=self.parse,
                meta={"repo": repo, "type": "dataset"},
            )

    def parse(self, response):
        repo = response.meta["repo"]
        data_type = response.meta["type"]

        if data_type == "dataset":
            item_count = response.css(
                "body > div > main > div.container.relative.flex.flex-col.md\\:grid.md\\:space-y-0.w-full.md\\:grid-cols-12.md\\:flex-1.md\\:grid-rows-full.space-y-4.md\\:gap-6 > section.pt-6.border-gray-100.md\\:pb-24.md\\:pl-6.md\\:w-64.lg\\:w-80.xl\\:w-96.flex-none.order-first.md\\:order-none.md\\:border-l.\\!pt-3.md\\:\\!pt-6 > dl > dd::text"
            ).get()
            self.save_to_db(repo, item_count, "datasets_data")
        else:
            item_count = response.css(
                "body > div > main > div.container.relative.flex.flex-col.md\\:grid.md\\:space-y-0.w-full.md\\:grid-cols-12.md\\:flex-1.md\\:grid-rows-full.space-y-4.md\\:gap-6 > section.pt-8.border-gray-100.md\\:col-span-5.pt-6.md\\:pb-24.md\\:pl-6.md\\:border-l.order-first.md\\:order-none > div.flex.justify-between.pb-2 > dl > dd::text"
            ).get()
            self.save_to_db(repo, item_count, "models_data")

    def save_to_db(self, repo, counter, table):
        conn = sqlite3.connect(self.settings.get("DATABASE"))
        c = conn.cursor()

        try:
            counter_int = int(counter.replace(",", ""))
        except (ValueError, TypeError):
            counter_int = None

        c.execute(
            f"INSERT INTO {table} (repo, counter, timestamp) VALUES (?, ?, ?)",
            (repo, counter_int, self.scrape_timestamp),
        )
        conn.commit()
        conn.close()
