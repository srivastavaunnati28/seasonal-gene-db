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

# Database connection (uses Streamlit Secrets)
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

# Header
st.title("🧬 Seasonal Physiology Gene Database")
st.markdown("**Search genes → See seasonal expression roles**")
st.caption("DBT Research Project | Unnati Srivastava")
st.divider()

# Search + filter row
col1, col2 = st.columns([3, 1])
with col1:
    gene_input = st.text_input("🔍 Search Gene Symbol",
                                placeholder="e.g. CLOCK, VDR, IL6, LEP, SLC6A4")
with col2:
    category_filter = st.selectbox("Category",
                ["All", "Circadian", "Hormonal", "Immune", "Metabolic", "Mood/Brain"])

# ── Search result for a specific gene ──────────────────────────
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
        ORDER BY FIELD(s.name, 'Winter','Spring','Summer','Autumn')
    """
    df = pd.read_sql(query, conn, params=[gene_input.upper()])

    if not df.empty:
        st.success(f"✅ Found: **{df['full_name'][0]}**  |  Category: {df['category'][0]}")

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
                        title=f"{gene_input.upper()} — Seasonal Expression",
                        labels={'fold_change': 'Fold Change', 'season': 'Season'})
            fig.update_layout(showlegend=False,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Seasonal Roles")
            icons = {'Winter': '❄️', 'Spring': '🌱', 'Summer': '☀️', 'Autumn': '🍂'}
            expr_colors = {'HIGH': '🔴', 'NORMAL': '🟡', 'LOW': '🟢'}
            for _, row in df.iterrows():
                st.markdown(f"""
**{icons[row['season']]} {row['season']}** — {expr_colors[row['expression_level']]} {row['expression_level']} | Fold: {row['fold_change']}x
> {row['functional_role']}
                """)

        st.divider()
        st.markdown("### 📊 Full Data Table")
        st.dataframe(
            df[['season', 'expression_level', 'fold_change',
                'pathway', 'tissue_type', 'study_reference']],
            use_container_width=True
        )

        csv = df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name=f"{gene_input.upper()}_seasonal_data.csv",
            mime="text/csv"
        )
    else:
        st.warning("Gene not found! Try: CLOCK, VDR, IL6, LEP, SLC6A4, BMAL1, CRY1, TNF, UCP1, AANAT")

# ── All genes table (browse + filter) ───────────────────────────
st.divider()
st.markdown("### 🗂 All Genes in Database")

all_query = """
    SELECT g.gene_symbol, g.full_name, g.category, g.chromosome, g.organism
    FROM genes g
    ORDER BY g.gene_symbol
"""
all_genes = pd.read_sql(all_query, conn)

if category_filter != "All":
    all_genes = all_genes[all_genes['category'] == category_filter]

st.dataframe(all_genes, use_container_width=True)

# ── Footer ───────────────────────────────────────────────────────
st.divider()
st.caption("Data sources: NCBI Gene · CircaDB · GEO Datasets · UniProt · PubMed references included per entry")
