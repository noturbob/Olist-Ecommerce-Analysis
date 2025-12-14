import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve, mean_squared_error, r2_score, accuracy_score
from sklearn.cluster import KMeans
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

# Create database connection
engine = create_engine('sqlite:///data/olist_ecommerce.db')

print("=" * 80)
print("BUILDING MACHINE LEARNING MODELS")
print("=" * 80)

# ============================================
# 1. DELIVERY DELAY PREDICTION MODEL
# ============================================
print("\n\n" + "=" * 80)
print("[MODEL 1] DELIVERY DELAY PREDICTION")
print("=" * 80)

print("\nLoading delivery data...")

delivery_data = pd.read_sql("""
SELECT 
    o.order_id,
    o.order_purchase_timestamp,
    o.order_estimated_delivery_date,
    o.order_delivered_customer_date,
    c.customer_state,
    s.seller_state,
    oi.price,
    oi.freight_value,
    oi.product_id,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm,
    CAST((julianday(o.order_delivered_customer_date) - julianday(o.order_purchase_timestamp)) AS FLOAT) as actual_delivery_days,
    CAST((julianday(o.order_estimated_delivery_date) - julianday(o.order_purchase_timestamp)) AS FLOAT) as estimated_delivery_days
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN sellers s ON oi.seller_id = s.seller_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_estimated_delivery_date IS NOT NULL
""", engine)

print(f"[OK] Loaded {len(delivery_data):,} delivery records")

# Create target: is_delayed (1 if actual > estimated, 0 otherwise)
delivery_data['is_delayed'] = (delivery_data['actual_delivery_days'] > delivery_data['estimated_delivery_days']).astype(int)

print(f"   Delayed orders: {delivery_data['is_delayed'].sum():,} ({100*delivery_data['is_delayed'].mean():.1f}%)")
print(f"   On-time orders: {(1-delivery_data['is_delayed']).sum():,} ({100*(1-delivery_data['is_delayed'].mean()):.1f}%)")

# Feature engineering
delivery_data['days_until_delivery'] = delivery_data['estimated_delivery_days']
delivery_data['weight_per_price'] = delivery_data['product_weight_g'] / (delivery_data['price'] + 1)
delivery_data['volume'] = delivery_data['product_length_cm'] * delivery_data['product_height_cm'] * delivery_data['product_width_cm']
delivery_data['freight_ratio'] = delivery_data['freight_value'] / (delivery_data['price'] + 1)

# State matching
delivery_data['same_state'] = (delivery_data['customer_state'] == delivery_data['seller_state']).astype(int)

# Handle missing values
delivery_data['product_weight_g'].fillna(delivery_data['product_weight_g'].median(), inplace=True)
delivery_data['volume'].fillna(delivery_data['volume'].median(), inplace=True)

# Select features
delay_features = ['price', 'freight_value', 'days_until_delivery', 'product_weight_g', 
                  'volume', 'freight_ratio', 'weight_per_price', 'same_state']
X_delay = delivery_data[delay_features].copy()
y_delay = delivery_data['is_delayed'].copy()

# Encode categorical features
le_delay = LabelEncoder()
X_delay['same_state'] = le_delay.fit_transform(X_delay['same_state'])

# Remove any remaining NaNs
X_delay = X_delay.fillna(X_delay.mean())

print("\nTraining Delivery Delay Model...")

# Split data
X_train_delay, X_test_delay, y_train_delay, y_test_delay = train_test_split(
    X_delay, y_delay, test_size=0.2, random_state=42, stratify=y_delay
)

# Scale features
scaler_delay = StandardScaler()
X_train_delay_scaled = scaler_delay.fit_transform(X_train_delay)
X_test_delay_scaled = scaler_delay.transform(X_test_delay)

# Train Random Forest
rf_delay = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
rf_delay.fit(X_train_delay_scaled, y_train_delay)

# Train Gradient Boosting for comparison
gb_delay = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
gb_delay.fit(X_train_delay_scaled, y_train_delay)

# Predictions
y_pred_delay_rf = rf_delay.predict(X_test_delay_scaled)
y_pred_delay_gb = gb_delay.predict(X_test_delay_scaled)
y_pred_proba_delay = rf_delay.predict_proba(X_test_delay_scaled)[:, 1]

# Evaluation
print("\n[RESULTS] RANDOM FOREST:")
print(f"   Accuracy: {accuracy_score(y_test_delay, y_pred_delay_rf):.4f}")
print(f"   ROC-AUC: {roc_auc_score(y_test_delay, y_pred_proba_delay):.4f}")
print(f"\n   Classification Report:")
print(classification_report(y_test_delay, y_pred_delay_rf, target_names=['On-Time', 'Delayed']))

print("\n[RESULTS] GRADIENT BOOSTING:")
print(f"   Accuracy: {accuracy_score(y_test_delay, y_pred_delay_gb):.4f}")

# Feature importance
feature_importance_delay = pd.DataFrame({
    'feature': delay_features,
    'importance': rf_delay.feature_importances_
}).sort_values('importance', ascending=False)

print("\nKey Features:")
print(feature_importance_delay.to_string(index=False))

# Save results
feature_importance_delay.to_csv('sql_results/10_delivery_feature_importance.csv', index=False)

# ============================================
# 2. REVIEW SCORE PREDICTION MODEL
# ============================================
print("\n\n" + "=" * 80)
print("[MODEL 2] REVIEW SCORE PREDICTION")
print("=" * 80)

print("\nLoading review data...")

review_data = pd.read_sql("""
SELECT 
    r.review_score,
    o.order_purchase_timestamp,
    c.customer_state,
    oi.price,
    oi.freight_value,
    CAST((julianday(o.order_delivered_customer_date) - julianday(o.order_purchase_timestamp)) AS FLOAT) as delivery_days,
    CAST((julianday(o.order_estimated_delivery_date) - julianday(o.order_purchase_timestamp)) AS FLOAT) as estimated_days,
    p.product_category_name_english,
    COUNT(DISTINCT oi.product_id) as products_in_order
FROM order_reviews r
JOIN orders o ON r.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_status = 'delivered'
  AND r.review_score IS NOT NULL
GROUP BY r.review_id
""", engine)

print(f"[OK] Loaded {len(review_data):,} reviews")
print(f"   Average Score: {review_data['review_score'].mean():.2f}/5.0")
print(f"   Score Distribution:\n{review_data['review_score'].value_counts().sort_index()}")

# Feature engineering
review_data['is_delayed'] = (review_data['delivery_days'] > review_data['estimated_days']).astype(int)
review_data['delivery_efficiency'] = review_data['delivery_days'] / (review_data['estimated_days'] + 1)
review_data['freight_ratio'] = review_data['freight_value'] / (review_data['price'] + 1)
review_data['high_value_order'] = (review_data['price'] > review_data['price'].quantile(0.75)).astype(int)

# Handle missing values
review_data['product_category_name_english'].fillna('unknown', inplace=True)
review_data = review_data[review_data['product_category_name_english'] != 'unknown']

# Encode categorical features
le_category = LabelEncoder()
review_data['category_encoded'] = le_category.fit_transform(review_data['product_category_name_english'])

le_state = LabelEncoder()
review_data['state_encoded'] = le_state.fit_transform(review_data['customer_state'])

# Select features
review_features = ['price', 'freight_value', 'delivery_days', 'is_delayed', 
                   'delivery_efficiency', 'freight_ratio', 'high_value_order', 
                   'products_in_order', 'category_encoded', 'state_encoded']
X_review = review_data[review_features].copy()
y_review = review_data['review_score'].copy()

# Remove NaNs
X_review = X_review.fillna(X_review.mean())
valid_idx = y_review.notna()
X_review = X_review[valid_idx]
y_review = y_review[valid_idx]

print("\nTraining Review Score Model...")

# Split data
X_train_review, X_test_review, y_train_review, y_test_review = train_test_split(
    X_review, y_review, test_size=0.2, random_state=42
)

# Scale features
scaler_review = StandardScaler()
X_train_review_scaled = scaler_review.fit_transform(X_train_review)
X_test_review_scaled = scaler_review.transform(X_test_review)

# Train Random Forest Regressor
rf_review = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
rf_review.fit(X_train_review_scaled, y_train_review)

# Train Linear Regression for comparison
lr_review = LinearRegression()
lr_review.fit(X_train_review_scaled, y_train_review)

# Predictions
y_pred_review_rf = rf_review.predict(X_test_review_scaled)
y_pred_review_lr = lr_review.predict(X_test_review_scaled)

# Evaluation
r2_rf = r2_score(y_test_review, y_pred_review_rf)
rmse_rf = np.sqrt(mean_squared_error(y_test_review, y_pred_review_rf))
r2_lr = r2_score(y_test_review, y_pred_review_lr)
rmse_lr = np.sqrt(mean_squared_error(y_test_review, y_pred_review_lr))

print("\n[RESULTS] RANDOM FOREST:")
print(f"   R2 Score: {r2_rf:.4f}")
print(f"   RMSE: {rmse_rf:.4f} stars")

print("\n[RESULTS] LINEAR REGRESSION:")
print(f"   R2 Score: {r2_lr:.4f}")
print(f"   RMSE: {rmse_lr:.4f} stars")

# Feature importance
feature_importance_review = pd.DataFrame({
    'feature': review_features,
    'importance': rf_review.feature_importances_
}).sort_values('importance', ascending=False)

print("\nKey Features:")
print(feature_importance_review.to_string(index=False))

feature_importance_review.to_csv('sql_results/11_review_feature_importance.csv', index=False)

# ============================================
# 3. CUSTOMER SEGMENTATION (RFM + CLUSTERING)
# ============================================
print("\n\n" + "=" * 80)
print("[MODEL 3] CUSTOMER SEGMENTATION (RFM + CLUSTERING)")
print("=" * 80)

print("\nLoading customer data for RFM...")

customer_rfm = pd.read_sql("""
WITH customer_metrics AS (
    SELECT 
        o.customer_id,
        MAX(o.order_purchase_timestamp) as last_purchase,
        COUNT(DISTINCT o.order_id) as frequency,
        ROUND(SUM(oi.price), 2) as monetary,
        AVG(oi.price) as avg_order_value
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY o.customer_id
)
SELECT 
    customer_id,
    CAST((julianday('2018-10-17') - julianday(last_purchase)) AS INTEGER) as recency_days,
    frequency,
    monetary,
    avg_order_value
FROM customer_metrics
WHERE frequency >= 1
""", engine)

print(f"[OK] Loaded {len(customer_rfm):,} customers")
print(f"\nRFM Summary Statistics:")
print(customer_rfm[['recency_days', 'frequency', 'monetary']].describe())

# Create RFM scores
customer_rfm['r_score'] = pd.qcut(customer_rfm['recency_days'], q=4, labels=[4, 3, 2, 1], duplicates='drop')
customer_rfm['f_score'] = pd.qcut(customer_rfm['frequency'].rank(method='first'), q=4, labels=[1, 2, 3, 4], duplicates='drop')
customer_rfm['m_score'] = pd.qcut(customer_rfm['monetary'], q=4, labels=[1, 2, 3, 4], duplicates='drop')

customer_rfm['rfm_score'] = customer_rfm['r_score'].astype(int) + customer_rfm['f_score'].astype(int) + customer_rfm['m_score'].astype(int)

print(f"\nRFM Score Distribution:")
print(customer_rfm['rfm_score'].value_counts().sort_index())

# Prepare for clustering
X_cluster = customer_rfm[['recency_days', 'frequency', 'monetary']].copy()

# Normalize features
scaler_cluster = StandardScaler()
X_cluster_scaled = scaler_cluster.fit_transform(X_cluster)

# Find optimal number of clusters using elbow method
print("\nFinding optimal number of clusters...")
inertias = []
silhouette_scores = []
for k in range(2, 11):
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_cluster_scaled)
    inertias.append(kmeans.inertia_)
    print(f"   k={k}: Inertia={kmeans.inertia_:.2f}")

# Use k=4 based on typical business segmentation
optimal_k = 4
print(f"\n[OK] Using k={optimal_k} clusters")

kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
customer_rfm['segment'] = kmeans.fit_predict(X_cluster_scaled)

# Label segments based on characteristics
segment_analysis = customer_rfm.groupby('segment')[['recency_days', 'frequency', 'monetary']].mean()
print("\n[SEGMENT ANALYSIS]:")
print(segment_analysis)

# Assign labels
segment_labels = {
    0: 'At Risk',
    1: 'Loyal',
    2: 'Potential',
    3: 'New'
}

# More sophisticated labeling
segment_names = []
for seg in range(optimal_k):
    seg_data = segment_analysis.loc[seg]
    if seg_data['frequency'] >= segment_analysis['frequency'].median() and seg_data['monetary'] >= segment_analysis['monetary'].median():
        if seg_data['recency_days'] <= segment_analysis['recency_days'].median():
            segment_names.append('Champions')
        else:
            segment_names.append('Loyal Customers')
    elif seg_data['frequency'] <= segment_analysis['frequency'].median() and seg_data['recency_days'] >= segment_analysis['recency_days'].median():
        segment_names.append('At Risk')
    elif seg_data['frequency'] <= segment_analysis['frequency'].median() and seg_data['monetary'] >= segment_analysis['monetary'].median():
        segment_names.append('Big Spenders')
    else:
        segment_names.append('New/Potential')

# Create mapping
label_mapping = {i: name for i, name in enumerate(segment_names)}
customer_rfm['segment_name'] = customer_rfm['segment'].map(label_mapping)

print("\nCustomer Segments:")
print(customer_rfm['segment_name'].value_counts())

# Save segmentation results
segmentation_results = customer_rfm[['customer_id', 'recency_days', 'frequency', 'monetary', 
                                     'rfm_score', 'segment_name']].copy()
segmentation_results.to_csv('sql_results/12_customer_segmentation.csv', index=False)
print("\nSaved: sql_results/12_customer_segmentation.csv")

# ============================================
# 4. MODEL SUMMARY AND VISUALIZATIONS
# ============================================
print("\n\n" + "=" * 80)
print("CREATING MODEL VISUALIZATIONS")
print("=" * 80)

import os
os.makedirs('ml_models', exist_ok=True)

# 4a. Confusion Matrix for Delivery Delay
fig, ax = plt.subplots(figsize=(10, 8))
cm = confusion_matrix(y_test_delay, y_pred_delay_rf)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax, cbar_kws={'label': 'Count'})
ax.set_title('Delivery Delay Prediction - Confusion Matrix', fontsize=14, fontweight='bold')
ax.set_xlabel('Predicted')
ax.set_ylabel('Actual')
ax.set_xticklabels(['On-Time', 'Delayed'])
ax.set_yticklabels(['On-Time', 'Delayed'])
plt.tight_layout()
plt.savefig('ml_models/01_delivery_confusion_matrix.png', dpi=300, bbox_inches='tight')
plt.close()
print("[OK] Saved: ml_models/01_delivery_confusion_matrix.png")

# 4b. ROC Curve for Delivery Delay
fpr, tpr, _ = roc_curve(y_test_delay, y_pred_proba_delay)
fig, ax = plt.subplots(figsize=(10, 8))
ax.plot(fpr, tpr, label=f'ROC Curve (AUC = {roc_auc_score(y_test_delay, y_pred_proba_delay):.3f})', linewidth=2)
ax.plot([0, 1], [0, 1], 'k--', label='Random Classifier', linewidth=2)
ax.set_xlabel('False Positive Rate', fontsize=12)
ax.set_ylabel('True Positive Rate', fontsize=12)
ax.set_title('Delivery Delay - ROC Curve', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('ml_models/02_delivery_roc_curve.png', dpi=300, bbox_inches='tight')
plt.close()
print("[OK] Saved: ml_models/02_delivery_roc_curve.png")

# 4c. Feature Importance - Delivery Delay
fig, ax = plt.subplots(figsize=(12, 6))
top_features = feature_importance_delay.head(10)
sns.barplot(data=top_features, x='importance', y='feature', palette='viridis', ax=ax)
ax.set_title('Top 10 Features - Delivery Delay Prediction', fontsize=14, fontweight='bold')
ax.set_xlabel('Importance', fontsize=12)
plt.tight_layout()
plt.savefig('ml_models/03_delivery_feature_importance.png', dpi=300, bbox_inches='tight')
plt.close()
print("[OK] Saved: ml_models/03_delivery_feature_importance.png")

# 4d. Actual vs Predicted - Review Scores
fig, ax = plt.subplots(figsize=(10, 8))
ax.scatter(y_test_review, y_pred_review_rf, alpha=0.5, s=20)
ax.plot([1, 5], [1, 5], 'r--', linewidth=2, label='Perfect Prediction')
ax.set_xlabel('Actual Review Score', fontsize=12)
ax.set_ylabel('Predicted Review Score', fontsize=12)
ax.set_title(f'Review Score Prediction (R2 = {r2_rf:.3f})', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('ml_models/04_review_actual_vs_predicted.png', dpi=300, bbox_inches='tight')
plt.close()
print("[OK] Saved: ml_models/04_review_actual_vs_predicted.png")

# 4e. Feature Importance - Review Score
fig, ax = plt.subplots(figsize=(12, 6))
top_review_features = feature_importance_review.head(10)
sns.barplot(data=top_review_features, x='importance', y='feature', palette='coolwarm', ax=ax)
ax.set_title('Top 10 Features - Review Score Prediction', fontsize=14, fontweight='bold')
ax.set_xlabel('Importance', fontsize=12)
plt.tight_layout()
plt.savefig('ml_models/05_review_feature_importance.png', dpi=300, bbox_inches='tight')
plt.close()
print("[OK] Saved: ml_models/05_review_feature_importance.png")

# 4f. Customer Segmentation - RFM Distribution
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
segment_colors = {'Champions': '#FFD700', 'Loyal Customers': '#4169E1', 
                   'At Risk': '#FF6347', 'Big Spenders': '#32CD32', 'New/Potential': '#9370DB'}

# Recency
customer_rfm.boxplot(column='recency_days', by='segment_name', ax=axes[0, 0])
axes[0, 0].set_title('Recency Distribution by Segment')
axes[0, 0].set_xlabel('Segment')
axes[0, 0].set_ylabel('Days Since Last Purchase')

# Frequency
customer_rfm.boxplot(column='frequency', by='segment_name', ax=axes[0, 1])
axes[0, 1].set_title('Purchase Frequency by Segment')
axes[0, 1].set_xlabel('Segment')
axes[0, 1].set_ylabel('Number of Orders')

# Monetary
customer_rfm.boxplot(column='monetary', by='segment_name', ax=axes[1, 0])
axes[1, 0].set_title('Total Spend by Segment')
axes[1, 0].set_xlabel('Segment')
axes[1, 0].set_ylabel('Total Monetary Value (R$)')

# Segment counts
segment_counts = customer_rfm['segment_name'].value_counts()
axes[1, 1].bar(segment_counts.index, segment_counts.values, color='steelblue')
axes[1, 1].set_title('Customer Count by Segment')
axes[1, 1].set_xlabel('Segment')
axes[1, 1].set_ylabel('Number of Customers')
axes[1, 1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('ml_models/06_customer_segmentation.png', dpi=300, bbox_inches='tight')
plt.close()
print("[OK] Saved: ml_models/06_customer_segmentation.png")

# ============================================
# 5. MODEL SUMMARY REPORT
# ============================================
print("\n" + "=" * 80)
print("ML MODEL SUMMARY REPORT")
print("=" * 80)

summary_report = f"""
========== ML MODELS PERFORMANCE SUMMARY ==========

[1] DELIVERY DELAY PREDICTION
   Model: Random Forest Classifier
   Accuracy: {accuracy_score(y_test_delay, y_pred_delay_rf):.2%}
   ROC-AUC Score: {roc_auc_score(y_test_delay, y_pred_proba_delay):.3f}
   Top Feature: {feature_importance_delay.iloc[0]['feature']}
   Use Case: Identify orders likely to be delayed
   
[2] REVIEW SCORE PREDICTION
   Model: Random Forest Regressor
   R2 Score: {r2_rf:.4f}
   RMSE: {rmse_rf:.4f} stars
   Top Feature: {feature_importance_review.iloc[0]['feature']}
   Use Case: Predict customer satisfaction scores
   
[3] CUSTOMER SEGMENTATION
   Method: K-Means Clustering (RFM Analysis)
   Segments: {optimal_k}
   Top Segment: {customer_rfm['segment_name'].value_counts().index[0]}
   Customers Segmented: {len(customer_rfm):,}
   Use Case: Targeted marketing campaigns

Output Files Generated:
   - Predictions: sql_results/10_delivery_feature_importance.csv
   - Predictions: sql_results/11_review_feature_importance.csv
   - Predictions: sql_results/12_customer_segmentation.csv
   - Visualizations: ml_models/01_*.png through ml_models/06_*.png
"""

print(summary_report)

# Save summary report
with open('ml_models/MODEL_SUMMARY_REPORT.txt', 'w') as f:
    f.write(summary_report)

print("\n[COMPLETE] ML MODELS TRAINING FINISHED!")
print("Models saved to: ml_models/")
print("=" * 80)
