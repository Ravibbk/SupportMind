"""Exploratory Data Analysis script for SupportMind datasets.

Generates:
1. docs/screenshots/class_balance.png
2. docs/screenshots/urgency_distribution.png
3. docs/screenshots/message_length_distribution.png
4. docs/screenshots/top_words_per_category.png
5. docs/screenshots/orders_status_distribution.png
"""

from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "backend" / "data"
SCREENSHOTS_DIR = BASE_DIR / "docs" / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Set visual styling for modern dark-slate aesthetic
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["figure.dpi"] = 150


def run_eda():
    tickets_path = DATA_DIR / "tickets_train.csv"
    orders_path = DATA_DIR / "orders.csv"

    df_tickets = pd.read_csv(tickets_path)
    df_orders = pd.read_csv(orders_path)

    print("=== Tickets Summary ===")
    print(df_tickets.info())
    print("\nMissing values in tickets:", df_tickets.isnull().sum().to_dict())
    print("Duplicates in tickets:", df_tickets.duplicated(subset=["text"]).sum())

    print("\n=== Orders Summary ===")
    print(df_orders.info())
    print("Orders status breakdown:\n", df_orders["status"].value_counts())

    # 1. Category Class Balance
    fig, ax = plt.subplots(figsize=(8, 4.5))
    counts = df_tickets["category"].value_counts()
    colors = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#6b7280"]
    bars = ax.bar(counts.index, counts.values, color=colors[:len(counts)], width=0.6, edgecolor="#1e293b", linewidth=1.2)
    ax.set_title("Ticket Category Distribution (1,500 Customer Inquiries)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Support Category", fontsize=11)
    ax.set_ylabel("Number of Tickets", fontsize=11)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height}", xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=10, fontweight="bold")
    plt.tight_layout()
    fig.savefig(SCREENSHOTS_DIR / "class_balance.png")
    plt.close(fig)
    print("Saved docs/screenshots/class_balance.png")

    # 2. Urgency Distribution by Category
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ct = pd.crosstab(df_tickets["category"], df_tickets["urgency"], normalize="index") * 100
    urgency_order = ["low", "medium", "high"]
    ct = ct[urgency_order]
    ct.plot(kind="bar", stacked=True, ax=ax, color=["#10b981", "#f59e0b", "#ef4444"], edgecolor="#1e293b")
    ax.set_title("Ticket Urgency Breakdown by Category (%)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Category", fontsize=11)
    ax.set_ylabel("Percentage (%)", fontsize=11)
    ax.legend(title="Urgency Tier", frameon=True)
    plt.xticks(rotation=15)
    plt.tight_layout()
    fig.savefig(SCREENSHOTS_DIR / "urgency_distribution.png")
    plt.close(fig)
    print("Saved docs/screenshots/urgency_distribution.png")

    # 3. Message Length Distribution (Character & Word Count)
    df_tickets["char_len"] = df_tickets["text"].str.len()
    df_tickets["word_len"] = df_tickets["text"].str.split().str.len()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    ax1.hist(df_tickets["char_len"], bins=30, color="#6366f1", edgecolor="#1e293b", alpha=0.85)
    ax1.set_title("Character Length Distribution", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Character Count")
    ax1.set_ylabel("Frequency")
    ax1.axvline(df_tickets["char_len"].mean(), color="#ef4444", linestyle="--", label=f"Mean: {df_tickets['char_len'].mean():.1f}")
    ax1.legend()

    ax2.hist(df_tickets["word_len"], bins=25, color="#06b6d4", edgecolor="#1e293b", alpha=0.85)
    ax2.set_title("Word Count Distribution", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Word Count")
    ax2.set_ylabel("Frequency")
    ax2.axvline(df_tickets["word_len"].mean(), color="#ef4444", linestyle="--", label=f"Mean: {df_tickets['word_len'].mean():.1f}")
    ax2.legend()

    plt.tight_layout()
    fig.savefig(SCREENSHOTS_DIR / "message_length_distribution.png")
    plt.close(fig)
    print("Saved docs/screenshots/message_length_distribution.png")

    # 4. Top Distinctive Keywords per Category
    stopwords = {"i", "me", "my", "myself", "we", "our", "you", "your", "the", "a", "an", "is", "was",
                 "are", "to", "for", "with", "at", "by", "from", "in", "on", "and", "or", "so", "it",
                 "be", "this", "that", "can", "get", "do", "of", "my", "have", "has", "not", "but", "what"}
    
    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    categories = list(df_tickets["category"].unique())

    for idx, (cat, ax) in enumerate(zip(categories, axes.flatten(), strict=False)):
        cat_texts = df_tickets[df_tickets["category"] == cat]["text"].str.lower().str.replace(r"[^\w\s]", "", regex=True)
        words = [w for t in cat_texts for w in t.split() if w not in stopwords and len(w) > 2]
        common = Counter(words).most_common(7)
        if common:
            w_names, w_counts = zip(*common, strict=False)
            ax.barh(list(w_names)[::-1], list(w_counts)[::-1], color="#3b82f6", edgecolor="#1e293b")
        ax.set_title(f"Class: {cat.upper()}", fontsize=11, fontweight="bold")
        ax.set_xlabel("Frequency")

    plt.suptitle("Top 7 Distinguishing Tokens per Customer Ticket Category", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(SCREENSHOTS_DIR / "top_words_per_category.png")
    plt.close(fig)
    print("Saved docs/screenshots/top_words_per_category.png")

    # 5. Orders Status Breakdown
    fig, ax = plt.subplots(figsize=(7, 4.5))
    order_counts = df_orders["status"].value_counts()
    status_colors = {"Delivered": "#10b981", "In Transit": "#3b82f6", "Delayed": "#ef4444", "Processing": "#f59e0b", "Cancelled": "#6b7280"}
    col_list = [status_colors.get(s, "#3b82f6") for s in order_counts.index]
    order_bars = ax.bar(order_counts.index, order_counts.values, color=col_list, width=0.55, edgecolor="#1e293b")
    ax.set_title("E-Commerce Order Fulfillment Status (500 Orders)", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel("Order Count")
    for bar in order_bars:
        h = bar.get_height()
        ax.annotate(f"{h} ({h/len(df_orders)*100:.1f}%)", xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=10, fontweight="bold")
    plt.tight_layout()
    fig.savefig(SCREENSHOTS_DIR / "orders_status_distribution.png")
    plt.close(fig)
    print("Saved docs/screenshots/orders_status_distribution.png")


if __name__ == "__main__":
    run_eda()
