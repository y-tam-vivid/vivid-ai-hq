# Looker Studio Troubleshooting Guide

Common issues encountered during dashboard construction and operation, with solutions.

---

## Table of Contents

1. [Data Source Connection Issues](#1-data-source-connection-issues)
2. [Display & Rendering Issues](#2-display--rendering-issues)
3. [Calculated Field Issues](#3-calculated-field-issues)
4. [Data Blending Issues](#4-data-blending-issues)
5. [Performance Issues](#5-performance-issues)
6. [Sharing & Permission Issues](#6-sharing--permission-issues)
7. [GA4-Specific Issues](#7-ga4-specific-issues)
8. [Google Sheets-Specific Issues](#8-google-sheets-specific-issues)

---

## 1. Data Source Connection Issues

### "Dataset configuration error" displayed
- **Cause**: Data source schema changed (columns added/removed/renamed)
- **Fix**: Open data source settings → click "Refresh Fields" → remap changed fields

### "Cannot connect" error on data source
- **Cause**: Insufficient sharing permissions on Google Sheets, or the sheet was deleted/moved
- **Fix**:
  1. Check Sheets sharing settings (ensure the Looker Studio service account has access)
  2. Try reconnecting the data source
  3. If the Sheets owner changed, reconnection is required

### Data not updating to latest values
- **Cause**: Looker Studio cache (default 15 min to 12 hours)
- **Fix**:
  1. Click the refresh button at the top-right of the report
  2. Reduce "Data Freshness" interval in data source settings (minimum 15 min)
  3. Note: shorter freshness degrades performance

---

## 2. Display & Rendering Issues

### "null" or blank values displayed in charts
- **Cause**: Blank cells or NULL values in data source
- **Fix**:
  1. Use `IFNULL(field_name, 0)` in calculated fields
  2. Fill blank cells with 0 or N/A in Google Sheets
  3. Add a filter to exclude NULL values

### Scorecard shows "No data"
- **Cause**: Date filter range excludes available data, or filter conditions match no rows
- **Fix**:
  1. Check the date range filter
  2. Relax other filter conditions
  3. Review default date range settings

### Number formatting incorrect (thousands separator, decimals)
- **Fix**: Chart style settings → explicitly set metric format (Number, Currency, Percentage, etc.)

### Table column widths misaligned
- **Fix**: Select table → Style → turn off "Auto column width" → manually set widths

---

## 3. Calculated Field Issues

### Calculated field returns an error
- **Common causes and fixes**:
  1. **Type mismatch**: Arithmetic on text field → use `CAST(field AS NUMBER)` for type conversion
  2. **Division by zero**: Use `CASE WHEN denominator = 0 THEN 0 ELSE numerator / denominator END`
  3. **Date format inconsistency**: Use `TODATE(date_field, "input_format", "output_format")` to standardize

### How to calculate month-over-month or year-over-year comparison
- **Fix**: Use the built-in "Comparison date range" chart feature rather than calculated fields — it is simpler and more accurate
- **How**: Chart settings → Comparison period → select "Previous period" or "Previous year"

### REGEX functions not working as expected
- **Fix**:
  1. Looker Studio uses RE2 syntax (back-references not supported)
  2. `REGEXP_MATCH` returns boolean (use for filters)
  3. `REGEXP_EXTRACT` extracts matching strings
  4. `REGEXP_REPLACE` replaces matched patterns

---

## 4. Data Blending Issues

### Data missing after blending
- **Cause**: LEFT JOIN means records without a matching key in the right table become NULL
- **Fix**:
  1. Standardize join key values across both tables (watch for spacing, case, formatting differences)
  2. Unify date format to YYYY-MM-DD
  3. If missing data is unacceptable, pre-merge using VLOOKUP in Sheets before blending

### Aggregated values incorrect after blending (inflated numbers)
- **Cause**: Join key granularity mismatch (1-to-many join causes duplication)
- **Fix**:
  1. Verify that join key granularity matches across sources
  2. Pre-aggregate data in Sheets before blending if necessary

### Cannot apply calculated fields on blended data
- **Fix**: Calculated fields for blended data must be created inside the blend configuration — they are separate from individual data source calculated fields

---

## 5. Performance Issues

### Dashboard loads slowly
- **Primary causes and solutions**:
  1. **Too many components**: Keep ≤15 elements per page; split into multiple pages
  2. **Too much data**: For Google Sheets with 10,000+ rows, consider BigQuery migration
  3. **Too many blends**: Minimize blend count; pre-merge in Sheets instead
  4. **REGEX calculated fields**: Major performance bottleneck — minimize usage
  5. **Heavy images**: Optimize file sizes for background/decorative images

### "Too many requests" error
- **Fix**: Triggered by rapid filter operations in short succession. Wait briefly, then reload.

---

## 6. Sharing & Permission Issues

### Shared user cannot view the report
- **Checklist**:
  1. Check report sharing settings (link sharing vs. email-based)
  2. **Data source credentials**: Verify "Owner's credentials" is selected (not "Viewer's credentials")
  3. Confirm the recipient is logged into their Google account
  4. Check if the organization's Google Workspace blocks external sharing

### "Viewer's credentials" vs "Owner's credentials"
- **Owner's credentials (recommended)**: Data fetched using the report creator's account — viewers need no access to data sources
- **Viewer's credentials**: Data fetched using the viewer's account — viewers must have data source access
- **Decision rule**: For client-shared dashboards, always use "Owner's credentials"

### User needs edit access but only has "View only"
- **Fix**: Explicitly add them as "Editor" in report sharing settings. Avoid using "Anyone with link can edit" — it creates accidental edit risk; use email-based sharing instead.

---

## 7. GA4-Specific Issues

### "(not set)" appearing extensively in GA4 data
- **Cause**: Incomplete GA4 data collection setup or missing event parameters
- **Fix**:
  1. Verify tracking in GA4 DebugView
  2. Check for unregistered custom dimensions/metrics
  3. Filter out "(not set)" as a temporary measure in reports

### GA4 data is sampled (approximated)
- **Cause**: Automatic sampling applied when processing large data volumes
- **Fix**:
  1. Narrow the date range
  2. Reduce the number of dimensions
  3. Use GA4 BigQuery Export for unsampled data access

### GA4 "Engagement rate" vs legacy UA "Bounce rate"
- GA4 bounce rate = 1 − engagement rate
- Engaged session = 10+ seconds, 2+ page views, or conversion event occurred
- Definition differs from legacy Universal Analytics — direct historical comparison is invalid

---

## 8. Google Sheets-Specific Issues

### Sheets data not reflected in report
- **Cause**: Looker Studio cache
- **Fix**:
  1. Click the report refresh button
  2. Check "Data Freshness" setting in data source config
  3. Verify Sheets formulas (IMPORTRANGE, etc.) are functioning correctly

### Dates not recognized correctly from Sheets
- **Fix**:
  1. Verify actual cell values (not just display format) are in YYYY-MM-DD format
  2. Change field type to "Date" in Looker Studio
  3. Use `TODATE()` function to explicitly specify format

### Numbers treated as text from Sheets
- **Fix**:
  1. Set column format to "Number" in Sheets
  2. If a green triangle appears at cell top-left, select "Convert to number"
  3. Change field type to "Number" in Looker Studio
  4. Use `CAST(field AS NUMBER)` in calculated fields as fallback
