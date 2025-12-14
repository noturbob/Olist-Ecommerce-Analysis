# POWER BI QUICK START CHECKLIST

**Goal:** Build a professional e-commerce analytics dashboard in 2-3 hours
**Status:** Ready to Go!

---

## PRE-SETUP CHECKLIST

- [ ] Download Power BI Desktop (https://powerbi.microsoft.com/desktop/)
- [ ] Install Power BI Desktop on your computer
- [ ] Launch Power BI Desktop
- [ ] Have all CSV files ready from: `sql_results/` folder

---

## STEP 1: DATA IMPORT (15 mins)

### Import CSVs
- [ ] File → Get Data → Text/CSV
- [ ] Navigate to: `sql_results/` folder
- [ ] Select and import these files:
  - [ ] 01_business_summary.csv
  - [ ] 02_revenue_by_state.csv
  - [ ] 03_revenue_by_city.csv
  - [ ] 04_payment_methods.csv
  - [ ] 05_top_categories.csv
  - [ ] 06_delivery_analysis.csv
  - [ ] 08_order_status.csv
  - [ ] 09_top_sellers.csv
  - [ ] 10_delivery_feature_importance.csv
  - [ ] 11_review_feature_importance.csv
  - [ ] 12_customer_segmentation.csv

### Data Type Verification
- [ ] Format currency columns as Currency (BRL)
- [ ] Format percentage columns as Percentage
- [ ] Format date columns as Date

---

## STEP 2: CREATE RELATIONSHIPS (10 mins)

In Model view:
- [ ] Create key relationships between tables (if needed)
- [ ] Verify no circular dependencies
- [ ] Check data types are correct

---

## STEP 3: BUILD PAGE 1 - EXECUTIVE OVERVIEW (20 mins)

**Page Title:** Executive Overview

### KPI Cards (Top of page)
- [ ] Total Revenue: `=SUM(business_summary[total_revenue])`
  - Format: Currency R$
  - Target: R$13.49M
  
- [ ] Total Orders: `=SUM(business_summary[total_orders])`
  - Format: Number
  - Target: 98,199

- [ ] Avg Order Value: `=SUM(business_summary[avg_order_value])`
  - Format: Currency R$
  - Target: R$120.38

- [ ] Avg Delivery Days: `=AVG(delivery_analysis[avg_delivery_days])`
  - Format: Decimal (2 places)
  - Target: 12.56 days
  - Source: 06_delivery_analysis.csv

- [ ] Delivered Orders: `=SUM(delivery_analysis[delivered_orders])`
  - Format: Whole Number
  - Source: 06_delivery_analysis.csv

### Charts
- [ ] Monthly Trend (if data available)
  - Visual: Line chart
  - X-axis: Month
  - Y-axis: Revenue, Orders
  
- [ ] Top 10 States by Revenue
  - Visual: Horizontal bar chart
  - Data: 02_revenue_by_state.csv
  - Sort: Revenue descending
  
- [ ] Order Status Distribution
  - Visual: Pie chart
  - Data: 08_order_status.csv
  - Show: All statuses
  
- [ ] Payment Methods
  - Visual: Donut chart
  - Data: 04_payment_methods.csv
  - Show: Top 4 methods

---

## STEP 4: BUILD PAGE 2 - GEOGRAPHIC ANALYSIS (20 mins)

**Page Title:** Geographic Analysis

### Slicers
- [ ] State filter (dropdown)
- [ ] Date range filter (if applicable)

### Visualizations
- [ ] Top 15 States by Revenue
  - Visual: Horizontal bar chart
  - Source: 02_revenue_by_state.csv
  - Color: Blue gradient
  
- [ ] Top 20 Cities by Revenue
  - Visual: Horizontal bar chart
  - Source: 03_revenue_by_city.csv
  - Color: Blue gradient
  - Add: State column for context

- [ ] Revenue per Customer by State
  - Visual: Scatter chart
  - Show state name on hover

---

## STEP 5: BUILD PAGE 3 - PRODUCT ANALYTICS (20 mins)

**Page Title:** Product & Category Analysis

### Slicers
- [ ] Category filter (multi-select)
- [ ] Revenue range filter

### Visualizations
- [ ] Top 15 Categories by Revenue
  - Visual: Horizontal bar chart
  - Source: 05_top_categories.csv
  - Sort: Revenue descending
  - Color: Green gradient
  
- [ ] Category Count
  - Visual: Card
  - Value: Count of categories

- [ ] Average Price by Category
  - Visual: Scatter chart
  - X-axis: Category
  - Y-axis: Avg Price
  - Bubble size: Order count

---

## STEP 6: BUILD PAGE 4 - PAYMENT & DELIVERY (20 mins)

**Page Title:** Payment & Delivery Insights

### Top Slicers
- [ ] Payment Type filter
- [ ] State filter

### Visualizations
- [ ] Payment Method Distribution
  - Visual: Pie chart
  - Source: 04_payment_methods.csv
  - Show percentages
  
- [ ] Average Delivery Days (KPI)
  - Visual: Card
  - Value: 12.56 days
  - Color: Green (good performance)
  
- [ ] On-Time vs Late Orders
  - Visual: Stacked bar chart
  - If data available
  
- [ ] Delivery Performance by State
  - Visual: Table with Top N
  - Columns: State, Avg Days, On-Time %

---

## STEP 7: BUILD PAGE 5 - CUSTOMER SEGMENTS (25 mins)

**Page Title:** Customer Segmentation & RFM

### Key Metrics
- [ ] Total Customers (Card): 96,478
- [ ] Segments Count (Card): 4

### Visualizations
- [ ] Customer Distribution by Segment
  - Visual: Pie chart
  - Source: 12_customer_segmentation.csv
  - Colors: 
    - At Risk: Red
    - Loyal: Blue
    - Champions: Gold
    - Big Spenders: Green
  
- [ ] Customer Count by Segment
  - Visual: Bar chart
  - Sort: Count descending
  
- [ ] Segment Details Table
  - Visual: Table
  - Columns: 
    - Segment Name
    - Customer Count
    - Avg Recency Days
    - Avg Frequency
    - Avg Monetary Value
  - Source: 12_customer_segmentation.csv

- [ ] RFM Characteristics
  - Visual: Matrix/Table
  - Show segment breakdown

---

## STEP 8: BUILD PAGE 6 - ML INSIGHTS (20 mins)

**Page Title:** Predictive Analytics & ML Models

### Model 1: Delivery Delay Prediction
- [ ] Accuracy KPI Card: 92.16%
- [ ] ROC-AUC Card: 0.729
- [ ] Feature Importance Chart
  - Visual: Horizontal bar chart
  - Source: 10_delivery_feature_importance.csv
  - Top 8 features
  - Color: Orange gradient

### Model 2: Review Score Prediction
- [ ] R² Score Card: 0.2054
- [ ] RMSE Card: 1.15 stars
- [ ] Feature Importance Chart
  - Visual: Horizontal bar chart
  - Source: 11_review_feature_importance.csv
  - Top 8 features
  - Color: Purple gradient

### Key Insights (Text Box)
- [ ] Add 3-4 bullet points with main findings

---

## STEP 9: BUILD PAGE 7 - DATA REFERENCE (15 mins)

**Page Title:** Data Tables & Reference

### Tables for Drill-Down
- [ ] Top Sellers Table
  - Source: 09_top_sellers.csv
  - Columns: Seller ID, City, State, Orders, Revenue
  - Sort: Revenue descending
  
- [ ] All Customers Segmented
  - Source: 12_customer_segmentation.csv
  - Enable search functionality
  - Columns: ID, City, State, Segment, RFM Score

- [ ] Summary Statistics
  - Visual: Table
  - Show key metrics

---

## STEP 10: FORMATTING & POLISH (20 mins)

### Themes & Colors
- [ ] Apply consistent color scheme
  - Primary: #1f77b4 (Blue)
  - Secondary: #ff7f0e (Orange)
  - Success: #2ca02c (Green)
  - Alert: #d62728 (Red)

### Navigation
- [ ] Add buttons for page navigation
- [ ] Create table of contents on first page
- [ ] Add bookmarks for quick access

### Formatting
- [ ] Align visuals to grid
- [ ] Add consistent spacing
- [ ] Use professional fonts (Segoe UI or Calibri)
- [ ] Add page numbers

---

## STEP 11: INTERACTIVITY (15 mins)

### Slicers & Filters
- [ ] Ensure all slicers work across pages
- [ ] Enable multi-select where appropriate
- [ ] Test cross-filtering

### Tooltips
- [ ] Add custom tooltips to visuals
- [ ] Show additional context on hover
- [ ] Enable visual interactions

### Drill-Through
- [ ] Set up drill-through from State → City
- [ ] Set up drill-through from Category → Products
- [ ] Test navigation

---

## STEP 12: TESTING & VALIDATION (15 mins)

### Data Validation
- [ ] Verify all numbers match source CSV files
- [ ] Check for missing values
- [ ] Validate calculations
- [ ] Test filters and slicers

### Performance
- [ ] Check for slow-loading visuals
- [ ] Optimize large tables
- [ ] Test on different screen sizes

### Formatting
- [ ] Check for spelling errors
- [ ] Verify alignment and spacing
- [ ] Ensure colors are consistent
- [ ] Check readability

---

## STEP 13: SAVE & PUBLISH (10 mins)

### Save Locally
- [ ] File → Save As
- [ ] Name: `olist_ecommerce_dashboard.pbix`
- [ ] Location: `power bi/` folder

### Publish to Power BI Service (Optional)
- [ ] Home → Publish
- [ ] Select workspace
- [ ] Set refresh schedule (if live data)
- [ ] Share with team

---

## FINAL CHECKLIST

**Dashboard Completion:**
- [ ] 7 pages created
- [ ] All data imported
- [ ] All visuals formatted
- [ ] Slicers functional
- [ ] Tooltips added
- [ ] Colors consistent
- [ ] Performance optimized
- [ ] Saved locally
- [ ] Tested thoroughly

**Quality Assurance:**
- [ ] No #ERROR or #DIV/0! errors
- [ ] All fonts readable
- [ ] All colors visible
- [ ] Responsive on different screen sizes
- [ ] Drill-through working
- [ ] Cross-filtering working

**Documentation:**
- [ ] Dashboard title clear
- [ ] Page titles descriptive
- [ ] Metrics labeled
- [ ] Units specified (R$, %)
- [ ] Data sources noted

---

## ESTIMATED TIMELINE

| Activity | Time | Total |
|----------|------|-------|
| Data Import | 15 min | 15 min |
| Relationships | 10 min | 25 min |
| Page 1 (Overview) | 20 min | 45 min |
| Page 2 (Geographic) | 20 min | 65 min |
| Page 3 (Products) | 20 min | 85 min |
| Page 4 (Payment) | 20 min | 105 min |
| Page 5 (Segments) | 25 min | 130 min |
| Page 6 (ML) | 20 min | 150 min |
| Page 7 (Reference) | 15 min | 165 min |
| Formatting | 20 min | 185 min |
| Interactivity | 15 min | 200 min |
| Testing | 15 min | 215 min |
| Save & Publish | 10 min | 225 min |

**Total: ~3.5 hours for complete professional dashboard**

---

## TROUBLESHOOTING

**Problem:** Data not showing in visual
- **Solution:** Check data source, verify column names, check filters

**Problem:** Slow performance
- **Solution:** Limit rows displayed, use aggregations, optimize data model

**Problem:** Formatting doesn't look right
- **Solution:** Check data types, adjust column widths, verify sort order

**Problem:** Slicers not filtering correctly
- **Solution:** Check relationships, verify field names, test cross-page filtering

---

## RESOURCES

- Power BI Help: https://support.powerbi.com
- DAX Function Reference: https://dax.guide
- Power BI Community: https://community.powerbi.com
- YouTube Tutorial: "Power BI Beginners Tutorial"

---

**Good luck building your dashboard! 🎉**

Once complete, share with stakeholders and gather feedback for dashboard enhancements.
