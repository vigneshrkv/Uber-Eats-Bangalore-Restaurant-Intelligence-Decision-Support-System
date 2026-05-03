import streamlit as st
import pandas as pd
import sqlite3

# Title
st.title("🍽 Restaurant Data Explorer")

# Connect to DB
conn = sqlite3.connect("food_data.db")

# Dropdown for queries
option = st.selectbox(
    "Select Analysis",
    [
        "Restaurants by Price Category",
        "Average Rating by Location",
        "Rating Segmentation",
        "Average Rating by Price Category"
    ]
)

# Queries
if option == "Restaurants by Price Category":
    query = """
    SELECT price_category, COUNT(*) AS total_restaurants
    FROM restaurants
    GROUP BY price_category;
    """

elif option == "Average Rating by Location":
    query = """
    SELECT location, AVG(rate) AS avg_rating
    FROM restaurants
    GROUP BY location
    HAVING AVG(rate) > 4;
    """

elif option == "Rating Segmentation":
    query = """
    SELECT name, rate,
    CASE 
        WHEN rate <= 2.5 THEN 'Low'
        WHEN rate <= 4 THEN 'Average'
        ELSE 'Good'
    END AS rating_segment
    FROM restaurants
    LIMIT 20;
    """

elif option == "Average Rating by Price Category":
    query = """
    SELECT price_category, AVG(rate) AS avg_rating
    FROM restaurants
    GROUP BY price_category
    ORDER BY avg_rating DESC;
    """

# Run query
df = pd.read_sql(query, conn)

# Display result
st.dataframe(df)