import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(
    page_title="🧬 Seasonal Gene DB",
    page_icon="🧬",
    layout="wide"
)

# Database connection
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root16",  # apna password
        database="seasonal_physiology_db"
    )

conn = get_connection()

# Header
st.title("🧬 Seasonal Physiology Gene Database")
st.markdown("**Search genes → See seasonal expression roles**")
st.divider()

# Search box
col1, col2 = st.columns([3, 1])
with col1:
    gene_input = st.text_input("🔍 Gene Symbol", 
                                placeholder="e.g. CLOCK, VDR, IL6, LEP")
with col2:
    category = st.selectbox("Category", 
                ["All", "Circadian", "Hormonal", "Immune", "Metabolic", "Mood/Brain"])

# Search result
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
        # Gene info
        st.success(f"✅ Found: **{df['full_name'][0]}** | Category: {df['category'][0]}")
        
        # 2 columns layout
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart
            fig = px.bar(df, x='season', y='fold_change',
                        color='season',
                        color_discrete_map={
                            'Winter': '#60a5fa',
                            'Spring': '#4ade80',
                            'Summer': '#f59e0b',
                            'Autumn': '#f87171'
                        },
                        title=f"{gene_input.upper()} — Fold Change by Season",
                        labels={'fold_change': 'Fold Change', 'season': 'Season'})
            fig.update_layout(showlegend=False, 
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Expression levels
            st.markdown("### Seasonal Expression")
            for _, row in df.iterrows():
                season_icons = {
                    'Winter': '❄️', 'Spring': '🌱',
                    'Summer': '☀️', 'Autumn': '🍂'
                }
                expr_colors = {
                    'HIGH': '🔴', 'NORMAL': '🟡', 'LOW': '🟢'
                }
                st.markdown(f"""
                **{season_icons[row['season']]} {row['season']}** 
                {expr_colors[row['expression_level']]} {row['expression_level']} 
                | Fold: {row['fold_change']}x
                > {row['functional_role']}
                """)
        
        # Full table
        st.divider()
        st.markdown("### 📊 Full Data Table")
        st.dataframe(df[['season', 'expression_level', 'fold_change',
                         'pathway', 'tissue_type', 'study_reference']],
                    use_container_width=True)
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name=f"{gene_input}_seasonal_data.csv",
            mime="text/csv"
        )
    else:
        st.warning("Gene not found! Try: CLOCK, VDR, IL6, LEP, SLC6A4")

# Show all genes
st.divider()
st.markdown("### 🗂 All Genes in Database")

all_query = """
    SELECT g.gene_symbol, g.full_name, g.category, g.chromosome,
           COUNT(gsf.id) as seasons_count
    FROM genes g
    LEFT JOIN gene_seasonal_function gsf ON g.id = gsf.gene_id
    GROUP BY g.id
"""
all_genes = pd.read_sql(all_query, conn)

if category != "All":
    all_genes = all_genes[all_genes['category'] == category]

st.dataframe(all_genes, use_container_width=True)