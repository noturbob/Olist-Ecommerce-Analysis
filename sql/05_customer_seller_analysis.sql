-- ============================================
-- CUSTOMER BEHAVIOR & SELLER PERFORMANCE
-- ============================================

-- ============================================
-- QUERY 23: CUSTOMER PURCHASE FREQUENCY (RFM-style)
-- ============================================

WITH customer_metrics AS (
    SELECT 
        o.customer_id,
        COUNT(DISTINCT o.order_id) as total_orders,
        ROUND(SUM(oi.price)::NUMERIC, 2) as total_spent,
        ROUND(AVG(oi.price)::NUMERIC, 2) as avg_order_value,
        MIN(o.order_purchase_timestamp) as first_purchase,
        MAX(o.order_purchase_timestamp) as last_purchase,
        MAX(o.order_purchase_timestamp)::DATE - MIN(o.order_purchase_timestamp)::DATE as customer_lifetime_days
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
    END as customer_segment,
    COUNT(*) as customer_count,
    ROUND(AVG(total_spent)::NUMERIC, 2) as avg_lifetime_value,
    ROUND(AVG(avg_order_value)::NUMERIC, 2) as avg_order_value
FROM customer_metrics
GROUP BY customer_segment
ORDER BY 
    CASE 
        WHEN customer_segment = 'Loyal customer (3+ orders)' THEN 1
        WHEN customer_segment = 'Repeat buyer (2 orders)' THEN 2
        ELSE 3
    END;

-- ============================================
-- QUERY 24: TOP 20 CUSTOMERS (By Total Spend)
-- ============================================

SELECT 
    o.customer_id,
    c.customer_city,
    c.customer_state,
    COUNT(DISTINCT o.order_id) as total_orders,
    ROUND(SUM(oi.price)::NUMERIC, 2) as total_spent,
    ROUND(AVG(oi.price)::NUMERIC, 2) as avg_order_value,
    MIN(o.order_purchase_timestamp)::DATE as first_purchase,
    MAX(o.order_purchase_timestamp)::DATE as last_purchase
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY o.customer_id, c.customer_city, c.customer_state
ORDER BY total_spent DESC
LIMIT 20;

-- ============================================
-- QUERY 25: CUSTOMER RETENTION (COHORT ANALYSIS)
-- ============================================

WITH first_purchase AS (
    SELECT 
        customer_id,
        DATE_TRUNC('month', MIN(order_purchase_timestamp)) as cohort_month
    FROM orders
    WHERE order_status = 'delivered'
    GROUP BY customer_id
),
customer_orders AS (
    SELECT 
        o.customer_id,
        DATE_TRUNC('month', o.order_purchase_timestamp) as order_month
    FROM orders o
    WHERE o.order_status = 'delivered'
)
SELECT 
    fp.cohort_month,
    co.order_month,
    COUNT(DISTINCT co.customer_id) as active_customers,
    EXTRACT(MONTH FROM AGE(co.order_month, fp.cohort_month)) as months_since_first_purchase
FROM first_purchase fp
JOIN customer_orders co ON fp.customer_id = co.customer_id
GROUP BY fp.cohort_month, co.order_month
ORDER BY fp.cohort_month, co.order_month;

-- ============================================
-- QUERY 26: TOP SELLERS BY REVENUE
-- ============================================

SELECT 
    s.seller_id,
    s.seller_city,
    s.seller_state,
    COUNT(DISTINCT oi.order_id) as total_orders,
    COUNT(DISTINCT oi.product_id) as unique_products,
    ROUND(SUM(oi.price)::NUMERIC, 2) as total_revenue,
    ROUND(AVG(oi.price)::NUMERIC, 2) as avg_item_price,
    ROUND(AVG(r.review_score)::NUMERIC, 2) as avg_review_score
FROM sellers s
JOIN order_items oi ON s.seller_id = oi.seller_id
JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN order_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY s.seller_id, s.seller_city, s.seller_state
HAVING COUNT(DISTINCT oi.order_id) >= 10
ORDER BY total_revenue DESC
LIMIT 20;

-- ============================================
-- QUERY 27: SELLER PERFORMANCE BY STATE
-- ============================================

SELECT 
    s.seller_state,
    COUNT(DISTINCT s.seller_id) as total_sellers,
    COUNT(DISTINCT oi.order_id) as total_orders,
    ROUND(SUM(oi.price)::NUMERIC, 2) as total_revenue,
    ROUND(AVG(oi.price)::NUMERIC, 2) as avg_order_value,
    ROUND(SUM(oi.price) / COUNT(DISTINCT s.seller_id)::NUMERIC, 2) as revenue_per_seller
FROM sellers s
JOIN order_items oi ON s.seller_id = oi.seller_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY s.seller_state
ORDER BY total_revenue DESC;

-- ============================================
-- QUERY 28: REVIEW SCORE ANALYSIS
-- ============================================

SELECT 
    r.review_score,
    COUNT(*) as review_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage,
    ROUND(AVG(oi.price)::NUMERIC, 2) as avg_order_value,
    ROUND(AVG(o.delivery_delay_days)::NUMERIC, 2) as avg_delivery_delay
FROM order_reviews r
JOIN orders o ON r.order_id = o.order_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY r.review_score
ORDER BY r.review_score DESC;

-- ============================================
-- QUERY 29: REVIEW SCORE BY PRODUCT CATEGORY
-- ============================================

SELECT 
    p.product_category_name_english as category,
    COUNT(DISTINCT r.review_id) as total_reviews,
    ROUND(AVG(r.review_score)::NUMERIC, 2) as avg_review_score,
    SUM(CASE WHEN r.review_score >= 4 THEN 1 ELSE 0 END) as positive_reviews,
    ROUND(100.0 * SUM(CASE WHEN r.review_score >= 4 THEN 1 ELSE 0 END) / COUNT(*), 2) as positive_review_percentage
FROM order_reviews r
JOIN orders o ON r.order_id = o.order_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE p.product_category_name_english IS NOT NULL
  AND p.product_category_name_english != 'unknown'
GROUP BY p.product_category_name_english
HAVING COUNT(DISTINCT r.review_id) >= 20
ORDER BY avg_review_score DESC;

-- ============================================
-- QUERY 30: FREIGHT COST ANALYSIS
-- ============================================

SELECT 
    c.customer_state,
    COUNT(DISTINCT oi.order_id) as total_orders,
    ROUND(AVG(oi.freight_value)::NUMERIC, 2) as avg_freight_cost,
    ROUND(AVG(oi.price)::NUMERIC, 2) as avg_product_price,
    ROUND(100.0 * AVG(oi.freight_value) / AVG(oi.price), 2) as freight_as_pct_of_price
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
HAVING COUNT(DISTINCT oi.order_id) >= 10
ORDER BY avg_freight_cost DESC;

-- ============================================
-- QUERY 31: ADVANCED - CUSTOMER LIFETIME VALUE PREDICTION
-- ============================================

WITH customer_lifetime AS (
    SELECT 
        o.customer_id,
        COUNT(DISTINCT o.order_id) as order_count,
        ROUND(SUM(oi.price)::NUMERIC, 2) as lifetime_value,
        MIN(o.order_purchase_timestamp)::DATE as first_order_date,
        MAX(o.order_purchase_timestamp)::DATE as last_order_date,
        MAX(o.order_purchase_timestamp)::DATE - MIN(o.order_purchase_timestamp)::DATE as customer_age_days,
        ROUND(AVG(oi.price)::NUMERIC, 2) as avg_order_value
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY o.customer_id
)
SELECT 
    CASE 
        WHEN customer_age_days = 0 THEN '0 days (single purchase)'
        WHEN customer_age_days <= 30 THEN '1-30 days'
        WHEN customer_age_days <= 90 THEN '31-90 days'
        WHEN customer_age_days <= 180 THEN '91-180 days'
        ELSE '180+ days'
    END as customer_age_group,
    COUNT(*) as customer_count,
    ROUND(AVG(order_count)::NUMERIC, 2) as avg_orders_per_customer,
    ROUND(AVG(lifetime_value)::NUMERIC, 2) as avg_lifetime_value,
    ROUND(AVG(avg_order_value)::NUMERIC, 2) as avg_order_value
FROM customer_lifetime
GROUP BY customer_age_group
ORDER BY 
    CASE 
        WHEN customer_age_group = '0 days (single purchase)' THEN 1
        WHEN customer_age_group = '1-30 days' THEN 2
        WHEN customer_age_group = '31-90 days' THEN 3
        WHEN customer_age_group = '91-180 days' THEN 4
        ELSE 5
    END;

-- ============================================
-- QUERY 32: GEOGRAPHIC CONCENTRATION (BONUS)
-- ============================================

WITH state_revenue AS (
    SELECT 
        c.customer_state,
        ROUND(SUM(oi.price)::NUMERIC, 2) as state_revenue
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_state
),
total_revenue AS (
    SELECT SUM(state_revenue) as total FROM state_revenue
)
SELECT 
    sr.customer_state,
    sr.state_revenue,
    ROUND(100.0 * sr.state_revenue / tr.total, 2) as percentage_of_total,
    SUM(ROUND(100.0 * sr.state_revenue / tr.total, 2)) OVER (ORDER BY sr.state_revenue DESC) as cumulative_percentage
FROM state_revenue sr
CROSS JOIN total_revenue tr
ORDER BY sr.state_revenue DESC;