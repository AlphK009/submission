import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
from babel.numbers import format_currency

sns.set(style='dark')
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)

    return daily_orders_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("order_id")["order_item_id"].count().reset_index()
    return sum_order_items_df

def create_by_customer_state_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bystate_df

def create_by_seller_state_df(df):
    by_seller_state_df = df.groupby(by="seller_state").seller_id.nunique().reset_index()
    by_seller_state_df.rename(columns={
        "seller_id": "seller_count"
    }, inplace=True)
    
    return by_seller_state_df

def create_review_score_df(df):
  by_review_score_df = df.groupby(by="review_score").customer_id.nunique().reset_index()
  by_review_score_df.rename(columns={
      "customer_id": "review_count"
  }, inplace=True)
  return by_review_score_df

def create_revenue_payment_type_df(df):
    revenue_payment_type_df = df.groupby("payment_type").agg({
        "payment_value": "sum"
    }).reset_index()
    revenue_payment_type_df.rename(columns={
        "payment_type": "payment_type",
        "payment_value": "revenue"
    }, inplace=True)
    return revenue_payment_type_df
def create_payment_type_df(df):
    payment_type_df = df.groupby("payment_type")["customer_id"].nunique().reset_index()
    payment_type_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    return payment_type_df
def create_order_df(df):
    byorder_df = df.groupby("order_status")["order_id"].nunique().reset_index()
    byorder_df.rename(columns={"order_id": "order_count"}, inplace=True)
    return byorder_df
                          
def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max", #mengambil tanggal order terakhir
        "order_id": "nunique",
        "payment_value": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df['recency'] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df

all_df = pd.read_csv("https://raw.githubusercontent.com/AlphK009/submission/main/dashboard/all_data.csv")

datetime_columns = ["order_purchase_timestamp", "order_delivered_carrier_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

datetime_columns = ["order_purchase_timestamp", "order_delivered_carrier_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    # st.image("")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) &
                 (all_df["order_purchase_timestamp"] <= str(end_date))]

daily_orders_df =  create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
payment_type_df = create_payment_type_df(main_df)
bystate_df = create_by_customer_state_df(main_df)
by_seller_state_df = create_by_seller_state_df(main_df)
by_review_score_df = create_review_score_df(main_df)
bypayment_df = create_revenue_payment_type_df(main_df)
byorder_df = create_order_df(main_df)
by_payment_type_df = create_revenue_payment_type_df(main_df)
rfm_df = create_rfm_df(main_df)


rfm_df = create_rfm_df(main_df)

st.header('Dicoding E-Commerce')
st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value = total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "BRL", locale='pt_BR')

    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))

ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)

ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.subheader("Customer and Seller Demographics")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    colors = ["#90CAF9"]
    sns.barplot(
    x="customer_count",
    y="customer_state",
    data=bystate_df.sort_values(by="customer_count", ascending=False),
    palette=colors,
    ax=ax
    )
    ax.set_title("Number of Customer by States", loc="center", fontsize=30)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
    st.pyplot(fig)
with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    colors = ["#90CAF9"]
    sns.barplot(
    x="seller_count",
    y="seller_state",
    data=by_seller_state_df.sort_values(by="seller_count", ascending=False),
    palette=colors,
    ax=ax
    )
    ax.set_title("Number of Seller by States", loc="center", fontsize=30)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
    st.pyplot(fig)

st.subheader("Customer given review Score")

fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9"]
sns.barplot(
    x="review_score",
    y="review_count",
    data=by_review_score_df.sort_values(by="review_count", ascending=False),
    palette=colors,
    ax=ax
)
ax.set_title("Number of Review score given by Customer", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

st.subheader("Revenue based Payment Type")

fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9"]
sns.barplot(
    x="payment_type",
    y="revenue",
    data=bypayment_df.sort_values(by="revenue", ascending=False),
    palette=colors,
    ax=ax
)
ax.set_title("Revenue by Payment Type", loc="center", fontsize=30)
ax.set_ylabel("Revenue", fontsize=20)  
ax.set_xlabel("Payment Type", fontsize=20)  
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)  

st.pyplot(fig)

st.subheader("Payment Method")
col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots()
    payment_type_df.groupby(['payment_type'])['customer_count'].sum().plot(
        kind='pie', 
        title="Number of Payment used by Customers",
        autopct='%1.0f%%',
        shadow=False,
        ax=ax 
    )
    st.pyplot(fig)


with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    colors = ["#90CAF9"]
    sns.barplot(
        x="payment_type",
        y="customer_count",
        data=payment_type_df.sort_values(by="customer_count", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Payment used by Customers", loc="center", fontsize=30)
    ax.tick_params(axis='y', labelsize=15)
    ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

st.subheader("Order Status")

fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9"]
sns.barplot(
    x="order_status",
    y="order_count",
    data=byorder_df.sort_values(by="order_count", ascending=False),
    palette=colors,
    ax=ax
    )
ax.set_title("Number of Payment used by Customers", loc="center", fontsize=30)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value = avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value = avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), 'BRL', locale='pt_BR')
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors=["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(
    y="recency", 
    x="customer_id", 
    data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0]
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency(days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(
    y="frequency", 
    x="customer_id", 
    data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1]
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
 
st.pyplot(fig)
