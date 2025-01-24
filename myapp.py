import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import altair as alt
import seaborn as sns
from PIL import Image


st.set_page_config(page_title = "Visualization Project",
                   page_icon = ":bar_chart:",
                   layout = "wide"
)

# Loading the dataset
@st.cache_data
def load_data():
  filepath = r"C:\Users\shish\OneDrive\Desktop\Project\Dataset\dataset.csv"
  
  data = pd.read_csv(filepath)

  return data

# Storing the dataframe in data
data =  load_data()

# Converting the dates into the pandas date format
data['Order Date'] = pd.to_datetime(data['Order Date'])
data['Ship Date'] = pd.to_datetime(data['Ship Date'])

# Extracting the years from the order date and ship date
order_year = data['Order Date'].dt.year
ship_year = data['Ship Date'].dt.year


# Sidefor Filters
st.sidebar.header("Apply Filters")

# Creating diferent filters
year = st.sidebar.multiselect(
      "Select the Year:",
      options = order_year.unique(),
      default = order_year.unique()
)

region = st.sidebar.multiselect(
      "Select the Region:",
      options = data['Region'].unique(),
      default = data['Region'].unique()
)

country = st.sidebar.multiselect(
      "Select the Country:",
      options = data['Country'].unique(),
      default = data['Country'].unique()
)

# Extracting the dataframe based on the filters
filtered_data = data[(data['Order Date'].dt.year.isin(year)) &
                     (data['Region'].isin(region)) &
                     (data['Country'].isin(country)) 
                      ]

# Title for the Dashboard
st.title("Visualization of an Online Store Data")
st.markdown("##")


total_sales = int(filtered_data['Sales'].sum())
total_profit = int(filtered_data['Profit'].sum())
total_customers = int(filtered_data['Customer Name'].nunique())
total_products = int(filtered_data['Product Name'].nunique())
average_shipping_time = filtered_data['Shipping Time'].mean()

def calculateChange():
      n = year.count()

      #Grouping By Year
      filtered_data['Year'] = filtered_data['Order Date'].dt.year
      group_by_year = filtered_data.groupby('Year')
      sales_by_year = group_by_year['Sales'].sum()

      sales_by_year = sales_by_year.reset_index()



# Defining conainer for KPIs
con1 = st.container()

with con1:

      col1, col2, col3, col4, col5= st.columns(5)

      with col1:
            if total_sales > 0:
                  if total_sales > 999999:
                        display_sales = total_sales / 1000000
                        st.metric(label = "Total Sales", value = f"${display_sales:,.2f} M")
                  
                  else:
                        if total_sales > 999:
                              display_sales = int(total_sales / 1000)
                              st.metric(label = "Total Sales", value = f"${display_sales} K")
            else:
                  st.metric(label = "Total Sales", value = f"${total_sales} K", delta = "200 K")

      with col2:
            if total_profit > 0:
                  if total_profit > 999999:
                        display_profit = total_profit / 100000
                        st.metric("Total Profit", f"${display_profit:,.2f} M")

                  else:
                        if total_profit > 999:
                              display_profit = int(total_profit / 1000)
                              st.metric("Total Profit", f"${display_profit} K")
            
            else:
                  st.metric("Total Profit", f"${total_profit} K")

      with col3:
            st.metric("Total Customer", f"{total_customers}")

      with col4:
            st.metric("Total Products", f"{total_products}")

      with col5:
            st.metric("Average Shipping Time", f"{average_shipping_time:.2f} days")


st.markdown("---")



# Bar Chart
# Grouping by region
group_by_region = filtered_data.groupby('Region')
sales_by_region = group_by_region['Sales'].sum()

# Grouping By State
group_by_state = filtered_data.groupby('State_Code', as_index = False)
sales_by_state = group_by_state['Sales'].sum()

# Choropleth Map
choropleth = px.choropleth(
      sales_by_state,
      locations = 'State_Code' ,
      locationmode = 'USA-states',
      scope = 'usa',
      color = 'Sales',
      color_continuous_scale = 'Viridis',
      title = "Sales by State/Province in the USA and Canda"
)

con2 = st.container()

with con2:

      col1, col2 = st.columns(2)

      with col1:
           st.header("Bar Chart")
           st.bar_chart(sales_by_region, x_label = "Region", y_label = "Sales")
     
      with col2:
           st.plotly_chart(choropleth)
            



# Line Chart
# Grouping By Year
group_by_year = filtered_data.groupby('Year')
sales_by_year = group_by_year['Sales'].sum()

sales_by_year = sales_by_year.reset_index()
sales_by_year['Year'] = sales_by_year['Year'].astype(str) 

# Donut Chart
# Grouping By Sub-Category
group_by_sub_category = filtered_data.groupby('Sub-Category')
sales_by_sub_category = group_by_sub_category['Sales'].sum()

# sales_by_sub_category = sales_by_sub_category.reset_index()

donutChart = alt.Chart(sales_by_sub_category).mark_arc(innerRadius = 50).encode(
            theta = alt.Theta(field = 'Sales', type = 'quantitative'),
            color = alt.Color(field = 'Sub-Category', type = 'nominal')
)

con3 = st.container()
with con3:
     col1, col2 = st.columns(2)

     with col1:
            st.header("Horizontal Bar Chart")
            # st.altair_chart(donutChart, use_container_width = True)
            st.bar_chart(sales_by_sub_category.T, horizontal = True)
            

     with col2:
            st.header("Line Chart")
            st.line_chart(sales_by_year, x = 'Year', y = 'Sales', x_label = 'Year', y_label = 'Sales')



# Horizontal bar Chart
# Grouping by category
# group_by_category = filtered_data.groupby('Category')
# sales_by_category = group_by_category['Sales'].sum()

# with col1:
#       st.header("Horizontal Bar Chart")
#       st.bar_chart(sales_by_category.T, horizontal = True)


con4 = st.container()

# Grouped Bar Chart
group_by_year_category = filtered_data.groupby(['Year', 'Category'])
profit_by_year_category = group_by_year_category['Profit'].sum()

profit_by_year_category = profit_by_year_category.reset_index()

barChart = alt.Chart(profit_by_year_category).mark_bar().encode(
            x = alt.X('Category:N', title = None, axis = alt.Axis(labels=False)),
            y = alt.Y('sum(Profit):Q', title = 'Total Profit'),
            color = alt.Color('Category:N', scale = alt.Scale(scheme = 'blueorange')),
            column = 'Year:N'
).properties(
            width = 60,
            height = 300
)


# Donut Chart
# Grouping By months
group_by_month = filtered_data.groupby('Month')

profit_by_month = group_by_month['Profit'].sum()
profit_by_month = profit_by_month.reset_index()

# Defining the month order
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']

# Convert 'Month' column to a categorical type with the defined order
profit_by_month['Month'] = pd.Categorical(profit_by_month['Month'], categories=month_order, ordered=True)

# Sorting By Month Order
profit_by_month = profit_by_month.sort_values('Month')

profit_by_month = profit_by_month.reset_index()

# Grouping By Season
group_by_season = filtered_data.groupby('Season')

profit_by_season = group_by_season['Profit'].sum()

profit_by_season = profit_by_season.reset_index()


donutChart = alt.Chart(profit_by_season).mark_arc(innerRadius = 50).encode(
            theta = alt.Theta(field = 'Profit', type = 'quantitative'),
            color = alt.Color(field = 'Season', type = 'nominal')
).properties(
            title = 'Profit By Season'
)

with con4:

      col1, col2 = st.columns(2)

      with col1:
            st.header("Grouped Bar Chart")
            st.altair_chart(barChart)
      
      with col2:
            st.header("Donut Chart")
            st.altair_chart(donutChart, use_container_width = True)


scatter_plot = alt.Chart(filtered_data).mark_circle(size=60).encode(
    x=alt.X('Profit', title='Profit ($)'),
    y=alt.Y('Discount', title='Discount (%)'),
).properties(
    title='Discount vs. Profit',
    width=700,  # Set chart width
    height=400  # Set chart height
)



# con5 = st.container()

# with con5:

#       col1, col2 = st.columns(2)

#       with col1:
            # plt.figure(figsize=(10, 6))
            # sns.scatterplot(data=filtered_data, x='Discount', y='Profit', jitter = True)
            # plt.title('Discount vs. Profit')
            # plt.xlabel('Discount (%)')
            # plt.ylabel('Profit ($)')
            # plt.show()
            # st.pyplot(plt)
            # st.altair_chart(scatter_plot, use_container_width = True)


# WordCloud
city_order_frequency = data.groupby('City')['Order ID'].count().to_dict()

wordcloud = WordCloud(
            width = 1000,
            height = 500,
            background_color = 'black',
            colormap = 'viridis',
            prefer_horizontal = 0,
            contour_width= 0
).generate_from_frequencies(city_order_frequency)

con5 = st.container()

fig, ax = plt.subplots(figsize = (12, 6))
ax.imshow(wordcloud, interpolation = 'bilinear')
ax.axis("off")
plt.gca().set_position([0, 0, 1, 1])  # Fill the entire figure canvas


# # Saving the wordcloud
plt.savefig("wordcloud.png", format="png", bbox_inches="tight", pad_inches=0, facecolor="black")
image = Image.open("wordcloud.png")

with con5:
     st.header("Word Cloud")
#      st.pyplot(fig, clear_figure = True)
     st.image(image, use_container_width=True)
