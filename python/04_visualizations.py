import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy import create_engine
import os
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

# Create database connection
engine = create_engine('sqlite:///data/olist_ecommerce.db')

# Create output directories
os.makedirs('visualizations', exist_ok=True)
os.makedirs('visualizations/interactive', exist_ok=True)

print("=" * 80)
print("📊 BUILDING COMPREHENSIVE VISUALIZATIONS")
print("=" * 80)

# ============================================
# 1. LOAD DATA FOR VISUALIZATIONS
# ============================================
print("\n📥 Loading data...")

orders = pd.read_sql("SELECT * FROM orders", engine)
order_items = pd.read_sql("SELECT * FROM order_items", engine)
customers = pd.read_sql("SELECT * FROM customers", engine)
products = pd.read_sql("SELECT * FROM products", engine)
reviews = pd.read_sql("SELECT * FROM order_reviews", engine)
sellers = pd.read_sql("SELECT * FROM sellers", engine)

print("✅ Data loaded!")

# ============================================
# 2. REVENUE BY STATE - INTERACTIVE MAP
# ============================================
print("\n🗺️ Creating: Revenue by State Map...")

revenue_by_state = pd.read_sql("""
SELECT 
    c.customer_state,
    COUNT(DISTINCT o.order_id) as orders,
    ROUND(SUM(oi.price), 2) as revenue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY revenue DESC
""", engine)

fig_state = px.bar(
    revenue_by_state,
    x='customer_state',
    y='revenue',
    color='orders',
    title='Revenue by State (Top States)',
    labels={'customer_state': 'State', 'revenue': 'Revenue (R$)', 'orders': 'Order Count'},
    color_continuous_scale='Viridis'
)
fig_state.update_layout(height=600, width=1200, font=dict(size=12))
fig_state.write_html('visualizations/interactive/01_revenue_by_state.html')
print("   ✅ Saved: visualizations/interactive/01_revenue_by_state.html")

# ============================================
# 3. REVENUE BY CITY - TOP 20
# ============================================
print("\n🏙️ Creating: Revenue by City (Top 20)...")

revenue_by_city = pd.read_sql("""
SELECT 
    c.customer_city,
    c.customer_state,
    COUNT(DISTINCT o.order_id) as orders,
    ROUND(SUM(oi.price), 2) as revenue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_city, c.customer_state
HAVING COUNT(DISTINCT o.order_id) >= 10
ORDER BY revenue DESC
LIMIT 20
""", engine)

fig_city = px.bar(
    revenue_by_city,
    x='customer_city',
    y='revenue',
    color='orders',
    title='Top 20 Cities by Revenue',
    labels={'customer_city': 'City', 'revenue': 'Revenue (R$)', 'orders': 'Order Count'},
    color_continuous_scale='Blues'
)
fig_city.update_xaxes(tickangle=45)
fig_city.update_layout(height=600, width=1200, font=dict(size=10))
fig_city.write_html('visualizations/interactive/02_revenue_by_city.html')
print("   ✅ Saved: visualizations/interactive/02_revenue_by_city.html")

# ============================================
# 4. ORDER VALUE DISTRIBUTION
# ============================================
print("\n💰 Creating: Order Value Distribution...")

order_prices = pd.read_sql("""
SELECT 
    oi.price
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
""", engine)

fig_price = go.Figure()
fig_price.add_trace(go.Histogram(
    x=order_prices['price'],
    nbinsx=50,
    name='Order Value',
    marker_color='rgba(100, 150, 255, 0.7)'
))
fig_price.update_layout(
    title='Distribution of Order Values',
    xaxis_title='Order Value (R$)',
    yaxis_title='Frequency',
    height=500,
    width=1200
)
fig_price.write_html('visualizations/interactive/03_price_distribution.html')
print("   ✅ Saved: visualizations/interactive/03_price_distribution.html")

# ============================================
# 5. DELIVERY TIME ANALYSIS
# ============================================
print("\n⏱️ Creating: Delivery Time Distribution...")

delivery_times = pd.read_sql("""
SELECT 
    CAST((julianday(order_delivered_customer_date) - julianday(order_purchase_timestamp)) AS FLOAT) as delivery_days
FROM orders
WHERE order_status = 'delivered'
""", engine)

fig_delivery = go.Figure()
fig_delivery.add_trace(go.Histogram(
    x=delivery_times['delivery_days'],
    nbinsx=40,
    name='Delivery Days',
    marker_color='rgba(255, 150, 100, 0.7)'
))
fig_delivery.update_layout(
    title='Distribution of Delivery Times',
    xaxis_title='Days to Deliver',
    yaxis_title='Frequency',
    height=500,
    width=1200
)
fig_delivery.write_html('visualizations/interactive/04_delivery_distribution.html')
print("   ✅ Saved: visualizations/interactive/04_delivery_distribution.html")

# ============================================
# 6. PAYMENT METHODS PIE CHART
# ============================================
print("\n💳 Creating: Payment Methods Breakdown...")

payment_methods = pd.read_sql("""
SELECT 
    payment_type,
    COUNT(*) as count,
    ROUND(SUM(payment_value), 2) as total_value
FROM order_payments
GROUP BY payment_type
ORDER BY count DESC
""", engine)

fig_payment = px.pie(
    payment_methods,
    values='count',
    names='payment_type',
    title='Payment Method Distribution',
    color_discrete_sequence=px.colors.qualitative.Set3
)
fig_payment.update_layout(height=600, width=1000)
fig_payment.write_html('visualizations/interactive/05_payment_methods.html')
print("   ✅ Saved: visualizations/interactive/05_payment_methods.html")

# ============================================
# 7. TOP PRODUCT CATEGORIES
# ============================================
print("\n📦 Creating: Top Product Categories...")

top_categories = pd.read_sql("""
SELECT 
    p.product_category_name_english as category,
    COUNT(DISTINCT oi.order_id) as orders,
    ROUND(SUM(oi.price), 2) as revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
  AND p.product_category_name_english IS NOT NULL
  AND p.product_category_name_english != 'unknown'
GROUP BY p.product_category_name_english
HAVING COUNT(DISTINCT oi.order_id) >= 10
ORDER BY revenue DESC
LIMIT 20
""", engine)

fig_cat = px.bar(
    top_categories,
    x='revenue',
    y='category',
    color='orders',
    orientation='h',
    title='Top 20 Product Categories by Revenue',
    labels={'revenue': 'Revenue (R$)', 'category': 'Category', 'orders': 'Orders'},
    color_continuous_scale='Greens'
)
fig_cat.update_layout(height=700, width=1200)
fig_cat.write_html('visualizations/interactive/06_top_categories.html')
print("   ✅ Saved: visualizations/interactive/06_top_categories.html")

# ============================================
# 8. MONTHLY REVENUE TREND
# ============================================
print("\n📈 Creating: Monthly Revenue Trend...")

monthly_revenue = pd.read_sql("""
SELECT 
    SUBSTR(o.order_purchase_timestamp, 1, 7) as month,
    COUNT(DISTINCT o.order_id) as orders,
    ROUND(SUM(oi.price), 2) as revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY SUBSTR(o.order_purchase_timestamp, 1, 7)
ORDER BY month
""", engine)

fig_trend = px.line(
    monthly_revenue,
    x='month',
    y='revenue',
    markers=True,
    title='Monthly Revenue Trend',
    labels={'month': 'Month', 'revenue': 'Revenue (R$)'},
    color_discrete_sequence=['#1f77b4']
)
fig_trend.add_scatter(
    x=monthly_revenue['month'],
    y=monthly_revenue['orders'],
    mode='lines',
    name='Order Count',
    yaxis='y2',
    line=dict(color='orange')
)
fig_trend.update_layout(
    height=600,
    width=1200,
    yaxis2=dict(
        title='Order Count',
        overlaying='y',
        side='right'
    ),
    hovermode='x unified'
)
fig_trend.write_html('visualizations/interactive/07_monthly_trend.html')
print("   ✅ Saved: visualizations/interactive/07_monthly_trend.html")

# ============================================
# 9. CUSTOMER STATE HEATMAP
# ============================================
print("\n🔥 Creating: State Frequency Heatmap...")

state_orders = pd.read_sql("""
SELECT 
    c.customer_state,
    SUBSTR(o.order_purchase_timestamp, 1, 7) as month,
    COUNT(*) as orders
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state, SUBSTR(o.order_purchase_timestamp, 1, 7)
""", engine)

pivot_states = state_orders.pivot_table(
    index='customer_state',
    columns='month',
    values='orders',
    fill_value=0
)

fig_heatmap = go.Figure(data=go.Heatmap(
    z=pivot_states.values,
    x=pivot_states.columns,
    y=pivot_states.index,
    colorscale='YlOrRd',
    colorbar=dict(title='Order Count')
))
fig_heatmap.update_layout(
    title='State-wise Order Distribution Over Time',
    xaxis_title='Month',
    yaxis_title='State',
    height=700,
    width=1400
)
fig_heatmap.write_html('visualizations/interactive/08_state_heatmap.html')
print("   ✅ Saved: visualizations/interactive/08_state_heatmap.html")

# ============================================
# 10. STATIC VISUALIZATIONS (PNG)
# ============================================
print("\n📸 Creating Static Visualizations (PNG)...")

# 10a. Revenue by State (static)
fig, ax = plt.subplots(figsize=(14, 8))
top_20_states = revenue_by_state.head(20)
sns.barplot(data=top_20_states, x='customer_state', y='revenue', palette='viridis', ax=ax)
ax.set_title('Revenue by State (Top 20)', fontsize=16, fontweight='bold')
ax.set_xlabel('State', fontsize=12)
ax.set_ylabel('Revenue (R$)', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('visualizations/01_static_revenue_state.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ Saved: visualizations/01_static_revenue_state.png")

# 10b. Order Status Distribution
order_status = pd.read_sql("""
SELECT 
    order_status,
    COUNT(*) as count
FROM orders
GROUP BY order_status
ORDER BY count DESC
""", engine)

fig, ax = plt.subplots(figsize=(10, 6))
colors = sns.color_palette('Set2', len(order_status))
ax.pie(order_status['count'], labels=order_status['order_status'], autopct='%1.1f%%', colors=colors, startangle=90)
ax.set_title('Order Status Distribution', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('visualizations/02_static_order_status.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ Saved: visualizations/02_static_order_status.png")

# 10c. Price Distribution (Seaborn)
fig, ax = plt.subplots(figsize=(14, 6))
sns.histplot(data=order_prices, x='price', bins=50, kde=True, color='steelblue', ax=ax)
ax.set_title('Distribution of Order Prices', fontsize=16, fontweight='bold')
ax.set_xlabel('Price (R$)', fontsize=12)
ax.set_ylabel('Frequency', fontsize=12)
plt.tight_layout()
plt.savefig('visualizations/03_static_price_dist.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ Saved: visualizations/03_static_price_dist.png")

# 10d. Delivery Time Distribution
fig, ax = plt.subplots(figsize=(14, 6))
sns.histplot(data=delivery_times, x='delivery_days', bins=40, kde=True, color='coral', ax=ax)
ax.set_title('Distribution of Delivery Times', fontsize=16, fontweight='bold')
ax.set_xlabel('Days to Delivery', fontsize=12)
ax.set_ylabel('Frequency', fontsize=12)
plt.tight_layout()
plt.savefig('visualizations/04_static_delivery_dist.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ Saved: visualizations/04_static_delivery_dist.png")

# 10e. Top Categories
fig, ax = plt.subplots(figsize=(14, 8))
top_15_cat = top_categories.head(15)
sns.barplot(data=top_15_cat, y='category', x='revenue', palette='RdYlGn', ax=ax)
ax.set_title('Top 15 Product Categories by Revenue', fontsize=16, fontweight='bold')
ax.set_xlabel('Revenue (R$)', fontsize=12)
ax.set_ylabel('Category', fontsize=12)
plt.tight_layout()
plt.savefig('visualizations/05_static_top_categories.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ Saved: visualizations/05_static_top_categories.png")

# 10f. Correlation: Price vs Review Score
price_review = pd.read_sql("""
SELECT 
    oi.price,
    r.review_score
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN order_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
  AND r.review_score IS NOT NULL
  AND oi.price < 1000
LIMIT 5000
""", engine)

fig, ax = plt.subplots(figsize=(12, 8))
sns.scatterplot(data=price_review, x='price', y='review_score', alpha=0.5, ax=ax)
sns.regplot(data=price_review, x='price', y='review_score', scatter=False, color='red', ax=ax)
ax.set_title('Price vs Review Score (Correlation)', fontsize=16, fontweight='bold')
ax.set_xlabel('Order Price (R$)', fontsize=12)
ax.set_ylabel('Review Score (1-5)', fontsize=12)
plt.tight_layout()
plt.savefig('visualizations/06_static_price_review.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ Saved: visualizations/06_static_price_review.png")

# ============================================
# 11. SUMMARY STATISTICS
# ============================================
print("\n📊 Creating Summary Statistics...")

summary_stats = {
    'Total Orders': len(orders),
    'Total Revenue': order_items['price'].sum(),
    'Avg Order Value': order_items['price'].mean(),
    'Total Customers': len(customers),
    'Total Products': len(products),
    'Avg Delivery Days': delivery_times['delivery_days'].mean(),
    'Avg Review Score': reviews['review_score'].mean()
}

summary_df = pd.DataFrame(list(summary_stats.items()), columns=['Metric', 'Value'])
summary_df.to_csv('sql_results/summary_statistics.csv', index=False)
print("   ✅ Saved: sql_results/summary_statistics.csv")

print("\n" + "=" * 80)
print("✅ VISUALIZATIONS COMPLETE!")
print("=" * 80)
print(f"\n📊 Static Visualizations (PNG): visualizations/")
print(f"🌐 Interactive Visualizations (HTML): visualizations/interactive/")
print("\nGenerated Files:")
print("  Interactive Maps & Charts:")
print("    - 01_revenue_by_state.html")
print("    - 02_revenue_by_city.html")
print("    - 03_price_distribution.html")
print("    - 04_delivery_distribution.html")
print("    - 05_payment_methods.html")
print("    - 06_top_categories.html")
print("    - 07_monthly_trend.html")
print("    - 08_state_heatmap.html")
print("\n  Static Images (PNG):")
print("    - 01_static_revenue_state.png")
print("    - 02_static_order_status.png")
print("    - 03_static_price_dist.png")
print("    - 04_static_delivery_dist.png")
print("    - 05_static_top_categories.png")
print("    - 06_static_price_review.png")
print("=" * 80)
