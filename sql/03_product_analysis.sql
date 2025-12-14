-- ============================================
-- PRODUCT & CATEGORY PERFORMANCE ANALYSIS
-- ============================================

-- ============================================
-- QUERY 10: TOP 20 SELLING PRODUCTS
-- ============================================

SELECT 
    p.product_id,
    p.product_category_name_english as category,
    COUNT(DISTINCT oi.order_id) as times_sold,
    ROUND(SUM(oi.price)::NUMERIC, 2) as total_revenue,
    ROUND(AVG(oi.price)::NUMERIC, 2) as avg_price,
    ROUND(AVG(r.review_score)::NUMERIC, 2) as avg_review_score
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN order_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY p.product_id, p.product_category_name_english
ORDER BY total_revenue DESC
LIMIT 20;

-- ============================================
-- QUERY 11: TOP PRODUCT CATEGORIES
-- ============================================

SELECT 
    p.product_category_name_english as category,
    COUNT(DISTINCT oi.order_id) as total_orders,
    COUNT(DISTINCT p.product_id) as unique_products,
    ROUND(SUM(oi.price)::NUMERIC, 2) as total_revenue,
    ROUND(AVG(oi.price)::NUMERIC, 2) as avg_price,
    ROUND(SUM(oi.price) / COUNT(DISTINCT oi.order_id)::NUMERIC, 2) as revenue_per_order
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
  AND p.product_category_name_english IS NOT NULL
  AND p.product_category_name_english != 'unknown'
GROUP BY p.product_category_name_english
HAVING COUNT(DISTINCT oi.order_id) >= 10
ORDER BY total_revenue DESC;

-- ============================================
-- QUERY 12: CATEGORY REVENUE BY STATE
-- ============================================

SELECT 
    c.customer_state,
    p.product_category_name_english as category,
    COUNT(DISTINCT o.order_id) as orders,
    ROUND(SUM(oi.price)::NUMERIC, 2) as revenue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_status = 'delivered'
  AND p.product_category_name_english IS NOT NULL
  AND p.product_category_name_english != 'unknown'
GROUP BY c.customer_state, p.product_category_name_english
HAVING SUM(oi.price) > 1000  -- Categories with >1000 BRL revenue
ORDER BY c.customer_state, revenue DESC;

-- ============================================
-- QUERY 13: PRODUCT PRICE DISTRIBUTION BY CATEGORY
-- ============================================

SELECT 
    p.product_category_name_english as category,
    COUNT(*) as product_count,
    ROUND(MIN(oi.price)::NUMERIC, 2) as min_price,
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY oi.price)::NUMERIC, 2) as q1_price,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY oi.price)::NUMERIC, 2) as median_price,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY oi.price)::NUMERIC, 2) as q3_price,
    ROUND(MAX(oi.price)::NUMERIC, 2) as max_price,
    ROUND(AVG(oi.price)::NUMERIC, 2) as avg_price,
    ROUND(STDDEV(oi.price)::NUMERIC, 2) as stddev_price
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
WHERE p.product_category_name_english IS NOT NULL
  AND p.product_category_name_english != 'unknown'
GROUP BY p.product_category_name_english
HAVING COUNT(*) >= 50
ORDER BY avg_price DESC;

-- ============================================
-- QUERY 14: SEASONAL TRENDS BY CATEGORY
-- ============================================

SELECT 
    p.product_category_name_english as category,
    o.order_month,
    COUNT(DISTINCT o.order_id) as orders,
    ROUND(SUM(oi.price)::NUMERIC, 2) as revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_status = 'delivered'
  AND p.product_category_name_english IN (
      -- Get top 5 categories by revenue
      SELECT product_category_name_english
      FROM order_items oi2
      JOIN products p2 ON oi2.product_id = p2.product_id
      WHERE p2.product_category_name_english IS NOT NULL
      GROUP BY product_category_name_english
      ORDER BY SUM(oi2.price) DESC
      LIMIT 5
  )
GROUP BY p.product_category_name_english, o.order_month
ORDER BY p.product_category_name_english, o.order_month;

-- ============================================
-- QUERY 15: PRODUCT BUNDLE ANALYSIS (Market Basket)
-- ============================================

WITH product_pairs AS (
    SELECT 
        oi1.product_id as product_1,
        oi2.product_id as product_2,
        p1.product_category_name_english as category_1,
        p2.product_category_name_english as category_2,
        COUNT(*) as times_bought_together
    FROM order_items oi1
    JOIN order_items oi2 ON oi1.order_id = oi2.order_id 
        AND oi1.product_id < oi2.product_id  -- Avoid duplicates
    JOIN products p1 ON oi1.product_id = p1.product_id
    JOIN products p2 ON oi2.product_id = p2.product_id
    WHERE p1.product_category_name_english IS NOT NULL
      AND p2.product_category_name_english IS NOT NULL
    GROUP BY oi1.product_id, oi2.product_id, 
             p1.product_category_name_english, p2.product_category_name_english
    HAVING COUNT(*) >= 5
)
SELECT 
    category_1,
    category_2,
    SUM(times_bought_together) as total_co_purchases
FROM product_pairs
GROUP BY category_1, category_2
ORDER BY total_co_purchases DESC
LIMIT 20;