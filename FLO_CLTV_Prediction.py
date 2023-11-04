##############################################################
# CLTV Prediction with BG-NBD and Gamma-Gamma
##############################################################

###############################################################
# Preparing the Data
###############################################################

import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
from lifetimes.plotting import plot_period_transactions
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter

pd.set_option("display.max_columns", None)
pd.set_option("display.float_format", lambda x: "%.4f" % x)

df_ = pd.read_csv("flo_data_20k.csv")
df = df_.copy()


# 2. Define the outlier_thresholds and replace_with_thresholds functions to suppress outliers.
# Note: When calculating cltv, the frequency values must be integers, so we should round the lower and upper limits with round().
def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquantile_range = quartile3 - quartile1
    up_limit = round(quartile3 + 1.5 * interquantile_range)
    low_limit = round(quartile1 - 1.5 * interquantile_range)
    return low_limit, up_limit


def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit


# replace_with_thresholds(df, "order_num_total_ever_online")
# replace_with_thresholds(df, "order_num_total_ever_offline")
# replace_with_thresholds(df, "customer_value_total_ever_offline")
# replace_with_thresholds(df, "customer_value_total_ever_online")

cols_to_supress = [
    "order_num_total_ever_online",
    "order_num_total_ever_offline",
    "customer_value_total_ever_offline",
    "customer_value_total_ever_online",
]

for col in cols_to_supress:
    replace_with_thresholds(df, col)


# Omnichannel means that customers shop both online and offline. Let's create new variables for each customer's total number of purchases and spend.

df["order_total_ever"] = (
    df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
)

df["value_total_ever"] = (
    df["customer_value_total_ever_online"] + df["customer_value_total_ever_offline"]
)

# df.head()

# Let's examine variable types and change the type of variables that express dates to date.

# df.info()
date_variables = [
    "first_order_date",
    "last_order_date",
    "last_order_date_online",
    "last_order_date_offline",
]

df[date_variables] = df[date_variables].apply(pd.to_datetime)

###############################################################
# Creating CLTV Data Structure
###############################################################

# Taking 2 days after the date of the last purchase in the dataset as the analysis date.

# df["last_order_date"].max()
today_date = pd.Timestamp(dt.date(2021, 6, 1))

# Creating a new cltv dataframe with customer_id, recency_cltv_weekly, T_weekly, frequency and monetary_cltv_avg.

df["recency_dates"] = (df["last_order_date"] - df["first_order_date"]).dt.days
df["recency_dates"]
cltv_df = df.groupby("master_id").agg(
    {
        "recency_dates": lambda x: x / 7,
        "first_order_date": lambda x: ((today_date - x).dt.days) / 7,
        "order_total_ever": "sum",
        "value_total_ever": "sum",
    }
)

cltv_df.columns = ["recency_cltv_weekly", "T_weekly", "frequency", "monetary_cltv_avg"]
cltv_df["monetary_cltv_avg"] = cltv_df["monetary_cltv_avg"] / cltv_df["frequency"]
cltv_df = cltv_df[cltv_df["frequency"] > 1]


###############################################################
# Building of BG/NBD, Gamma-Gamma Models and calculation of 6-month CLTV
###############################################################

# BG/NBD model.
bgf = BetaGeoFitter(penalizer_coef=0.001)
bgf.fit(cltv_df["frequency"], cltv_df["recency_cltv_weekly"], cltv_df["T_weekly"])


# In 3 months, let's estimate the expected purchases from customers and add them to the cltv dataframe as exp_sales_3_month.

cltv_df["exp_sales_3_month"] = bgf.predict(
    12, cltv_df["frequency"], cltv_df["recency_cltv_weekly"], cltv_df["T_weekly"]
)


# In 6 months, let's estimate the expected purchases from customers and add them to the cltv dataframe as exp_sales_6_month.
cltv_df["exp_sales_6_month"] = bgf.predict(
    24, cltv_df["frequency"], cltv_df["recency_cltv_weekly"], cltv_df["T_weekly"]
)

# Let's take a look at the top 10 buyers in the 3rd and 6th months.
cltv_df["exp_sales_3_month"].sort_values(ascending=False).head(10)
cltv_df["exp_sales_6_month"].sort_values(ascending=False).head(10)
plot_period_transactions(bgf)
plt.show()

# Let's fit the Gamma-Gamma model and estimate the average value that we will earn from customers and add it to the cltv dataframe as exp_average_value.
ggf = GammaGammaFitter(penalizer_coef=0.01)
ggf.fit(cltv_df["frequency"], cltv_df["monetary_cltv_avg"])

cltv_df["exp_average_value"] = ggf.conditional_expected_average_profit(
    cltv_df["frequency"], cltv_df["monetary_cltv_avg"]
)

# Calculate 6 months CLTV and add it to the dataframe as cltv.


cltv_df["cltv"] = ggf.customer_lifetime_value(
    bgf,
    cltv_df["frequency"],
    cltv_df["recency_cltv_weekly"],
    cltv_df["T_weekly"],
    cltv_df["monetary_cltv_avg"],
    time=6,
    freq="W",
    discount_rate=0.01,
)


# The 20 people with the highest CLTV.
cltv_df["cltv"].sort_values(ascending=False).head(20)

###############################################################
# Creation of Segments According to CLTV
###############################################################

# According to the 6-month CLTV, let's divide all your customers into 4 groups (segments) and add the group names to the data set.

cltv_df["cltv_segment"] = pd.qcut(cltv_df["cltv"], 4, labels=["D", "C", "B", "A"])

# Examine the recency, frequnecy and monetary averages of the segments.
cltv_df.groupby("cltv_segment").agg({"count", "mean"})
cltv_df.describe().T
