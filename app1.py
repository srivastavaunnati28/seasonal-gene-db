import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="🧬 Seasonal Gene DB",
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

conn = get_connection()

st.title("🧬 Seasonal Physiology Gene Database")
st.markdown("**Search genes → See seasonal expression roles**")
st.divider()

gene_input = st.text_input("🔍 Gene Symbol",
                            placeholder="e.g. CLOCK, VDR, IL6, LEP")

if gene_input:
    query = """
        SELECT g.gene_symbol, g.full_name, g.category,
               s.name AS season, gsf.expression_level,
               gsf.fold_change, gsf.functional_role,
               gsf.pathway, gsf.tissue_type, gsf.study_reference
        FROM gene_seasonal_function gsf
        JOIN genes g ON gsf.gene_id = g.id
        JOIN seasons s ON gsf.season_id = s.id
        WHERE g.gene_symbol = %s
        ORDER BY s.start_month
    """
    df = pd.read_sql(query, conn, params=[gene_input.upper()])

    if not df.empty:
        st.success(f"✅ Found: **{df['full_name'][0]}**")

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(df, x='season', y='fold_change',
                        color='season',
                        color_discrete_map={
                            'Winter': '#60a5fa',
                            'Spring': '#4ade80',
                            'Summer': '#f59e0b',
                            'Autumn': '#f87171'
                        },
                        title=f"{gene_input.upper()} — Seasonal Expression")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Seasonal Roles")
            icons = {'Winter':'❄️','Spring':'🌱','Summer':'☀️','Autumn':'🍂'}
            expr  = {'HIGH':'🔴','NORMAL':'🟡','LOW':'🟢'}
            for _, row in df.iterrows():
                st.markdown(f"""
**{icons[row['season']]} {row['season']}** — {expr[row['expression_level']]} {row['expression_level']} | {row['fold_change']}x
> {row['functional_role']}
                """)

        st.divider()
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "⬇️ Download CSV",
            df.to_csv(index=False),
            f"{gene_input}_data.csv",
            "text/csv"
        )
    else:
        st.warning("Gene not found! Try: CLOCK, VDR, IL6, LEP, SLC6A4")

st.divider()
st.markdown("### 🗂 All Genes in Database")
all_df = pd.read_sql("SELECT * FROM genes", conn)
st.dataframe(all_df, use_container_width=True)
