import pandas as pd
import numpy as np

# Load all datasets
customers = pd.read_csv('data/raw-data/olist_customers_dataset.csv')
geolocation = pd.read_csv('data/raw-data/olist_geolocation_dataset.csv')
order_items = pd.read_csv('data/raw-data/olist_order_items_dataset.csv')
payments = pd.read_csv('data/raw-data/olist_order_payments_dataset.csv')
reviews = pd.read_csv('data/raw-data/olist_order_reviews_dataset.csv')
orders = pd.read_csv('data/raw-data/olist_orders_dataset.csv')
products = pd.read_csv('data/raw-data/olist_products_dataset.csv')
sellers = pd.read_csv('data/raw-data/olist_sellers_dataset.csv')
category_translation = pd.read_csv('data/raw-data/product_category_name_translation.csv')

# Print basic info
datasets = {
    'Customers': customers,
    'Geolocation': geolocation,
    'Order Items': order_items,
    'Payments': payments,
    'Reviews': reviews,
    'Orders': orders,
    'Products': products,
    'Sellers': sellers,
    'Categories': category_translation
}

print("=" * 60)
print("OLIST E-COMMERCE DATASET OVERVIEW")
print("=" * 60)

for name, df in datasets.items():
    print(f"\n📊 {name}")
    print(f"   Rows: {len(df):,}")
    print(f"   Columns: {len(df.columns)}")
    print(f"   Columns: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
    print(f"   Missing values: {df.isnull().sum().sum()}")

# Key statistics
print("\n" + "=" * 60)
print("KEY METRICS")
print("=" * 60)
print(f"Total Orders: {len(orders):,}")
print(f"Total Customers: {len(customers):,}")
print(f"Total Products: {len(products):,}")
print(f"Total Sellers: {len(sellers):,}")
print(f"Date Range: {orders['order_purchase_timestamp'].min()} to {orders['order_purchase_timestamp'].max()}")

# Order status breakdown
print("\n📦 Order Status:")
print(orders['order_status'].value_counts())

# Payment methods
print("\n💳 Payment Methods:")
print(payments['payment_type'].value_counts())

print("\n✅ Exploration complete!")