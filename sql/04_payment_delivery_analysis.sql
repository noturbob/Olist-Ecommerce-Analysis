-- ============================================
-- PAYMENT METHOD & DELIVERY PERFORMANCE
-- ============================================

-- ============================================
-- QUERY 16: PAYMENT METHOD ANALYSIS
-- ============================================

SELECT 
    op.payment_type,
    COUNT(DISTINCT op.order_id) as total_orders,
    ROUND(100.0 * COUNT(DISTINCT op.order_id) / SUM(COUNT(DISTINCT op.order_id)) OVER (), 2) as percentage_orders,
    ROUND(SUM(op.payment_value)::NUMERIC, 2) as total_payment_value,
    ROUND(AVG(op.payment_value)::NUMERIC, 2) as avg_payment_value,
    ROUND(AVG(op.payment_installments)::NUMERIC, 2) as avg_installments
FROM order_payments op
JOIN orders o ON op.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY op.payment_type
ORDER BY total_orders DESC;

-- ============================================
-- QUERY 17: PAYMENT INSTALLMENTS DISTRIBUTION
-- ============================================

SELECT 
    CASE 
        WHEN payment_installments = 1 THEN '1 (No installment)'
        WHEN payment_installments BETWEEN 2 AND 3 THEN '2-3 installments'
        WHEN payment_installments BETWEEN 4 AND 6 THEN '4-6 installments'
        WHEN payment_installments BETWEEN 7 AND 10 THEN '7-10 installments'
        ELSE '10+ installments'
    END as installment_group,
    COUNT(DISTINCT order_id) as orders,
    ROUND(AVG(payment_value)::NUMERIC, 2) as avg_payment_value,
    ROUND(SUM(payment_value)::NUMERIC, 2) as total_value
FROM order_payments
WHERE payment_type = 'credit_card'
GROUP BY installment_group
ORDER BY 
    CASE 
        WHEN installment_group = '1 (No installment)' THEN 1
        WHEN installment_group = '2-3 installments' THEN 2
        WHEN installment_group = '4-6 installments' THEN 3
        WHEN installment_group = '7-10 installments' THEN 4
        ELSE 5
    END;

-- ============================================
-- QUERY 18: PAYMENT METHOD BY STATE
-- ============================================

SELECT 
    c.customer_state,
    op.payment_type,
    COUNT(DISTINCT op.order_id) as orders,
    ROUND(SUM(op.payment_value)::NUMERIC, 2) as total_value
FROM order_payments op
JOIN orders o ON op.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state, op.payment_type
ORDER BY c.customer_state, orders DESC;

-- ============================================
-- QUERY 19: DELIVERY PERFORMANCE OVERVIEW
-- ============================================

SELECT 
    COUNT(*) as total_delivered_orders,
    ROUND(AVG(actual_delivery_days)::NUMERIC, 2) as avg_actual_delivery_days,
    ROUND(AVG(estimated_delivery_days)::NUMERIC, 2) as avg_estimated_delivery_days,
    ROUND(AVG(delivery_delay_days)::NUMERIC, 2) as avg_delay_days,
    SUM(CASE WHEN on_time_delivery THEN 1 ELSE 0 END) as on_time_orders,
    ROUND(100.0 * SUM(CASE WHEN on_time_delivery THEN 1 ELSE 0 END) / COUNT(*), 2) as on_time_percentage,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY actual_delivery_days) as median_delivery_days,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY actual_delivery_days) as p95_delivery_days
FROM orders
WHERE order_status = 'delivered'
  AND actual_delivery_days IS NOT NULL;

-- ============================================
-- QUERY 20: DELIVERY PERFORMANCE BY STATE
-- ============================================

SELECT 
    c.customer_state,
    COUNT(*) as total_orders,
    ROUND(AVG(o.actual_delivery_days)::NUMERIC, 2) as avg_delivery_days,
    ROUND(AVG(o.delivery_delay_days)::NUMERIC, 2) as avg_delay_days,
    SUM(CASE WHEN o.on_time_delivery THEN 1 ELSE 0 END) as on_time_orders,
    ROUND(100.0 * SUM(CASE WHEN o.on_time_delivery THEN 1 ELSE 0 END) / COUNT(*), 2) as on_time_percentage
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
  AND o.actual_delivery_days IS NOT NULL
GROUP BY c.customer_state
HAVING COUNT(*) >= 10
ORDER BY avg_delivery_days DESC;

-- ============================================
-- QUERY 21: DELAYED ORDERS ANALYSIS
-- ============================================

WITH delayed_orders AS (
    SELECT 
        o.*,
        c.customer_state,
        c.customer_city
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
      AND o.on_time_delivery = FALSE
      AND o.delivery_delay_days > 0
)
SELECT 
    customer_state,
    COUNT(*) as delayed_orders,
    ROUND(AVG(delivery_delay_days)::NUMERIC, 2) as avg_delay_days,
    MAX(delivery_delay_days) as max_delay_days,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY delivery_delay_days) as median_delay_days
FROM delayed_orders
GROUP BY customer_state
HAVING COUNT(*) >= 5
ORDER BY delayed_orders DESC
LIMIT 10;

-- ============================================
-- QUERY 22: DELIVERY TIME BY DISTANCE (Using Seller Location)
-- ============================================

WITH order_distances AS (
    SELECT 
        o.order_id,
        o.actual_delivery_days,
        c.customer_state,
        s.seller_state,
        CASE 
            WHEN c.customer_state = s.seller_state THEN 'Same State'
            ELSE 'Different State'
        END as delivery_type
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN sellers s ON oi.seller_id = s.seller_id
    WHERE o.order_status = 'delivered'
      AND o.actual_delivery_days IS NOT NULL
)
SELECT 
    delivery_type,
    COUNT(*) as total_orders,
    ROUND(AVG(actual_delivery_days)::NUMERIC, 2) as avg_delivery_days,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY actual_delivery_days) as median_delivery_days,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY actual_delivery_days) as p95_delivery_days
FROM order_distances
GROUP BY delivery_type;