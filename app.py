import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('seaborn-v0_8')

st.set_page_config(page_title='E-commerce Ops Dashboard', layout='wide')

st.title("E-commerce Operations Dashboard by team 'Machine not Learning'")
st.caption('For the E-commerce Operations Manager. Supports: adjusting category discount caps and flagging high-return SKUs.')
st.caption('Data: 2023-01-01 — 2023-12-22 (course snapshot; Dec incomplete). Production refresh: nightly; reviewed weekly (daily in Nov–Dec).')

@st.cache_data
def load_data():
    df = pd.read_csv('ecommerce_orders_dataset.csv', parse_dates=['Order_Date'])
    df['is_returned'] = (df['Returned'] == 'Yes').astype(int)
    df['disc_bin'] = pd.cut(
        df['Discount_Percent'],
        [-1, 0, 10, 20, 30, 100],
        labels=['0%', '1-10%', '11-20%', '21-30%', '>30%']
    )
    return df

df = load_data()

category_filter = st.sidebar.multiselect(
    'Product Category',
    sorted(df.Product_Category.unique()),
    sorted(df.Product_Category.unique())
)

form = st.sidebar.form('holiday_form')
holiday_filter = form.selectbox('Holiday Season', ['ALL', 'Yes', 'No'], 0)
form.form_submit_button('Apply')

df = df[df.Product_Category.isin(category_filter)]
if holiday_filter != 'ALL':
    df = df[df.Holiday_Season == holiday_filter]

c1, c2, c3 = st.columns(3)
c1.metric('Total Sales', f"${df.Order_Amount.sum():,.0f}")
c2.metric('Return Rate', f"{df.is_returned.mean()*100:.1f}%")
c3.metric('Avg Profit Margin', f"{df.Profit_Margin_Percent.mean():.1f}%")
st.caption('Note: CLV / profit-margin fields contain capped values (50000 / 3%). Return rate uses the Returned flag.')

st.subheader('Monthly Sales and Return Rate')
monthly = (df.groupby(df.Order_Date.dt.to_period('M').astype(str))
             .agg(sales=('Order_Amount', 'sum'), return_rate=('is_returned', 'mean')))

fig, ax1 = plt.subplots(figsize=(20, 5))
ax1.bar(monthly.index, monthly.sales, color='#1f77b4', alpha=0.7, label='Sales')
ax1.set_ylabel('Sales ($)')
ax2 = ax1.twinx()
ax2.plot(monthly.index, monthly.return_rate, color='#d62728', marker='o', label='Return rate')
ax2.set_ylabel('Return rate')
ax1.set_title('Monthly Sales and Return Rate')
fig.autofmt_xdate()
st.pyplot(fig)
st.caption('December is incomplete in the snapshot — read the last bar with care.')

st.subheader('Return Rate and Profit Margin by Discount Band')
disc = df.groupby('disc_bin', observed=True).agg(
    return_rate=('is_returned', 'mean'),
    margin=('Profit_Margin_Percent', 'mean')
)

fig2, axes = plt.subplots(1, 2, figsize=(20, 5))
axes[0].bar(disc.index.astype(str), disc.return_rate, color='#d62728')
axes[0].set_title('Return Rate by Discount Band')
axes[0].set_ylabel('Return rate')

axes[1].bar(disc.index.astype(str), disc.margin, color='#2ca02c')
axes[1].set_title('Avg Profit Margin by Discount Band')
axes[1].set_ylabel('Profit margin (%)')

st.pyplot(fig2)

st.subheader('Order Details (first 500 rows)')
st.write(df[['Order_ID', 'Order_Date', 'Product_Category', 'Brand',
             'Order_Amount', 'Discount_Percent', 'Returned',
             'Profit_Amount', 'Review_Rating']].head(500))