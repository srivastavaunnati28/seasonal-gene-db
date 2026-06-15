import streamlit as st
import mysql.connector
import pandas as pd

st.set_page_config(
    page_title="Seasonal Physiology Gene Database",
    page_icon="🧬",
    layout="wide"
)

@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"],
        port=int(st.secrets["DB_PORT"])
    )

try:
    conn = get_connection()

except mysql.connector.Error as err:
    st.error(f"Database Connection Failed: {err}")
    st.stop()

st.title("🧬 Seasonal Physiology Gene Database")

gene = st.text_input("Enter Gene Name")

if gene:
    query = """
    SELECT *
    FROM genes
    WHERE gene_name LIKE %s
    """

    try:
        df = pd.read_sql(
            query,
            conn,
            params=(f"%{gene}%",)
        )

        if len(df):
            st.dataframe(df)
        else:
            st.warning("No gene found.")

    except Exception as e:
        st.error(str(e))
