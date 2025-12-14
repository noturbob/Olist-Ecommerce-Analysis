import pandas as pd
import numpy as np
from datetime import datetime

print("Starting data cleaning...")

# ============================================
# 1. LOAD DATA
# ============================================

customers = pd.read_csv('data/raw-data/olist_customers_dataset.csv')
geolocation = pd.read_csv('data/raw-data/olist_geolocation_dataset.csv')
order_items = pd.read_csv('data/raw-data/olist_order_items_dataset.csv')
payments = pd.read_csv('data/raw-data/olist_order_payments_dataset.csv')
reviews = pd.read_csv('data/raw-data/olist_order_reviews_dataset.csv')
orders = pd.read_csv('data/raw-data/olist_orders_dataset.csv')
products = pd.read_csv('data/raw-data/olist_products_dataset.csv')
sellers = pd.read_csv('data/raw-data/olist_sellers_dataset.csv')
category_translation = pd.read_csv('data/raw-data/product_category_name_translation.csv')

# ============================================
# 2. CLEAN ORDERS (MAIN TABLE)
# ============================================

print("\n📦 Cleaning Orders...")

# Convert timestamps to datetime
date_columns = ['order_purchase_timestamp', 'order_approved_at', 
                'order_delivered_carrier_date', 'order_delivered_customer_date',
                'order_estimated_delivery_date']

for col in date_columns:
    orders[col] = pd.to_datetime(orders[col], errors='coerce')

# Remove orders with no purchase date
orders = orders.dropna(subset=['order_purchase_timestamp'])

# Create useful date features
orders['order_date'] = orders['order_purchase_timestamp'].dt.date
orders['order_month'] = orders['order_purchase_timestamp'].dt.to_period('M')
orders['order_year'] = orders['order_purchase_timestamp'].dt.year
orders['order_quarter'] = orders['order_purchase_timestamp'].dt.quarter
orders['order_dayofweek'] = orders['order_purchase_timestamp'].dt.dayofweek
orders['order_hour'] = orders['order_purchase_timestamp'].dt.hour

# Calculate delivery time (actual vs estimated)
orders['actual_delivery_days'] = (
    orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']
).dt.days

orders['estimated_delivery_days'] = (
    orders['order_estimated_delivery_date'] - orders['order_purchase_timestamp']
).dt.days

orders['delivery_delay_days'] = (
    orders['actual_delivery_days'] - orders['estimated_delivery_days']
)

# Flag: delivered on time?
orders['on_time_delivery'] = orders['delivery_delay_days'] <= 0

print(f"Orders after cleaning: {len(orders):,}")
print(f"Date range: {orders['order_date'].min()} to {orders['order_date'].max()}")

# ============================================
# 3. CLEAN CUSTOMERS
# ============================================

print("\n👥 Cleaning Customers...")

# Remove duplicates
customers = customers.drop_duplicates(subset=['customer_id'])

# Standardize city names (title case)
customers['customer_city'] = customers['customer_city'].str.title()
customers['customer_state'] = customers['customer_state'].str.upper()

print(f"Customers after cleaning: {len(customers):,}")
print(f"Unique states: {customers['customer_state'].nunique()}")

# ============================================
# 4. CLEAN ORDER ITEMS
# ============================================

print("\n🛍️ Cleaning Order Items...")

# Remove negative prices (if any)
order_items = order_items[order_items['price'] > 0]

# Remove rows with missing product_id
order_items = order_items.dropna(subset=['product_id'])

print(f"Order items after cleaning: {len(order_items):,}")

# ============================================
# 5. CLEAN PAYMENTS
# ============================================

print("\n💳 Cleaning Payments...")

# Remove negative payment values
payments = payments[payments['payment_value'] > 0]

# Standardize payment types
payments['payment_type'] = payments['payment_type'].str.lower()

print(f"Payments after cleaning: {len(payments):,}")

# ============================================
# 6. CLEAN PRODUCTS
# ============================================

print("\n📦 Cleaning Products...")

# Remove duplicates
products = products.drop_duplicates(subset=['product_id'])

# Merge with category translation
products = products.merge(
    category_translation, 
    on='product_category_name', 
    how='left'
)

# Fill missing category names
products['product_category_name_english'].fillna('unknown', inplace=True)

print(f"Products after cleaning: {len(products):,}")

# ============================================
# 7. CLEAN REVIEWS
# ============================================

print("\n⭐ Cleaning Reviews...")

# Convert timestamps
reviews['review_creation_date'] = pd.to_datetime(reviews['review_creation_date'])
reviews['review_answer_timestamp'] = pd.to_datetime(reviews['review_answer_timestamp'])

# Ensure review scores are 1-5
reviews = reviews[reviews['review_score'].between(1, 5)]

print(f"Reviews after cleaning: {len(reviews):,}")

# ============================================
# 8. CLEAN SELLERS
# ============================================

print("\n🏪 Cleaning Sellers...")

# Standardize city names
sellers['seller_city'] = sellers['seller_city'].str.title()
sellers['seller_state'] = sellers['seller_state'].str.upper()

# Remove duplicates
sellers = sellers.drop_duplicates(subset=['seller_id'])

print(f"Sellers after cleaning: {len(sellers):,}")

# ============================================
# 9. CLEAN GEOLOCATION (Sample for performance)
# ============================================

print("\n🗺️ Cleaning Geolocation...")

# This file is huge (1M+ rows), let's aggregate
# Get average lat/long for each zip code prefix
geolocation['zip_code_prefix'] = geolocation['geolocation_zip_code_prefix']
geolocation_agg = geolocation.groupby('zip_code_prefix').agg({
    'geolocation_lat': 'mean',
    'geolocation_lng': 'mean',
    'geolocation_city': 'first',
    'geolocation_state': 'first'
}).reset_index()

print(f"Geolocation after aggregation: {len(geolocation_agg):,}")

# ============================================
# 10. SAVE CLEANED DATA
# ============================================

print("\n💾 Saving cleaned datasets...")

orders.to_csv('data/cleaned/orders_clean.csv', index=False)
customers.to_csv('data/cleaned/customers_clean.csv', index=False)
order_items.to_csv('data/cleaned/order_items_clean.csv', index=False)
payments.to_csv('data/cleaned/payments_clean.csv', index=False)
reviews.to_csv('data/cleaned/reviews_clean.csv', index=False)
products.to_csv('data/cleaned/products_clean.csv', index=False)
sellers.to_csv('data/cleaned/sellers_clean.csv', index=False)
geolocation_agg.to_csv('data/cleaned/geolocation_clean.csv', index=False)

print("\n✅ Data cleaning complete!")
print("\nCleaned files saved to data/cleaned/")