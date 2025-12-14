-- ============================================
-- OLIST E-COMMERCE DATABASE SCHEMA
-- ============================================

-- Drop existing tables (in correct order due to foreign keys)
DROP TABLE IF EXISTS order_reviews CASCADE;
DROP TABLE IF EXISTS order_payments CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS sellers CASCADE;
DROP TABLE IF EXISTS geolocation CASCADE;

-- ============================================
-- 1. CUSTOMERS TABLE
-- ============================================
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50),
    customer_zip_code_prefix INT,
    customer_city VARCHAR(100),
    customer_state VARCHAR(2)
);

-- ============================================
-- 2. SELLERS TABLE
-- ============================================
CREATE TABLE sellers (
    seller_id VARCHAR(50) PRIMARY KEY,
    seller_zip_code_prefix INT,
    seller_city VARCHAR(100),
    seller_state VARCHAR(2)
);

-- ============================================
-- 3. PRODUCTS TABLE
-- ============================================
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_category_name VARCHAR(100),
    product_category_name_english VARCHAR(100),
    product_name_length INT,
    product_description_length INT,
    product_photos_qty INT,
    product_weight_g INT,
    product_length_cm INT,
    product_height_cm INT,
    product_width_cm INT
);

-- ============================================
-- 4. ORDERS TABLE (MAIN)
-- ============================================
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES customers(customer_id),
    order_status VARCHAR(20),
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,
    order_date DATE,
    order_month VARCHAR(7),
    order_year INT,
    order_quarter INT,
    order_dayofweek INT,
    order_hour INT,
    actual_delivery_days INT,
    estimated_delivery_days INT,
    delivery_delay_days INT,
    on_time_delivery BOOLEAN
);

-- ============================================
-- 5. ORDER ITEMS TABLE
-- ============================================
CREATE TABLE order_items (
    order_id VARCHAR(50) REFERENCES orders(order_id),
    order_item_id INT,
    product_id VARCHAR(50) REFERENCES products(product_id),
    seller_id VARCHAR(50) REFERENCES sellers(seller_id),
    shipping_limit_date TIMESTAMP,
    price DECIMAL(10,2),
    freight_value DECIMAL(10,2),
    PRIMARY KEY (order_id, order_item_id)
);

-- ============================================
-- 6. ORDER PAYMENTS TABLE
-- ============================================
CREATE TABLE order_payments (
    order_id VARCHAR(50) REFERENCES orders(order_id),
    payment_sequential INT,
    payment_type VARCHAR(20),
    payment_installments INT,
    payment_value DECIMAL(10,2),
    PRIMARY KEY (order_id, payment_sequential)
);

-- ============================================
-- 7. ORDER REVIEWS TABLE
-- ============================================
CREATE TABLE order_reviews (
    review_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) REFERENCES orders(order_id),
    review_score INT CHECK (review_score BETWEEN 1 AND 5),
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP
);

-- ============================================
-- 8. GEOLOCATION TABLE
-- ============================================
CREATE TABLE geolocation (
    zip_code_prefix INT PRIMARY KEY,
    geolocation_lat DECIMAL(10,6),
    geolocation_lng DECIMAL(10,6),
    geolocation_city VARCHAR(100),
    geolocation_state VARCHAR(2)
);

-- ============================================
-- CREATE INDEXES FOR PERFORMANCE
-- ============================================

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_status ON orders(order_status);
CREATE INDEX idx_order_items_product ON order_items(product_id);
CREATE INDEX idx_order_items_seller ON order_items(seller_id);
CREATE INDEX idx_payments_type ON order_payments(payment_type);
CREATE INDEX idx_reviews_score ON order_reviews(review_score);