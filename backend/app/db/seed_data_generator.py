"""Synthetic dataset generator for SupportMind.

Generates:
1. orders.csv (500 realistic e-commerce orders with delayed/cancelled states)
2. tickets_train.csv (1,500 realistic customer queries with noise, typos, slang)
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Set fixed seeds for deterministic reproducibility
random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Casey", "Riley", "Avery", "Jamie",
    "Priya", "Carlos", "Mei", "Liam", "Emma", "Noah", "Olivia", "Ethan", "Sophia", "Lucas",
    "Aria", "Mateo", "Zoe", "Dante", "Elena", "Marcus", "Chloe", "Hassan", "Fatima", "Chen",
    "Yuki", "Ananya", "Devon", "Harper", "Siddharth", "Aisha", "Gabriel", "Camila", "Kai", "Maya"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez",
    "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore",
    "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez",
    "Lewis", "Robinson", "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Patel"
]

PRODUCTS = [
    ("NovaSound Wireless ANC Headphones", 149.99),
    ("NovaPulse Smart Fitness Tracker V3", 89.99),
    ("UltraView 4K Portable Monitor 15.6 inch", 219.50),
    ("AeroBrew Smart Temperature Coffee Mug", 64.00),
    ("ErgoGlide Ergonomic Office Chair", 349.99),
    ("TitanShield Rugged PowerBank 30000mAh", 49.99),
    ("LuminaDesk RGB LED Light Bar", 39.99),
    ("SoundBar Studio Pro with Wireless Subwoofer", 189.00),
    ("CleanWave Ultrasonic UV Toothbrush", 45.00),
    ("QuantumKey Mechanical Gaming Keyboard", 119.99),
    ("HyperSpeed Dual-Band Wi-Fi 6 Router", 129.00),
    ("PocketCam 4K Action Camera Bundle", 179.99),
    ("SwiftCharge 3-in-1 MagSafe Station", 59.99),
    ("BreezeAir HEPA True Allergen Purifier", 139.95),
    ("NovaTab Pro 10.5 inch Tablet 128GB", 299.00),
    ("EchoBreeze Desk Fan with Nightlight", 28.50),
    ("ArmorFit Water Bottle 32oz Insulated", 24.99),
    ("OmniGrip Silicone Kitchen Cookware Set", 79.99),
    ("Voyager Anti-Theft Travel Backpack", 85.00),
    ("AuraGlow Smart Sunset Ambient Lamp", 34.99)
]

CARRIERS = ["FedEx", "UPS", "USPS", "DHL Express"]
STATUSES = ["Delivered", "Delivered", "Delivered", "In Transit", "In Transit", "Delayed", "Processing", "Cancelled"]


def generate_orders(n=500, output_path=DATA_DIR / "orders.csv"):
    """Generate orders.csv with n orders."""
    start_date = datetime(2025, 12, 1)
    orders = []

    for i in range(1, n + 1):
        order_id = f"ORD-{10000 + i}"
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        customer_name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}{random.randint(10, 99)}@example.com"
        product, price = random.choice(PRODUCTS)
        
        # Fluctuate prices slightly for discounts / promotions
        price_adjusted = round(price * random.choice([0.85, 0.90, 1.0, 1.0, 1.0, 1.1]), 2)
        status = random.choice(STATUSES)
        
        order_dt = start_date + timedelta(days=random.randint(0, 75), hours=random.randint(0, 23))
        carrier = random.choice(CARRIERS)
        
        if status in ("Delivered", "In Transit", "Delayed"):
            exp_delivery = order_dt + timedelta(days=random.randint(3, 7))
        elif status == "Processing":
            exp_delivery = order_dt + timedelta(days=random.randint(2, 5))
        else: # Cancelled
            exp_delivery = order_dt + timedelta(days=random.randint(3, 6))

        orders.append({
            "order_id": order_id,
            "customer_name": customer_name,
            "email": email,
            "product_title": product,
            "price_usd": price_adjusted,
            "status": status,
            "order_date": order_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "expected_delivery": exp_delivery.strftime("%Y-%m-%d"),
            "carrier": carrier
        })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "order_id", "customer_name", "email", "product_title", "price_usd",
            "status", "order_date", "expected_delivery", "carrier"
        ])
        writer.writeheader()
        writer.writerows(orders)

    print(f"Generated {len(orders)} orders saved to {output_path}")


# Templates and vocabulary for tickets_train.csv
CATEGORY_TEMPLATES = {
    "billing": [
        "Why was my credit card charged twice for {order_id}?",
        "I was charged ${price} but checkout showed a discount code was active.",
        "Can I get a VAT invoice with my company tax number for order {order_id}?",
        "My bank statement has an unauthorized charge from NovaCart.",
        "Payment keeps failing with card ending in 4128, error code ERR_CARD_DECLINE.",
        "Did my refund go through? My bank still hasn't received the deposit.",
        "Charged for shipping even though my cart was over $50 threshold.",
        "Need a receipt PDF sent to my accountant right away.",
        "Duplicate charge on visa statement for NovaSound headphones.",
        "Klarna payment installment was taken twice this month.",
        "Why is there a $10 fee on my receipt?",
        "Card was charged but I never got an order confirmation email."
    ],
    "delivery": [
        "Where is my package? Tracking for {order_id} hasn't updated in 4 days.",
        "Tracking says delivered yesterday but nothing on my porch or mailroom.",
        "My order {order_id} was supposed to arrive yesterday, when will it be here?",
        "Can I change the delivery address to 742 Evergreen Terrace before it ships?",
        "FedEx marked parcel delayed due to severe weather, any ETA updates?",
        "Package arrived at wrong apartment unit, driver dropped it down the hall.",
        "Tracking number TRK-992144 shows stalled in transit at Memphis hub.",
        "Carrier left package in the rain and box is soaking wet.",
        "Can I reschedule delivery for Monday when I am home from work?",
        "Need overnight delivery upgrade for order {order_id} urgently.",
        "Delivery driver didn't ring the buzzer and marked delivery attempted."
    ],
    "refund": [
        "I want to return the {product} from order {order_id}, how do I get a return label?",
        "Item doesn't fit my desk, please initiate a full refund.",
        "Returned my parcel 10 days ago, where is my refund money?",
        "Sent back the broken headset, when does the money hit my PayPal?",
        "Want to exchange this coffee mug for a black one instead of white.",
        "Is there a restocking fee for returning unopened headphones within 30 days?",
        "Can I return an item after 35 days for store credit?",
        "Received damaged goods, packaging was crushed. I want my money back.",
        "Return label says $5.99 deducted, but I was sent the wrong color by mistake!",
        "Need to return three items from my last order."
    ],
    "account": [
        "Forgot my password and the reset email is not arriving in my inbox.",
        "My account is locked after typing my password wrong a few times.",
        "How do I enable two-factor authentication on my NovaCart account?",
        "Please delete my account and all personal data under GDPR right to be forgotten.",
        "How do I update my registered email address from old yahoo mail?",
        "Want to cancel my NovaCart Plus annual subscription before it auto-renews.",
        "I'm not receiving order status SMS notifications on my new phone number.",
        "How do I remove saved credit cards from my wallet profile?",
        "Suspicious login attempt alert received from unknown IP in Russia.",
        "Cannot log in via Google SSO, getting a blank redirect."
    ],
    "product": [
        "Does the {product} come with a 1-year manufacturer warranty?",
        "How do I pair the NovaSound headphones with two Bluetooth devices at once?",
        "Is the Smart Coffee Mug dishwasher safe or hand wash only?",
        "Will the 4K portable monitor connect directly to an iPhone 15 via USB-C?",
        "My powerbank stopped charging past 2 bars, is this covered under warranty?",
        "Do you have a user manual PDF for setting up the True Allergen Purifier?",
        "What are the exact dimensions of the ErgoGlide office chair seat?",
        "Is the stainless steel bottle BPA free and lead free?",
        "Firmware update failed on my smart fitness tracker, screen is frozen black.",
        "Are replacement filter cartridges in stock for the CleanWave unit?"
    ],
    "other": [
        "Do you have a physical retail store in Chicago or New York?",
        "Are you currently hiring customer service representatives?",
        "Can I place a wholesale bulk order of 200 units for our corporate retreat?",
        "Who is the CEO of NovaCart?",
        "What is your environmental carbon offset policy for parcel logistics?",
        "Do you sponsor college esports tournaments or tech podcasts?",
        "Can I submit an unsolicited product invention idea to your engineering team?",
        "Is NovaCart participating in upcoming Black Friday sales?",
        "Website buttons are overlapping on mobile Safari iOS 17.2.",
        "Just wanted to say your packaging design looks really modern and cool!"
    ]
}

NOISE_VARIATIONS = [
    lambda s: s.lower(),
    lambda s: s.upper(),
    lambda s: s.replace("?", "???"),
    lambda s: s.replace(".", "..."),
    lambda s: s + " pls reply asap!!",
    lambda s: s + " hello?? anyone there??",
    lambda s: "hey support team, " + s.lower(),
    lambda s: s.replace("the", "teh").replace("package", "pakage"),
    lambda s: s.replace("please", "plz").replace("you", "u"),
    lambda s: s.replace("your", "ur").replace("order", "ordr"),
    lambda s: "URGENT: " + s,
    lambda s: s
]


def generate_tickets(n=1500, output_path=DATA_DIR / "tickets_train.csv"):
    """Generate tickets_train.csv with 1,500 realistic noisy records."""
    categories = list(CATEGORY_TEMPLATES.keys())
    # Category distribution: roughly balanced with slight realistic bias towards delivery/refund
    weights = [0.20, 0.25, 0.22, 0.12, 0.15, 0.06]
    
    tickets = []
    for i in range(1, n + 1):
        ticket_id = f"TCK-{2000 + i}"
        cat = random.choices(categories, weights=weights)[0]
        template = random.choice(CATEGORY_TEMPLATES[cat])
        
        # Format variables
        order_num = f"ORD-{random.randint(10001, 10500)}"
        prod_title, prod_price = random.choice(PRODUCTS)
        
        msg = template.format(
            order_id=order_num,
            product=prod_title,
            price=f"{prod_price:.2f}"
        )
        
        # Apply realistic noise / typos / casing
        if random.random() < 0.45:
            noise_fn = random.choice(NOISE_VARIATIONS)
            msg = noise_fn(msg)
            
        # Determine urgency
        high_urgency_words = ["unauthorized", "stolen", "lawyer", "chargeback", "police", "fraud", "urgent", "asap", "ruined", "emergency", "twice", "furious"]
        low_urgency_words = ["retail store", "hiring", "wholesale", "dimensions", "manual", "cool", "black friday", "sponsorship"]
        
        lower_msg = msg.lower()
        if any(w in lower_msg for w in high_urgency_words) or random.random() < 0.12:
            urgency = "high"
        elif any(w in lower_msg for w in low_urgency_words) or cat == "other" or random.random() < 0.35:
            urgency = "low"
        else:
            urgency = "medium"
            
        # Determine sentiment
        if urgency == "high" or any(w in lower_msg for w in ["broken", "crushed", "hate", "terrible", "stalled", "locked", "worst", "fail"]):
            sentiment = "negative"
        elif any(w in lower_msg for w in ["cool", "thanks", "great", "love", "awesome", "good"]):
            sentiment = "positive"
        else:
            sentiment = "neutral"
            
        tickets.append({
            "ticket_id": ticket_id,
            "text": msg,
            "category": cat,
            "urgency": urgency,
            "sentiment": sentiment
        })
        
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["ticket_id", "text", "category", "urgency", "sentiment"])
        writer.writeheader()
        writer.writerows(tickets)
        
    print(f"Generated {len(tickets)} tickets saved to {output_path}")


if __name__ == "__main__":
    generate_orders(500)
    generate_tickets(1500)
