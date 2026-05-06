"""
Uber Eats Bangalore — Restaurant Intelligence & Decision Support System
=======================================================================
Built from: CLEANED1.csv  +  orders.json
DB file   : food_data.db  (SQLite)
Tables    : restaurants, orders

How to setup DB (run once before launching app):
-------------------------------------------------
    python setup_db.py

How to run app:
-------------------------------------------------
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import sqlite3

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Uber Eats Bangalore Analytics",
    page_icon="🍽️",
    layout="wide",
)

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE CONNECTION
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_conn():
    return sqlite3.connect("food_data.db", check_same_thread=False)

conn = get_conn()

def run_query(sql: str) -> pd.DataFrame:
    return pd.read_sql(sql, conn)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.title("Uber Eats Bangalore")
st.sidebar.markdown("Restaurant Intelligence & Decision Support System")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Dashboard", "❓ Q&A — Restaurants", "📦 Q&A — Orders"],
)

st.sidebar.markdown("---")
st.sidebar.caption("GUVI x HCL Capstone Project")


# =============================================================================
# PAGE 1 — DASHBOARD
# Columns in DB : name, online_order (Yes/No), book_table (Yes/No),
#                 rate (float), votes (int), location, rest_type,
#                 dish_liked, cuisines, approx_cost_for_two (int),
#                 listed_type, listed_city, rating_category, price_category
# price_category : Cheap | Low | Moderate | High | Very High
# rating_category: Low | Average | Good
# =============================================================================
if page == "🏠 Dashboard":

    st.title("🏠 Restaurant Data Explorer")
    st.markdown(
        "Use the Quick Analysis dropdown for predefined queries, "
        "or apply filters below to explore the full dataset."
    )
    st.markdown("---")

    # ── SECTION A : Quick Analysis (4 original queries) ──────────────────────
    st.subheader("Quick Analysis")

    option = st.selectbox(
        "Select Analysis",
        [
            "Restaurants by Price Category",
            "Average Rating by Location",
            "Rating Segmentation",
            "Average Rating by Price Category",
        ],
    )

    if option == "Restaurants by Price Category":
        query = """
            SELECT price_category        AS Price_Category,
                   COUNT(*)              AS Total_Restaurants
            FROM restaurants
            GROUP BY price_category
            ORDER BY Total_Restaurants DESC;
        """

    elif option == "Average Rating by Location":
        query = """
            SELECT location              AS Location,
                   ROUND(AVG(rate), 2)   AS Avg_Rating,
                   COUNT(*)              AS Num_Restaurants
            FROM restaurants
            WHERE rate IS NOT NULL
            GROUP BY location
            HAVING AVG(rate) > 4
            ORDER BY Avg_Rating DESC;
        """

    elif option == "Rating Segmentation":
        query = """
            SELECT name                  AS Restaurant,
                   rate                  AS Rate,
                   rating_category       AS Rating_Segment
            FROM restaurants
            WHERE rate IS NOT NULL
            ORDER BY rate DESC
            LIMIT 20;
        """

    elif option == "Average Rating by Price Category":
        query = """
            SELECT price_category        AS Price_Category,
                   ROUND(AVG(rate), 2)   AS Avg_Rating,
                   COUNT(*)              AS Num_Restaurants
            FROM restaurants
            WHERE rate IS NOT NULL
            GROUP BY price_category
            ORDER BY Avg_Rating DESC;
        """

    df = run_query(query)
    st.markdown(f"**{len(df)} rows returned**")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")

    # ── SECTION B : Filter Explorer ──────────────────────────────────────────
    st.subheader("Filter and Explore Restaurants")

    # Fetch distinct filter values directly from DB
    locations = ["All"] + run_query(
        "SELECT DISTINCT location FROM restaurants WHERE location IS NOT NULL ORDER BY location"
    )["location"].tolist()

    rest_types = ["All"] + run_query(
        "SELECT DISTINCT rest_type FROM restaurants WHERE rest_type IS NOT NULL ORDER BY rest_type"
    )["rest_type"].tolist()

    listed_types = ["All"] + run_query(
        "SELECT DISTINCT listed_type FROM restaurants WHERE listed_type IS NOT NULL ORDER BY listed_type"
    )["listed_type"].tolist()

    # Filter row 1
    c1, c2, c3 = st.columns(3)
    with c1:
        sel_location  = st.selectbox("Location",       locations)
    with c2:
        sel_rest_type = st.selectbox("Restaurant Type", rest_types)
    with c3:
        sel_listed    = st.selectbox("Listed In",       listed_types)

    # Filter row 2
    c4, c5, c6 = st.columns(3)
    with c4:
        sel_online   = st.selectbox("Online Order",    ["All", "Yes", "No"])
    with c5:
        sel_booking  = st.selectbox("Table Booking",   ["All", "Yes", "No"])
    with c6:
        sel_price    = st.selectbox("Price Category",
                                    ["All", "Cheap", "Low", "Moderate", "High", "Very High"])

    # Filter row 3
    c7, c8 = st.columns(2)
    with c7:
        min_rate = st.slider("Minimum Rating", 1.8, 4.9, 3.5, step=0.1)
    with c8:
        max_cost = st.slider("Max Cost for Two (Rs)", 40, 6000, 2000, step=100)

    # Build WHERE clause
    conditions = [
        "rate IS NOT NULL",
        f"rate >= {min_rate}",
        f"approx_cost_for_two <= {max_cost}",
    ]
    if sel_location  != "All": conditions.append(f"location = '{sel_location}'")
    if sel_rest_type != "All": conditions.append(f"rest_type = '{sel_rest_type}'")
    if sel_listed    != "All": conditions.append(f"listed_type = '{sel_listed}'")
    if sel_online    != "All": conditions.append(f"online_order = '{sel_online}'")
    if sel_booking   != "All": conditions.append(f"book_table = '{sel_booking}'")
    if sel_price     != "All": conditions.append(f"price_category = '{sel_price}'")

    where_clause = " AND ".join(conditions)

    filter_sql = f"""
        SELECT name                AS Restaurant,
               location            AS Location,
               rest_type           AS Type,
               cuisines            AS Cuisines,
               rate                AS Rating,
               votes               AS Votes,
               approx_cost_for_two AS Cost_for_Two,
               price_category      AS Price_Category,
               rating_category     AS Rating_Category,
               online_order        AS Online_Order,
               book_table          AS Table_Booking,
               listed_type         AS Listed_In
        FROM restaurants
        WHERE {where_clause}
        ORDER BY rate DESC, votes DESC
    """

    df_filtered = run_query(filter_sql)
    st.markdown(f"### Results — {len(df_filtered):,} restaurants found")
    st.dataframe(df_filtered, use_container_width=True, height=420)

    if len(df_filtered) > 0:
        st.markdown("---")
        st.markdown("#### Summary")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Restaurants", f"{len(df_filtered):,}")
        m2.metric("Avg Rating",        f"{df_filtered['Rating'].mean():.2f}")
        m3.metric("Avg Cost for Two",  f"Rs {df_filtered['Cost_for_Two'].mean():.0f}")
        m4.metric("Avg Votes",         f"{df_filtered['Votes'].mean():.0f}")


# =============================================================================
# PAGE 2 — Q&A : RESTAURANTS (15 business questions)
# =============================================================================
elif page == "❓ Q&A — Restaurants":

    st.title("Q&A — Restaurant Business Intelligence")
    st.markdown(
        "Select a business question. The answer is computed live from the "
        "**restaurants** table using SQL and displayed as a DataFrame."
    )
    st.markdown("---")

    QUESTIONS = [
        "Q1  — Which locations have the highest average restaurant ratings?",
        "Q2  — Which locations are over-saturated with restaurants?",
        "Q3  — Does online ordering improve restaurant ratings?",
        "Q4  — Does table booking correlate with higher customer ratings?",
        "Q5  — What price category delivers the best customer satisfaction?",
        "Q6  — How do different price categories perform on rating segments?",
        "Q7  — Which cuisines are most common in Bangalore?",
        "Q8  — Which cuisines receive the highest average ratings?",
        "Q9  — Which cuisines perform well despite having fewer restaurants?",
        "Q10 — What is the relationship between restaurant cost and rating?",
        "Q11 — Which locations are ideal for premium restaurant onboarding?",
        "Q12 — Which locations show high demand but lower average ratings?",
        "Q13 — Do restaurants with both online ordering and table booking perform better?",
        "Q14 — What combination of factors maximises restaurant success?",
        "Q15 — Which restaurants are top performers within each price category?",
    ]

    selected_q = st.selectbox("Select a Business Question", QUESTIONS)
    qnum = int(selected_q.split("Q")[1].split()[0])

    BV = {
        1:  "Identifies premium-performing areas suitable for brand positioning and new partner onboarding.",
        2:  "Helps avoid overcrowded markets and guides smarter expansion decisions.",
        3:  "Evaluates the ROI of Uber Eats online ordering feature for restaurant partners.",
        4:  "Measures the effectiveness of table booking as a premium platform feature.",
        5:  "Helps define the optimal pricing band for maximum partner success.",
        6:  "Supports pricing-based market segmentation and partner strategy.",
        7:  "Reveals market demand and cuisine saturation levels across Bangalore.",
        8:  "Identifies high-quality cuisine categories suitable for targeted promotion.",
        9:  "Highlights niche cuisine opportunities with strong differentiation potential.",
        10: "Determines whether higher pricing translates to better customer perception.",
        11: "Combines cost, rating, and location data to guide premium restaurant expansion.",
        12: "Indicates areas where quality improvement and partner support are needed.",
        13: "Validates whether bundled feature adoption leads to better restaurant performance.",
        14: "Supports strategic partner recommendations across pricing, location, and features.",
        15: "Helps identify benchmark partners and best practices within each pricing tier.",
    }

    st.info(f"Business Value: {BV[qnum]}")

    SQL = {

        1: """
            SELECT location                     AS Location,
                   ROUND(AVG(rate), 2)          AS Avg_Rating,
                   COUNT(*)                     AS Num_Restaurants
            FROM restaurants
            WHERE rate IS NOT NULL
              AND location IS NOT NULL
            GROUP BY location
            ORDER BY Avg_Rating DESC
            LIMIT 15;
        """,

        2: """
            SELECT location                     AS Location,
                   COUNT(*)                     AS Restaurant_Count,
                   ROUND(AVG(rate), 2)          AS Avg_Rating
            FROM restaurants
            WHERE location IS NOT NULL
            GROUP BY location
            ORDER BY Restaurant_Count DESC
            LIMIT 15;
        """,

        3: """
            SELECT online_order                 AS Online_Order,
                   ROUND(AVG(rate), 2)          AS Avg_Rating,
                   COUNT(*)                     AS Num_Restaurants
            FROM restaurants
            WHERE rate IS NOT NULL
            GROUP BY online_order
            ORDER BY Avg_Rating DESC;
        """,

        4: """
            SELECT book_table                   AS Table_Booking,
                   ROUND(AVG(rate), 2)          AS Avg_Rating,
                   COUNT(*)                     AS Num_Restaurants
            FROM restaurants
            WHERE rate IS NOT NULL
            GROUP BY book_table
            ORDER BY Avg_Rating DESC;
        """,

        5: """
            SELECT price_category               AS Price_Category,
                   ROUND(AVG(rate), 2)          AS Avg_Rating,
                   COUNT(*)                     AS Num_Restaurants
            FROM restaurants
            WHERE rate IS NOT NULL
              AND price_category IS NOT NULL
            GROUP BY price_category
            ORDER BY Avg_Rating DESC;
        """,

        6: """
            SELECT price_category               AS Price_Category,
                   rating_category              AS Rating_Category,
                   COUNT(*)                     AS Num_Restaurants,
                   ROUND(AVG(rate), 2)          AS Avg_Rating
            FROM restaurants
            WHERE price_category IS NOT NULL
              AND rating_category IS NOT NULL
            GROUP BY price_category, rating_category
            ORDER BY price_category, Avg_Rating DESC;
        """,

        7: """
            SELECT cuisines                     AS Cuisine,
                   COUNT(*)                     AS Num_Restaurants
            FROM restaurants
            WHERE cuisines IS NOT NULL
            GROUP BY cuisines
            ORDER BY Num_Restaurants DESC
            LIMIT 20;
        """,

        8: """
            SELECT cuisines                     AS Cuisine,
                   ROUND(AVG(rate), 2)          AS Avg_Rating,
                   COUNT(*)                     AS Num_Restaurants
            FROM restaurants
            WHERE rate IS NOT NULL
              AND cuisines IS NOT NULL
            GROUP BY cuisines
            HAVING COUNT(*) >= 5
            ORDER BY Avg_Rating DESC
            LIMIT 20;
        """,

        9: """
            SELECT cuisines                     AS Cuisine,
                   COUNT(*)                     AS Num_Restaurants,
                   ROUND(AVG(rate), 2)          AS Avg_Rating
            FROM restaurants
            WHERE rate IS NOT NULL
              AND cuisines IS NOT NULL
            GROUP BY cuisines
            HAVING COUNT(*) BETWEEN 2 AND 15
               AND AVG(rate) >= 4.0
            ORDER BY Avg_Rating DESC
            LIMIT 20;
        """,

        10: """
            SELECT CASE
                       WHEN approx_cost_for_two <= 300               THEN '0 - 300'
                       WHEN approx_cost_for_two BETWEEN 301 AND 700  THEN '301 - 700'
                       WHEN approx_cost_for_two BETWEEN 701 AND 1500 THEN '701 - 1500'
                       ELSE '1500+'
                   END                               AS Cost_Bracket,
                   ROUND(AVG(rate), 2)               AS Avg_Rating,
                   ROUND(AVG(approx_cost_for_two), 0) AS Avg_Cost,
                   COUNT(*)                          AS Num_Restaurants
            FROM restaurants
            WHERE rate IS NOT NULL
              AND approx_cost_for_two IS NOT NULL
            GROUP BY Cost_Bracket
            ORDER BY Avg_Cost;
        """,

        11: """
            SELECT location                          AS Location,
                   ROUND(AVG(rate), 2)               AS Avg_Rating,
                   ROUND(AVG(approx_cost_for_two), 0) AS Avg_Cost,
                   COUNT(*)                          AS Num_Restaurants
            FROM restaurants
            WHERE rate IS NOT NULL
              AND price_category IN ('High', 'Very High')
            GROUP BY location
            HAVING Avg_Rating >= 4.0
               AND Num_Restaurants >= 5
            ORDER BY Avg_Rating DESC, Avg_Cost DESC
            LIMIT 15;
        """,

        12: """
            SELECT location                     AS Location,
                   COUNT(*)                     AS Num_Restaurants,
                   ROUND(AVG(rate), 2)          AS Avg_Rating
            FROM restaurants
            WHERE rate IS NOT NULL
            GROUP BY location
            HAVING Num_Restaurants >= 20
               AND Avg_Rating < 3.9
            ORDER BY Num_Restaurants DESC;
        """,

        13: """
            SELECT online_order                 AS Online_Order,
                   book_table                   AS Table_Booking,
                   ROUND(AVG(rate), 2)          AS Avg_Rating,
                   COUNT(*)                     AS Num_Restaurants
            FROM restaurants
            WHERE rate IS NOT NULL
            GROUP BY online_order, book_table
            ORDER BY Avg_Rating DESC;
        """,

        14: """
            SELECT price_category               AS Price_Category,
                   online_order                 AS Online_Order,
                   book_table                   AS Table_Booking,
                   ROUND(AVG(rate), 2)          AS Avg_Rating,
                   COUNT(*)                     AS Num_Restaurants
            FROM restaurants
            WHERE rate IS NOT NULL
              AND price_category IS NOT NULL
            GROUP BY price_category, online_order, book_table
            HAVING Num_Restaurants >= 10
            ORDER BY Avg_Rating DESC
            LIMIT 20;
        """,

        15: """
            SELECT r.price_category             AS Price_Category,
                   r.name                       AS Restaurant,
                   r.location                   AS Location,
                   r.rate                       AS Rating,
                   r.votes                      AS Votes,
                   r.approx_cost_for_two        AS Cost_for_Two
            FROM restaurants r
            INNER JOIN (
                SELECT price_category,
                       MAX(rate) AS max_rate
                FROM restaurants
                WHERE rate IS NOT NULL
                  AND price_category IS NOT NULL
                GROUP BY price_category
            ) top ON r.price_category = top.price_category
                 AND r.rate           = top.max_rate
            WHERE r.rate IS NOT NULL
              AND r.price_category IS NOT NULL
            ORDER BY r.price_category, r.votes DESC;
        """,
    }

    with st.spinner("Running SQL query..."):
        df_ans = run_query(SQL[qnum])

    st.markdown(f"**{len(df_ans)} rows returned**")
    st.dataframe(df_ans, use_container_width=True)


# =============================================================================
# PAGE 3 — Q&A : ORDERS
# orders columns: order_id, restaurant_name, order_date, order_value,
#                 discount_used (0/1 int), payment_method (Card/Cash/UPI)
# =============================================================================
elif page == "📦 Q&A — Orders":

    st.title("Q&A — Orders Analytics")
    st.markdown(
        "10 business questions answered from the **orders** table (25,000 records). "
        "All queries run live on SQLite."
    )
    st.markdown("---")

    ORDER_QUESTIONS = [
        "OQ1  — Total and average order value by payment method",
        "OQ2  — Which restaurants generate the highest total revenue?",
        "OQ3  — How many orders used a discount vs full price?",
        "OQ4  — Average order value: discount used vs not used",
        "OQ5  — Which payment method is most popular?",
        "OQ6  — Which restaurants have the highest number of orders?",
        "OQ7  — Monthly revenue trend (total revenue per month)",
        "OQ8  — Which restaurants have the highest average order value?",
        "OQ9  — Revenue split by discount usage for Top 10 restaurants",
        "OQ10 — Overall discount impact on total revenue",
    ]

    selected_oq = st.selectbox("Select an Orders Question", ORDER_QUESTIONS)
    oqnum = int(selected_oq.split("OQ")[1].split()[0])

    OQ_BV = {
        1:  "Understand which payment channel drives the most revenue and average spend per order.",
        2:  "Identify top revenue-generating restaurant partners for strategic investment.",
        3:  "Measure how widely discount promotions are being used across all orders.",
        4:  "Evaluate whether discounts attract lower-spend orders or maintain order value.",
        5:  "Informs payment gateway investment and checkout flow optimisation decisions.",
        6:  "Reveals the most active restaurant partners by order volume on the platform.",
        7:  "Track platform growth and seasonal demand patterns month-over-month.",
        8:  "Find high-value restaurants that attract premium spend per order.",
        9:  "Understand the revenue contribution of discounted vs full-price orders per restaurant.",
        10: "Quantify the overall revenue trade-off from running discount campaigns.",
    }

    st.info(f"Business Value: {OQ_BV[oqnum]}")

    ORDER_SQL = {

        1: """
            SELECT payment_method               AS Payment_Method,
                   COUNT(*)                     AS Total_Orders,
                   ROUND(SUM(order_value), 2)   AS Total_Revenue,
                   ROUND(AVG(order_value), 2)   AS Avg_Order_Value,
                   ROUND(MIN(order_value), 2)   AS Min_Order_Value,
                   ROUND(MAX(order_value), 2)   AS Max_Order_Value
            FROM orders
            GROUP BY payment_method
            ORDER BY Total_Revenue DESC;
        """,

        2: """
            SELECT restaurant_name              AS Restaurant,
                   COUNT(*)                     AS Total_Orders,
                   ROUND(SUM(order_value), 2)   AS Total_Revenue,
                   ROUND(AVG(order_value), 2)   AS Avg_Order_Value
            FROM orders
            GROUP BY restaurant_name
            ORDER BY Total_Revenue DESC
            LIMIT 20;
        """,

        3: """
            SELECT CASE WHEN discount_used = 1 THEN 'Yes' ELSE 'No' END
                                                AS Discount_Used,
                   COUNT(*)                     AS Total_Orders,
                   ROUND(COUNT(*) * 100.0 /
                       (SELECT COUNT(*) FROM orders), 2)    AS Percentage
            FROM orders
            GROUP BY discount_used;
        """,

        4: """
            SELECT CASE WHEN discount_used = 1 THEN 'Yes' ELSE 'No' END
                                                AS Discount_Used,
                   COUNT(*)                     AS Total_Orders,
                   ROUND(AVG(order_value), 2)   AS Avg_Order_Value,
                   ROUND(SUM(order_value), 2)   AS Total_Revenue
            FROM orders
            GROUP BY discount_used
            ORDER BY discount_used DESC;
        """,

        5: """
            SELECT payment_method               AS Payment_Method,
                   COUNT(*)                     AS Total_Orders,
                   ROUND(COUNT(*) * 100.0 /
                       (SELECT COUNT(*) FROM orders), 2)    AS Percentage
            FROM orders
            GROUP BY payment_method
            ORDER BY Total_Orders DESC;
        """,

        6: """
            SELECT restaurant_name              AS Restaurant,
                   COUNT(*)                     AS Total_Orders,
                   ROUND(SUM(order_value), 2)   AS Total_Revenue
            FROM orders
            GROUP BY restaurant_name
            ORDER BY Total_Orders DESC
            LIMIT 20;
        """,

        7: """
            SELECT STRFTIME('%Y-%m', order_date) AS Month,
                   COUNT(*)                      AS Total_Orders,
                   ROUND(SUM(order_value), 2)    AS Total_Revenue,
                   ROUND(AVG(order_value), 2)    AS Avg_Order_Value
            FROM orders
            GROUP BY Month
            ORDER BY Month ASC;
        """,

        8: """
            SELECT restaurant_name              AS Restaurant,
                   ROUND(AVG(order_value), 2)   AS Avg_Order_Value,
                   COUNT(*)                     AS Total_Orders,
                   ROUND(SUM(order_value), 2)   AS Total_Revenue
            FROM orders
            GROUP BY restaurant_name
            HAVING Total_Orders >= 10
            ORDER BY Avg_Order_Value DESC
            LIMIT 20;
        """,

        9: """
            SELECT restaurant_name              AS Restaurant,
                   ROUND(SUM(CASE WHEN discount_used = 1
                                  THEN order_value ELSE 0 END), 2)
                                                AS Revenue_With_Discount,
                   ROUND(SUM(CASE WHEN discount_used = 0
                                  THEN order_value ELSE 0 END), 2)
                                                AS Revenue_Without_Discount,
                   ROUND(SUM(order_value), 2)   AS Total_Revenue,
                   SUM(CASE WHEN discount_used = 1 THEN 1 ELSE 0 END)
                                                AS Discounted_Orders,
                   SUM(CASE WHEN discount_used = 0 THEN 1 ELSE 0 END)
                                                AS Full_Price_Orders
            FROM orders
            WHERE restaurant_name IN (
                SELECT restaurant_name FROM orders
                GROUP BY restaurant_name
                ORDER BY COUNT(*) DESC
                LIMIT 10
            )
            GROUP BY restaurant_name
            ORDER BY Total_Revenue DESC;
        """,

        10: """
            SELECT CASE WHEN discount_used = 1
                        THEN 'Discounted' ELSE 'Full Price' END
                                                AS Order_Type,
                   COUNT(*)                     AS Total_Orders,
                   ROUND(SUM(order_value), 2)   AS Total_Revenue,
                   ROUND(AVG(order_value), 2)   AS Avg_Order_Value,
                   ROUND(SUM(order_value) * 100.0 /
                       (SELECT SUM(order_value) FROM orders), 2)
                                                AS Revenue_Percentage
            FROM orders
            GROUP BY discount_used
            ORDER BY discount_used DESC;
        """,
    }

    with st.spinner("Running query on orders table..."):
        df_order = run_query(ORDER_SQL[oqnum])

    st.markdown(f"**{len(df_order)} rows returned**")
    st.dataframe(df_order, use_container_width=True)

    # Permanent summary metrics
    st.markdown("---")
    st.subheader("Orders Dataset Overview")

    df_summary = run_query("""
        SELECT COUNT(*)                         AS Total_Orders,
               ROUND(SUM(order_value), 2)       AS Total_Revenue,
               ROUND(AVG(order_value), 2)       AS Avg_Order_Value,
               COUNT(DISTINCT restaurant_name)  AS Unique_Restaurants,
               SUM(discount_used)               AS Discounted_Orders
        FROM orders;
    """)

    if len(df_summary) > 0:
        row = df_summary.iloc[0]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Orders",       f"{int(row['Total_Orders']):,}")
        c2.metric("Total Revenue",      f"Rs {float(row['Total_Revenue']):,.2f}")
        c3.metric("Avg Order Value",    f"Rs {float(row['Avg_Order_Value']):,.2f}")
        c4.metric("Unique Restaurants", f"{int(row['Unique_Restaurants'])}")
        c5.metric("Discounted Orders",  f"{int(row['Discounted_Orders']):,}")
        
