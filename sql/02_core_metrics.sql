-- ============================================
-- OLIST E-COMMERCE: CORE BUSINESS METRICS
-- ============================================

-- ============================================
-- QUERY 1: OVERALL BUSINESS SUMMARY
-- ============================================

SELECT 
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(DISTINCT o.customer_id) as total_customers,
    COUNT(DISTINCT oi.product_id) as total_products_sold,
    COUNT(DISTINCT oi.seller_id) as active_sellers,
    ROUND(SUM(oi.price)::NUMERIC, 2) as total_revenue,
    ROUND(AVG(oi.price)::NUMERIC, 2) as avg_order_value,
    ROUND(SUM(oi.freight_value)::NUMERIC, 2) as total_freight_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable');

-- ============================================
-- QUERY 2: REVENUE BY STATE (TOP 10)
-- ============================================

SELECT 
    c.customer_state,
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    ROUND(SUM(oi.price)::NUMERIC, 2) as total_revenue,
    ROUND(AVG(oi.price)::NUMERIC, 2) as avg_order_value,
    ROUND(SUM(oi.price) / COUNT(DISTINCT o.customer_id)::NUMERIC, 2) as revenue_per_customer
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY total_revenue DESC
LIMIT 10;

-- ============================================
-- QUERY 3: REVENUE BY CITY (TOP 15)
-- ============================================

SELECT 
    c.customer_city,
    c.customer_state,
    COUNT(DISTINCT o.order_id) as total_orders,
    ROUND(SUM(oi.price)::NUMERIC, 2) as total_revenue,
    ROUND(AVG(oi.price)::NUMERIC, 2) as avg_order_value
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_city, c.customer_state
HAVING COUNT(DISTINCT o.order_id) >= 10  -- Cities with at least 10 orders
ORDER BY total_revenue DESC
LIMIT 15;

-- ============================================
-- QUERY 4: MONTHLY REVENUE TREND
-- ============================================

SELECT 
    o.order_year,
    o.order_month,
    COUNT(DISTINCT o.order_id) as orders,
    ROUND(SUM(oi.price)::NUMERIC, 2) as revenue,
    ROUND(AVG(oi.price)::NUMERIC, 2) as avg_order_value,
    COUNT(DISTINCT o.customer_id) as unique_customers
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY o.order_year, o.order_month
ORDER BY o.order_year, o.order_month;

-- ============================================
-- QUERY 5: QUARTERLY PERFORMANCE
-- ============================================

SELECT 
    o.order_year,
    'Q' || o.order_quarter as quarter,
    COUNT(DISTINCT o.order_id) as total_orders,
    ROUND(SUM(oi.price)::NUMERIC, 2) as revenue,
    ROUND(SUM(oi.price) / COUNT(DISTINCT o.order_id)::NUMERIC, 2) as avg_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY o.order_year, o.order_quarter
ORDER BY o.order_year, o.order_quarter;

-- ============================================
-- QUERY 6: DAY OF WEEK ANALYSIS
-- ============================================

SELECT 
    CASE o.order_dayofweek
        WHEN 0 THEN 'Monday'
        WHEN 1 THEN 'Tuesday'
        WHEN 2 THEN 'Wednesday'
        WHEN 3 THEN 'Thursday'
        WHEN 4 THEN 'Friday'
        WHEN 5 THEN 'Saturday'
        WHEN 6 THEN 'Sunday'
    END as day_of_week,
    COUNT(DISTINCT o.order_id) as total_orders,
    ROUND(SUM(oi.price)::NUMERIC, 2) as revenue,
    ROUND(AVG(oi.price)::NUMERIC, 2) as avg_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY o.order_dayofweek
ORDER BY o.order_dayofweek;

-- ============================================
-- QUERY 7: HOURLY PURCHASE PATTERNS
-- ============================================

SELECT 
    o.order_hour,
    COUNT(DISTINCT o.order_id) as total_orders,
    ROUND(SUM(oi.price)::NUMERIC, 2) as revenue,
    ROUND(AVG(COUNT(DISTINCT o.order_id)) OVER (
        ORDER BY o.order_hour 
        ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
    ), 2) as moving_avg_orders
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY o.order_hour
ORDER BY o.order_hour;

-- ============================================
-- QUERY 8: RUNNING TOTAL REVENUE (WINDOW FUNCTION)
-- ============================================

WITH daily_revenue AS (
    SELECT 
        o.order_date,
        ROUND(SUM(oi.price)::NUMERIC, 2) as daily_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY o.order_date
)
SELECT 
    order_date,
    daily_revenue,
    SUM(daily_revenue) OVER (ORDER BY order_date) as cumulative_revenue,
    ROUND(AVG(daily_revenue) OVER (
        ORDER BY order_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    )::NUMERIC, 2) as ma_7day,
    ROUND(AVG(daily_revenue) OVER (
        ORDER BY order_date 
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    )::NUMERIC, 2) as ma_30day
FROM daily_revenue
ORDER BY order_date;

-- ============================================
-- QUERY 9: ORDER STATUS BREAKDOWN
-- ============================================

SELECT 
    o.order_status,
    COUNT(*) as order_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage,
    ROUND(AVG(oi.price)::NUMERIC, 2) as avg_order_value
FROM orders o
LEFT JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_status
ORDER BY order_count DESC;