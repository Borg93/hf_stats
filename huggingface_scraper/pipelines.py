import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import logging
import seaborn as sns


logging.getLogger("matplotlib").setLevel(logging.WARNING)
sns.set(style="whitegrid")


class HuggingfaceScraperPipeline:
    def open_spider(self, spider):
        self.conn = sqlite3.connect("huggingface_scraper.db")
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.generate_plot("models_data", "Model Data Over Time", "model_data_plot.png")
        self.generate_plot(
            "datasets_data", "Dataset Data Over Time", "dataset_data_plot.png"
        )

        self.conn.close()

    def process_item(self, item, spider):
        table = "models_data" if item.get("type") == "model" else "datasets_data"

        self.cursor.execute(
            f"INSERT INTO {table} (repo, counter, timestamp) VALUES (?, ?, ?)",
            (item["repo"], item["counter"], datetime.now()),
        )
        self.conn.commit()
        return item

    def generate_plot(self, table_name, title, file_name):
        conn = sqlite3.connect("huggingface_scraper.db")
        query = f"SELECT repo, counter, timestamp FROM {table_name}"
        df = pd.read_sql_query(query, conn)
        conn.close()

        df["counter"] = pd.to_numeric(df["counter"], errors="coerce")
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        output_dir = Path("plots")
        output_dir.mkdir(exist_ok=True)

        plt.figure(figsize=(12, 7))

        palette = sns.color_palette("Set2", n_colors=df["repo"].nunique())

        for (repo, data), color in zip(df.groupby("repo"), palette):
            plt.plot(
                data["timestamp"],
                data["counter"],
                marker="o",
                linestyle="-",
                color=color,
                label=repo,
                alpha=0.8,
                markersize=6,
            )

        plt.xlabel("Timestamp", fontsize=12, labelpad=10)
        plt.ylabel("Counter", fontsize=12, labelpad=10)
        plt.title(title, fontsize=16, weight='bold', pad=20)
        plt.xticks(rotation=45, ha="right")
        plt.grid(visible=True, color='gray', linestyle='--', linewidth=0.5, alpha=0.7)

        plt.legend(
            title="Repository",
            loc="upper left",
            bbox_to_anchor=(1, 1),
            frameon=True,
            fontsize=10,
            title_fontsize="13",
        )
        plt.tight_layout()

        plot_path = output_dir / file_name
        plt.savefig(plot_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"Plot saved to {plot_path}")