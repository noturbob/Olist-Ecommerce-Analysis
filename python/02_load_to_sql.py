import pandas as pd
from sqlalchemy import create_engine, text
import time

# Create database connection
# Option A: PostgreSQL
# engine = create_engine('postgresql://username:password@localhost:5432/olist_db')

# Option B: SQLite (simpler, no installation needed)
engine = create_engine('sqlite:///data/olist_ecommerce.db')

print("Loading data to database...")

# Load cleaned data
datasets = {
    'customers': 'data/cleaned/customers_clean.csv',
    'sellers': 'data/cleaned/sellers_clean.csv',
    'products': 'data/cleaned/products_clean.csv',
    'orders': 'data/cleaned/orders_clean.csv',
    'order_items': 'data/cleaned/order_items_clean.csv',
    'order_payments': 'data/cleaned/payments_clean.csv',
    'order_reviews': 'data/cleaned/reviews_clean.csv',
    'geolocation': 'data/cleaned/geolocation_clean.csv'
}

for table_name, file_path in datasets.items():
    print(f"\n📊 Loading {table_name}...")
    start_time = time.time()
    
    df = pd.read_csv(file_path)
    
    # Convert date columns back to datetime
    date_cols = [col for col in df.columns if 'timestamp' in col or 'date' in col]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Load to database
    df.to_sql(table_name, engine, if_exists='replace', index=False, chunksize=1000)
    
    elapsed = time.time() - start_time
    print(f"   ✅ Loaded {len(df):,} rows in {elapsed:.2f} seconds")

# Verify data
print("\n" + "=" * 60)
print("VERIFICATION")
print("=" * 60)

with engine.connect() as conn:
    for table in datasets.keys():
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
        count = result.fetchone()[0]
        print(f"{table}: {count:,} rows")

print("\n✅ All data loaded successfully!")