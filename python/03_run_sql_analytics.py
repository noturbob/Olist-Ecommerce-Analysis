import pandas as pd
from sqlalchemy import create_engine, text
import os

# Create database connection
engine = create_engine('sqlite:///data/olist_ecommerce.db')

print("=" * 80)
print("🚀 EXECUTING SQL ANALYTICS QUERIES")
print("=" * 80)

# Create output directory for results
os.makedirs('sql_results', exist_ok=True)

# ============================================
# QUERY 1: OVERALL BUSINESS SUMMARY
# ============================================
print("\n📊 QUERY 1: OVERALL BUSINESS SUMMARY")
print("-" * 80)

query_1 = """
SELECT 
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(DISTINCT o.customer_id) as total_customers,
    COUNT(DISTINCT oi.product_id) as total_products_sold,
    COUNT(DISTINCT oi.seller_id) as active_sellers,
    ROUND(SUM(oi.price), 2) as total_revenue,
    ROUND(AVG(oi.price), 2) as avg_order_value,
    ROUND(SUM(oi.freight_value), 2) as total_freight_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
"""

try:
    df = pd.read_sql(query_1, engine)
    print(f"✅ Rows: {len(df):,}")
    print(f"\n{df.to_string(index=False)}\n")
    df.to_csv('sql_results/01_business_summary.csv', index=False)
    print("💾 Saved: sql_results/01_business_summary.csv")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# ============================================
# QUERY 2: REVENUE BY STATE (TOP 10)
# ============================================
print("\n📊 QUERY 2: REVENUE BY STATE (TOP 10)")
print("-" * 80)

query_2 = """
SELECT 
    c.customer_state,
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    ROUND(SUM(oi.price), 2) as total_revenue,
    ROUND(AVG(oi.price), 2) as avg_order_value,
    ROUND(SUM(oi.price) / COUNT(DISTINCT o.customer_id), 2) as revenue_per_customer
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY total_revenue DESC
LIMIT 10
"""

try:
    df = pd.read_sql(query_2, engine)
    print(f"✅ Rows: {len(df):,}")
    print(f"\n{df.to_string(index=False)}\n")
    df.to_csv('sql_results/02_revenue_by_state.csv', index=False)
    print("💾 Saved: sql_results/02_revenue_by_state.csv")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# ============================================
# QUERY 3: REVENUE BY CITY (TOP 15)
# ============================================
print("\n📊 QUERY 3: REVENUE BY CITY (TOP 15)")
print("-" * 80)

query_3 = """
SELECT 
    c.customer_city,
    c.customer_state,
    COUNT(DISTINCT o.order_id) as total_orders,
    ROUND(SUM(oi.price), 2) as total_revenue,
    ROUND(AVG(oi.price), 2) as avg_order_value
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_city, c.customer_state
HAVING COUNT(DISTINCT o.order_id) >= 10
ORDER BY total_revenue DESC
LIMIT 15
"""

try:
    df = pd.read_sql(query_3, engine)
    print(f"✅ Rows: {len(df):,}")
    print(f"\n{df.to_string(index=False)}\n")
    df.to_csv('sql_results/03_revenue_by_city.csv', index=False)
    print("💾 Saved: sql_results/03_revenue_by_city.csv")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# ============================================
# QUERY 4: TOP PAYMENT METHODS
# ============================================
print("\n📊 QUERY 4: TOP PAYMENT METHODS")
print("-" * 80)

query_4 = """
SELECT 
    op.payment_type,
    COUNT(DISTINCT op.order_id) as total_orders,
    ROUND(100.0 * COUNT(DISTINCT op.order_id) / (SELECT COUNT(DISTINCT order_id) FROM order_payments), 2) as percentage,
    ROUND(SUM(op.payment_value), 2) as total_value,
    ROUND(AVG(op.payment_value), 2) as avg_value
FROM order_payments op
JOIN orders o ON op.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY op.payment_type
ORDER BY total_orders DESC
"""

try:
    df = pd.read_sql(query_4, engine)
    print(f"✅ Rows: {len(df):,}")
    print(f"\n{df.to_string(index=False)}\n")
    df.to_csv('sql_results/04_payment_methods.csv', index=False)
    print("💾 Saved: sql_results/04_payment_methods.csv")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# ============================================
# QUERY 5: TOP PRODUCT CATEGORIES
# ============================================
print("\n📊 QUERY 5: TOP PRODUCT CATEGORIES")
print("-" * 80)

query_5 = """
SELECT 
    p.product_category_name_english as category,
    COUNT(DISTINCT oi.order_id) as total_orders,
    COUNT(DISTINCT p.product_id) as unique_products,
    ROUND(SUM(oi.price), 2) as total_revenue,
    ROUND(AVG(oi.price), 2) as avg_price
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
  AND p.product_category_name_english IS NOT NULL
  AND p.product_category_name_english != 'unknown'
GROUP BY p.product_category_name_english
HAVING COUNT(DISTINCT oi.order_id) >= 10
ORDER BY total_revenue DESC
LIMIT 15
"""

try:
    df = pd.read_sql(query_5, engine)
    print(f"✅ Rows: {len(df):,}")
    print(f"\n{df.to_string(index=False)}\n")
    df.to_csv('sql_results/05_top_categories.csv', index=False)
    print("💾 Saved: sql_results/05_top_categories.csv")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# ============================================
# QUERY 6: DELIVERY TIME ANALYSIS
# ============================================
print("\n📊 QUERY 6: DELIVERY TIME ANALYSIS")
print("-" * 80)

query_6 = """
SELECT 
    ROUND(AVG(CAST((julianday(order_delivered_customer_date) - julianday(order_purchase_timestamp)) AS FLOAT)), 2) as avg_delivery_days,
    ROUND(MIN(CAST((julianday(order_delivered_customer_date) - julianday(order_purchase_timestamp)) AS FLOAT)), 2) as min_delivery_days,
    ROUND(MAX(CAST((julianday(order_delivered_customer_date) - julianday(order_purchase_timestamp)) AS FLOAT)), 2) as max_delivery_days,
    COUNT(*) as delivered_orders
FROM orders
WHERE order_status = 'delivered'
"""

try:
    df = pd.read_sql(query_6, engine)
    print(f"✅ Rows: {len(df):,}")
    print(f"\n{df.to_string(index=False)}\n")
    df.to_csv('sql_results/06_delivery_analysis.csv', index=False)
    print("💾 Saved: sql_results/06_delivery_analysis.csv")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# ============================================
# QUERY 7: CUSTOMER SEGMENTATION
# ============================================
print("\n📊 QUERY 7: CUSTOMER SEGMENTATION (RFM-Style)")
print("-" * 80)

query_7 = """
WITH customer_metrics AS (
    SELECT 
        o.customer_id,
        COUNT(DISTINCT o.order_id) as total_orders,
        ROUND(SUM(oi.price), 2) as total_spent
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY o.customer_id
)
SELECT 
    CASE 
        WHEN total_orders = 1 THEN 'One-time buyer'
        WHEN total_orders = 2 THEN 'Repeat buyer (2 orders)'
        WHEN total_orders >= 3 THEN 'Loyal customer (3+ orders)'
    END as segment,
    COUNT(*) as customer_count,
    ROUND(AVG(total_spent), 2) as avg_lifetime_value
FROM customer_metrics
GROUP BY segment
"""

try:
    df = pd.read_sql(query_7, engine)
    print(f"✅ Rows: {len(df):,}")
    print(f"\n{df.to_string(index=False)}\n")
    df.to_csv('sql_results/07_customer_segmentation.csv', index=False)
    print("💾 Saved: sql_results/07_customer_segmentation.csv")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# ============================================
# QUERY 8: ORDER STATUS BREAKDOWN
# ============================================
print("\n📊 QUERY 8: ORDER STATUS BREAKDOWN")
print("-" * 80)

query_8 = """
SELECT 
    order_status,
    COUNT(*) as order_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM orders), 2) as percentage
FROM orders
GROUP BY order_status
ORDER BY order_count DESC
"""

try:
    df = pd.read_sql(query_8, engine)
    print(f"✅ Rows: {len(df):,}")
    print(f"\n{df.to_string(index=False)}\n")
    df.to_csv('sql_results/08_order_status.csv', index=False)
    print("💾 Saved: sql_results/08_order_status.csv")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# ============================================
# QUERY 9: TOP SELLERS
# ============================================
print("\n📊 QUERY 9: TOP 15 SELLERS")
print("-" * 80)

query_9 = """
SELECT 
    oi.seller_id,
    s.seller_city,
    s.seller_state,
    COUNT(DISTINCT oi.order_id) as total_orders,
    COUNT(DISTINCT oi.product_id) as products_sold,
    ROUND(SUM(oi.price), 2) as total_revenue,
    ROUND(AVG(oi.price), 2) as avg_price
FROM order_items oi
JOIN sellers s ON oi.seller_id = s.seller_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY oi.seller_id, s.seller_city, s.seller_state
ORDER BY total_revenue DESC
LIMIT 15
"""

try:
    df = pd.read_sql(query_9, engine)
    print(f"✅ Rows: {len(df):,}")
    print(f"\n{df.to_string(index=False)}\n")
    df.to_csv('sql_results/09_top_sellers.csv', index=False)
    print("💾 Saved: sql_results/09_top_sellers.csv")
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n" + "=" * 80)
print("✅ SQL ANALYTICS COMPLETE!")
print("📁 Results saved to: sql_results/")
print("=" * 80)
