# CLTV Prediction with BG-NBD and Gamma-Gamma

This project focuses on predicting Customer Lifetime Value (CLTV) using the BG-NBD and Gamma-Gamma models. CLTV is a key metric that estimates the expected future value of a customer over a specific time period. By understanding CLTV, businesses can make informed decisions regarding customer acquisition, retention, and marketing strategies.

## Preparing the Data

- The project uses data from the `flo_data_20k.csv` dataset.
- Outliers in specific variables are suppressed using threshold values to ensure data quality.
- A new dataset is created for customers who shop both online and offline.

## Creating CLTV Data Structure

- CLTV is calculated based on Recency, Frequency, and Monetary (RFM) metrics.
- Recency is calculated as the time between the last purchase date and a reference date.
- Frequency represents the total number of purchases.
- Monetary CLTV Average is calculated by dividing the total monetary value by the frequency.

## Building of BG/NBD and Gamma-Gamma Models

- The BG-NBD (Beta Geo Fitter) model is used to estimate customer purchase behavior and predict expected purchases.
- The Gamma-Gamma model is applied to estimate the average value that will be earned from customers.

## Calculation of 6-Month CLTV

- The expected sales and average value are estimated for both 3 months and 6 months.
- The top buyers in the 3rd and 6th months are identified.
- Customer segments are created based on the 6-month CLTV.

## Segmentation According to CLTV

- Customers are divided into four segments (D, C, B, A) based on their 6-month CLTV.
- The project examines the recency, frequency, and monetary averages of these segments.

## Data Dictionary

Here is a brief explanation of the dataset columns used in this project:

- `master_id`: Unique client number
- `order_channel`: Shopping platform channel used (Android, iOS, Desktop, Mobile)
- `last_order_channel`: The channel where the last purchase was made
- `first_order_date`: The date of the first purchase made by the customer
- `last_order_date`: The date of the customer's last purchase
- `last_order_date_online`: The date of the last online purchase
- `last_order_date_offline`: The date of the last offline purchase
- `order_num_total_ever_online`: Total number of online purchases
- `order_num_total_ever_offline`: Total number of offline purchases
- `customer_value_total_ever_offline`: Total price paid for offline purchases
- `customer_value_total_ever_online`: Total price paid for online shopping

## Conclusion

Predicting CLTV is a valuable tool for businesses to optimize their marketing and customer management strategies. By understanding customer lifetime value, companies can make data-driven decisions to enhance customer relationships and profitability.

For detailed insights, explore the project code and data files.
