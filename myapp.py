import streamlit as st
import pandas as pd
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




def load_css(file_path):
    with open(file_path, "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

# Load the CSS file
load_css(r"C:\Users\shish\OneDrive\Desktop\Project\style.css")



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


# Fuction to calculate the change in sales and profit after each year
def calculateChange(years_selected):

      # Grouping the data frame to find the change in sales and profit after each year
      group_by_year = data.groupby('Year').agg({'Sales' : 'sum', 'Profit' : 'sum'}).reset_index()

      group_by_year['Sales Diff'] = group_by_year['Sales'].diff()
      group_by_year['Profit Diff'] = group_by_year['Profit'].diff()

      group_by_year['Sales Diff'] = group_by_year['Sales Diff'].fillna(0)
      group_by_year['Profit Diff'] = group_by_year['Profit Diff'].fillna(0)

      salesChange2022 = group_by_year.loc[group_by_year['Year'] == 2022, 'Sales Diff'].values[0]
      salesChange2023 = group_by_year.loc[group_by_year['Year'] == 2023, 'Sales Diff'].values[0]
      salesChange2024 = group_by_year.loc[group_by_year['Year'] == 2024, 'Sales Diff'].values[0]

      profitChange2022 = group_by_year.loc[group_by_year['Year'] == 2022, 'Profit Diff'].values[0]
      profitChange2023 = group_by_year.loc[group_by_year['Year'] == 2023, 'Profit Diff'].values[0]
      profitChange2024 = group_by_year.loc[group_by_year['Year'] == 2024, 'Profit Diff'].values[0]


      if not years_selected:
            return 0, 0

      n = len(years_selected)

      selected_year = max(years_selected)

      salesChange = 0
      profitChange = 0

      if (n == 1):
            if (selected_year == 2024):
                  salesChange = salesChange2024
                  profitChange = profitChange2024
                  

            elif (selected_year == 2023):
                  salesChange = salesChange2023
                  profitChange = profitChange2023
                  
            
            elif (selected_year == 2022):
                  salesChange = salesChange2022
                  profitChange = profitChange2022
                  

            elif (selected_year == 2021):
                  salesChange = 0
                  salesChange = 0
      
      elif(n > 1):
            return 0,0
    
      salesChange = int(salesChange/1000)
      profitChange = int(profitChange/1000)

      return salesChange, profitChange
      

# Calling the fucntion to calculate the change
salesChange, profitChange = calculateChange(year)


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
                  st.metric(label = "Total Sales", value = f"${total_sales} K")

      with col2:
            if total_profit > 0:
                  if total_profit > 999999:
                        display_profit = total_profit / 100000
                        st.metric("Total Profit", value = f"${display_profit:,.2f} M")

                  else:
                        if total_profit > 999:
                              display_profit = int(total_profit / 1000)
                              st.metric("Total Profit", value = f"${display_profit} K")
            
            else:
                  st.metric("Total Profit", f"${total_profit} K")

      with col3:
            st.metric("Total Customer", f"{total_customers}")

      with col4:
            st.metric("Total Products", f"{total_products}")

      with col5:
            st.metric("Average Shipping Time", f"{average_shipping_time:.2f} Days")


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
      title = "Sales By State/Province"
)

choropleth.update_layout(
    title_font=dict(
        size=36  # Change this value to set your desired font size
    )
)

con2 = st.container()

with con2:

      col1, col2 = st.columns(2)

      with col1:
           st.header("Bar Chart (Sales Vs Region)")
           st.bar_chart(sales_by_region, x_label = "Region", y_label = "Sales")
     
      with col2:
           st.plotly_chart(choropleth)
            




# Horizontal Bar Chart
# Grouping By Sub-Category
group_by_sub_category = filtered_data.groupby('Sub-Category')
sales_by_sub_category = group_by_sub_category['Sales'].sum()



# Line Chart
# Grouping By Year
group_by_year = filtered_data.groupby('Year')
sales_by_year = group_by_year['Sales'].sum()

sales_by_year = sales_by_year.reset_index()
sales_by_year['Year'] = sales_by_year['Year'].astype(str) 



con3 = st.container()
with con3:
     col1, col2 = st.columns(2)

     with col1:
            st.header("Horizontal Bar Chart")
            st.bar_chart(sales_by_sub_category.T, horizontal = True, x_label = "Sales", y_label = "Sub-Category")
            

     with col2:
            st.header("Line Chart (Sales Vs Year)")
            st.line_chart(sales_by_year, x = 'Year', y = 'Sales', x_label = 'Year', y_label = 'Sales')









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

con4 = st.container()

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


# Saving the wordcloud
plt.savefig("wordcloud.png", format="png", bbox_inches="tight", pad_inches=0, facecolor="black")
image = Image.open("wordcloud.png")

with con5:
     st.header("Word Cloud (Most Frequent Cities)")
#      st.pyplot(fig, clear_figure = True)
     st.image(image, use_container_width=True)
