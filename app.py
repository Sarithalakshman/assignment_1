import warnings
warnings.filterwarnings("ignore", module="streamlit.runtime.scriptrunner_utils")
import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px

# Function to establish a database connection
def connect_to_database():
    return mysql.connector.connect(
        host="localhost",  
        user="srihariharan",  
        password="srihariharan9",
        database="books"  
    )

# Function to fetch data from the database
def fetch_books_data():
    connection = connect_to_database()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books")  
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return data

# Streamlit app
def main():
    st.title("Books Data Viewer 📚")

    # Data Source Selection
    data_source = st.radio("Choose data source:", ("Database", "CSV File"))

    df = None  # Initialize dataframe

    if data_source == "Database":
        if st.button("Fetch Books Data"):
            st.write("Fetching data from the database...")
            try:
                books_data = fetch_books_data()
                if books_data:
                    df = pd.DataFrame(books_data)
                    st.write("Data fetched successfully!")
                    st.dataframe(df)
                else:
                    st.warning("No data found in the database!")
            except Exception as e:
                st.error(f"An error occurred: {e}")

    elif data_source == "CSV File":
        uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)  # Read CSV data
            st.write("Data loaded successfully from CSV!")
            st.dataframe(df)

    # Option to display specific queries (only for Database)
    if data_source == "Database" and df is not None:
        query = st.text_input("Enter a search key to filter results:", "")
        if query:
            st.write(f"Searching for books with the key: {query}")
            try:
                connection = connect_to_database()
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM books WHERE search_key LIKE %s", (f"%{query}%",))
                filtered_data = cursor.fetchall()
                if filtered_data:
                    filtered_df = pd.DataFrame(filtered_data)
                    st.dataframe(filtered_df)
                else:
                    st.warning("No matching records found!")
                cursor.close()
                connection.close()
            except Exception as e:
                st.error(f"An error occurred while searching: {e}")

    # Data visualization section
    if df is not None and st.button("Visualize Data"):
        st.write("Columns available:", df.columns.tolist())  # Show available columns
        
        # Price Distribution Bar Chart
        st.subheader("Price Distribution (Bar Chart)")
        if "amount_retailPrice" in df.columns:
            st.bar_chart(df["amount_retailPrice"])
        else:
            st.warning("The 'amount_retailPrice' column is not available in the data.")

        # Plotly Scatter Plot: Price vs Ratings
        st.subheader("Interactive Scatter Plot (Price vs Ratings)")
        if "amount_retailPrice" in df.columns and "averageRating" in df.columns:
            fig = px.scatter(
                df, 
                x="amount_retailPrice", 
                y="averageRating", 
                color="category" if "category" in df.columns else None, 
                title="Price vs Ratings by Category"
            )
            st.plotly_chart(fig)
        else:
            st.warning("Columns 'amount_retailPrice' and/or 'averageRating' are not available in the data.")

        # Pie Chart: Book Categories Distribution
        st.subheader("Book Categories Distribution (Pie Chart)")
        if "categories" in df.columns:
            category_counts = df["categories"].value_counts().reset_index()
            category_counts.columns = ["Category", "Count"]
            fig = px.pie(category_counts, names="Category", values="Count", title="Book Categories Distribution")
            st.plotly_chart(fig)
        else:
            st.warning("The 'categories' column is not available in the data.")

if __name__ == "__main__":
    main()
