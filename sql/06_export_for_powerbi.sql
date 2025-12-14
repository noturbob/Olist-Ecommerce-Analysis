-- ============================================
-- EXPORT KEY VIEWS FOR POWER BI DASHBOARD
-- ============================================

-- These views provide clean, aggregated data that Power BI can connect to directly

-- ============================================
-- VIEW 1: Orders with Full Details
-- ============================================

CREATE OR REPLACE VIEW vw_orders_full AS
SELECT 
    o.order_id,
    o.customer_id,
    c.customer_city,
    c.customer_state,
    c.customer_zip_code_prefix,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_date,
    o.order_month,
    o.order_year,
    o.order_quarter,
    o.order_dayofweek,
    o.order_hour,
    o.actual_delivery_days,
    o.estimated_delivery_days,
    o.delivery_delay_days,
    o.on_time_delivery,
    COALESCE(SUM(oi.price), 0) as order_value,
    COALESCE(SUM(oi.freight_value), 0) as freight_value,
    COALESCE(COUNT(oi.order_item_id), 0) as item_count
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY 
    o.order_id, o.customer_id, c.customer_city, c.customer_state, 
    c.customer_zip_code_prefix, o.order_status, o.order_purchase_timestamp,
    o.order_date, o.order_month, o.order_year, o.order_quarter,
    o.order_dayofweek, o.order_hour, o.actual_delivery_days,
    o.estimated_delivery_days, o.delivery_delay_days, o.on_time_delivery;

-- ============================================
-- VIEW 2: Product Performance Summary
-- ============================================

CREATE OR REPLACE VIEW vw_product_performance AS
SELECT 
    p.product_id,
    p.product_category_name_english as category,
    COUNT(DISTINCT oi.order_id) as times_sold,
    ROUND(COALESCE(SUM(oi.price), 0)::NUMERIC, 2) as total_revenue,
    ROUND(COALESCE(AVG(oi.price), 0)::NUMERIC, 2) as avg_price,
    ROUND(AVG(r.review_score)::NUMERIC, 2) as avg_review
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status = 'delivered'
LEFT JOIN order_reviews r ON o.order_id = r.order_id
GROUP BY p.product_id, p.product_category_name_english;

-- ============================================
-- VIEW 3: Seller Performance Summary
-- ============================================

CREATE OR REPLACE VIEW vw_seller_performance AS
SELECT 
    s.seller_id,
    s.seller_city,
    s.seller_state,
    COUNT(DISTINCT oi.order_id) as total_orders,
    ROUND(COALESCE(SUM(oi.price), 0)::NUMERIC, 2) as total_revenue,
    ROUND(AVG(r.review_score)::NUMERIC, 2) as avg_review
FROM sellers s
LEFT JOIN order_items oi ON s.seller_id = oi.seller_id
LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status = 'delivered'
LEFT JOIN order_reviews r ON o.order_id = r.order_id
GROUP BY s.seller_id, s.seller_city, s.seller_state;

-- ============================================
-- VIEW 4: Daily Revenue Summary
-- ============================================

CREATE OR REPLACE VIEW vw_daily_revenue AS
SELECT 
    o.order_date,
    o.order_year,
    o.order_month,
    o.order_quarter,
    COUNT(DISTINCT o.order_id) as daily_orders,
    ROUND(SUM(oi.price)::NUMERIC, 2) as daily_revenue,
    ROUND(AVG(oi.price)::NUMERIC, 2) as avg_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY o.order_date, o.order_year, o.order_month, o.order_quarter
ORDER BY o.order_date;

-- ============================================
-- VIEW 5: State Performance Summary
-- ============================================

CREATE OR REPLACE VIEW vw_state_performance AS
SELECT 
    c.customer_state,
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    ROUND(SUM(oi.price)::NUMERIC, 2) as total_revenue,
    ROUND(AVG(oi.price)::NUMERIC, 2) as avg_order_value,
    ROUND(AVG(o.delivery_delay_days)::NUMERIC, 2) as avg_delivery_delay,
    SUM(CASE WHEN o.on_time_delivery THEN 1 ELSE 0 END) as on_time_orders,
    ROUND(100.0 * SUM(CASE WHEN o.on_time_delivery THEN 1 ELSE 0 END) / COUNT(*), 2) as on_time_percentage
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state;

-- ============================================
-- VIEW 6: Category Performance Summary
-- ============================================

CREATE OR REPLACE VIEW vw_category_performance AS
SELECT 
    p.product_category_name_english as category,
    COUNT(DISTINCT oi.order_id) as total_orders,
    COUNT(DISTINCT p.product_id) as unique_products,
    ROUND(SUM(oi.price)::NUMERIC, 2) as total_revenue,
    ROUND(AVG(oi.price)::NUMERIC, 2) as avg_price,
    ROUND(AVG(r.review_score)::NUMERIC, 2) as avg_review_score
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN order_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
  AND p.product_category_name_english IS NOT NULL
  AND p.product_category_name_english != 'unknown'
GROUP BY p.product_category_name_english;

-- ============================================
-- VIEW 7: Payment Method Summary
-- ============================================

CREATE OR REPLACE VIEW vw_payment_summary AS
SELECT 
    op.payment_type,
    COUNT(DISTINCT op.order_id) as total_orders,
    ROUND(SUM(op.payment_value)::NUMERIC, 2) as total_value,
    ROUND(AVG(op.payment_value)::NUMERIC, 2) as avg_value,
    ROUND(AVG(op.payment_installments)::NUMERIC, 2) as avg_installments
FROM order_payments op
JOIN orders o ON op.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY op.payment_type;

-- ============================================
-- VIEW 8: Customer Segments
-- ============================================

CREATE OR REPLACE VIEW vw_customer_segments AS
WITH customer_metrics AS (
    SELECT 
        o.customer_id,
        c.customer_state,
        COUNT(DISTINCT o.order_id) as total_orders,
        ROUND(SUM(oi.price)::NUMERIC, 2) as lifetime_value,
        MIN(o.order_purchase_timestamp)::DATE as first_purchase,
        MAX(o.order_purchase_timestamp)::DATE as last_purchase
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY o.customer_id, c.customer_state
)
SELECT 
    customer_id,
    customer_state,
    total_orders,
    lifetime_value,
    first_purchase,
    last_purchase,
    CASE 
        WHEN total_orders = 1 THEN 'One-time'
        WHEN total_orders = 2 THEN 'Repeat'
        ELSE 'Loyal'
    END as segment
FROM customer_metrics;

-- ============================================
-- GRANT PERMISSIONS (if needed for Power BI user)
-- ============================================

-- Uncomment and modify if you have a specific Power BI user
-- GRANT SELECT ON vw_orders_full TO powerbi_user;
-- GRANT SELECT ON vw_product_performance TO powerbi_user;
-- GRANT SELECT ON vw_seller_performance TO powerbi_user;
-- GRANT SELECT ON vw_daily_revenue TO powerbi_user;
-- GRANT SELECT ON vw_state_performance TO powerbi_user;
-- GRANT SELECT ON vw_category_performance TO powerbi_user;
-- GRANT SELECT ON vw_payment_summary TO powerbi_user;
-- GRANT SELECT ON vw_customer_segments TO powerbi_user;