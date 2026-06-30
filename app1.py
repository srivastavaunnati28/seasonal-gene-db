import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px

# ════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Seasonal Physiology Gene Database | Search Circadian & Seasonal Genes",
    page_icon="🧬",
    layout="wide"
)

# ════════════════════════════════════════════════════════════════
# CUSTOM CSS — Dark glassmorphism theme
# ════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at 20% 20%, #0f1b3d 0%, #050814 50%, #0a0118 100%);
    }

    /* Glass card */
    .glass-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 212, 180, 0.25);
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        border-color: rgba(0, 212, 180, 0.6);
        box-shadow: 0 8px 32px rgba(0, 212, 180, 0.15);
    }

    /* Header gradient title */
    .hero-title {
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(90deg, #00d4b4, #60a5fa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 4px;
        letter-spacing: -1px;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 16px;
        margin-bottom: 20px;
    }

    /* Source badge buttons */
    .source-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 24px;
        padding: 6px 16px;
        margin: 4px 6px 4px 0;
        font-size: 13px;
        color: #e2e8f0;
        cursor: pointer;
        transition: all 0.25s ease;
    }
    .source-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,212,180,0.3);
    }

    /* Season pills */
    .season-pill {
        border-radius: 14px;
        padding: 16px;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.03);
        padding: 6px;
        border-radius: 14px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #94a3b8;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, rgba(0,212,180,0.2), rgba(96,165,250,0.2));
        color: #00d4b4 !important;
    }

    /* Inputs */
    .stTextInput input, .stSelectbox > div > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(0,212,180,0.3) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
    }

    /* Buttons */
    .stButton button, .stFormSubmitButton button {
        background: linear-gradient(90deg, #00d4b4, #00a896) !important;
        color: #050814 !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: none !important;
        transition: all 0.25s ease !important;
    }
    .stButton button:hover, .stFormSubmitButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,212,180,0.4) !important;
    }

    /* DataFrames */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* Caption / text */
    p, .stMarkdown, .stCaption { color: #cbd5e1; }

    /* Divider glow */
    hr { border-color: rgba(0,212,180,0.2) !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"],
        port=int(st.secrets["DB_PORT"]),
        ssl_disabled=False
    )

conn = get_connection()

_setup_cursor = conn.cursor()
_setup_cursor.execute("""
CREATE TABLE IF NOT EXISTS community_contributions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    gene_symbol VARCHAR(30) NOT NULL,
    season_or_condition VARCHAR(20),
    expression_level VARCHAR(10),
    fold_change DECIMAL(6,3),
    functional_role TEXT,
    pathway VARCHAR(200),
    tissue_type VARCHAR(150),
    source_db VARCHAR(30),
    source_reference VARCHAR(300),
    contributor_name VARCHAR(100),
    contributor_note TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")
conn.commit()

# ════════════════════════════════════════════════════════════════
# SOURCE DATABASE INFO — used for clickable badges
# ════════════════════════════════════════════════════════════════
SOURCE_INFO = {
    "NCBI": {
        "icon": "🧬",
        "url": "https://www.ncbi.nlm.nih.gov/gene",
        "desc": "National Center for Biotechnology Information. Provides authoritative gene identity, chromosomal location, and official gene summaries for organisms including humans."
    },
    "CircaDB": {
        "icon": "🕐",
        "url": "http://circadb.hogeneschlab.org/",
        "desc": "A curated database of genome-wide circadian/diurnal gene expression data across multiple tissues, used to identify genes with rhythmic expression patterns."
    },
    "PubMed": {
        "icon": "📄",
        "url": "https://pubmed.ncbi.nlm.nih.gov/",
        "desc": "A free search engine for biomedical literature from MEDLINE, life science journals, and online books — the primary source of peer-reviewed evidence behind functional claims."
    },
    "GEO Datasets": {
        "icon": "📊",
        "url": "https://www.ncbi.nlm.nih.gov/geo/",
        "desc": "Gene Expression Omnibus — a public repository of high-throughput functional genomics data, including microarray and RNA-seq experiments on seasonal/photoperiod conditions."
    },
    "UniProt": {
        "icon": "🧪",
        "url": "https://www.uniprot.org/",
        "desc": "A comprehensive resource of protein sequence and functional information, including post-translational modifications and pathway involvement."
    },
}

# ════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════
st.markdown('<div class="hero-title">🧬 Seasonal Physiology Gene Database</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">A public, community-curated database of gene expression across seasons and photoperiods (short-day / long-day)</div>', unsafe_allow_html=True)
st.caption("M.Sc. Bioinformatics Research Project | Unnati Srivastava, University of Allahabad")

# ── Clickable source badges with expandable info ──────────────────
st.markdown("##### 🔗 Data Sources — click to learn more")
badge_cols = st.columns(len(SOURCE_INFO))
for col, (name, info) in zip(badge_cols, SOURCE_INFO.items()):
    with col:
        with st.popover(f"{info['icon']} {name}", use_container_width=True):
            st.markdown(f"**{info['icon']} {name}**")
            st.write(info["desc"])
            st.markdown(f"[Visit {name} →]({info['url']})")

st.divider()

tab_search, tab_contribute, tab_browse = st.tabs(["🔍 Search", "✍️ Contribute Data", "🗂 Browse All Genes"])

# ════════════════════════════════════════════════════════════════
# TAB 1 — SEARCH
# ════════════════════════════════════════════════════════════════
with tab_search:
    gene_input = st.text_input("Search Gene Symbol",
                                placeholder="e.g. CLOCK, VDR, IL6, LEP, SLC6A4")

    if gene_input:
        symbol = gene_input.upper().strip()

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
        df = pd.read_sql(query, conn, params=[symbol])

        if not df.empty:
            st.markdown(f"""
            <div class="glass-card">
                <h3 style="color:#00d4b4; margin:0;">✅ {df['full_name'][0]}</h3>
                <p style="color:#94a3b8; margin:4px 0 0 0;">Category: {df['category'][0]} &nbsp;|&nbsp; Symbol: {symbol}</p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(df, x='season', y='fold_change', color='season',
                    color_discrete_map={'Winter': '#60a5fa', 'Spring': '#4ade80',
                                         'Summer': '#f59e0b', 'Autumn': '#f87171'},
                    title=f"{symbol} — Seasonal Expression")
                fig.update_layout(
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#e2e8f0',
                    title_font_color='#e2e8f0'
                )
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                icons = {'Winter': '❄️', 'Spring': '🌱', 'Summer': '☀️', 'Autumn': '🍂'}
                pill_colors = {'Winter': '#60a5fa22', 'Spring': '#4ade8022', 'Summer': '#f59e0b22', 'Autumn': '#f8717122'}
                expr_colors = {'HIGH': '🔴', 'NORMAL': '🟡', 'LOW': '🟢'}
                for _, row in df.iterrows():
                    st.markdown(f"""
                    <div class="season-pill" style="background:{pill_colors[row['season']]}; margin-bottom:8px;">
                        <b>{icons[row['season']]} {row['season']}</b> —
                        {expr_colors[row['expression_level']]} {row['expression_level']} | {row['fold_change']}x
                        <br><span style="color:#94a3b8; font-size:13px;">{row['functional_role']}</span>
                    </div>
                    """, unsafe_allow_html=True)

            st.dataframe(df[['season','expression_level','fold_change','pathway','tissue_type','study_reference']],
                         use_container_width=True)
        else:
            st.info(f"No curated data yet for '{symbol}'. Check the Contribute tab to add it, or Browse All Genes below.")

        comm_query = """
            SELECT season_or_condition, expression_level, fold_change,
                   functional_role, pathway, tissue_type, source_db,
                   source_reference, contributor_name, submitted_at
            FROM community_contributions
            WHERE gene_symbol = %s
            ORDER BY submitted_at DESC
        """
        comm_df = pd.read_sql(comm_query, conn, params=[symbol])
        if not comm_df.empty:
            st.divider()
            st.markdown("### 🌍 Community-Contributed Data")
            st.caption("Submitted directly by users — not independently verified by the project author.")
            st.dataframe(comm_df, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# TAB 2 — CONTRIBUTE
# ════════════════════════════════════════════════════════════════
with tab_contribute:
    st.markdown("### Add Your Own Curated Data")
    st.caption("Submissions are published immediately and are not reviewed before appearing publicly. "
               "Please cite a real source (NCBI, CircaDB, PubMed, GEO, or UniProt) wherever possible.")

    with st.form("contribute_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            f_gene = st.text_input("Gene Symbol *", placeholder="e.g. PER2")
            f_condition = st.selectbox("Season / Condition *",
                ["Winter", "Spring", "Summer", "Autumn", "SD (Short-Day)", "LD (Long-Day)"])
            f_expression = st.selectbox("Expression Level *", ["HIGH", "NORMAL", "LOW"])
            f_fold = st.number_input("Fold Change", min_value=0.0, max_value=20.0, value=1.0, step=0.1)
        with c2:
            f_pathway = st.text_input("Pathway", placeholder="e.g. Circadian Rhythm")
            f_tissue = st.text_input("Tissue Type", placeholder="e.g. Liver, SCN")
            f_source_db = st.selectbox("Source Database *",
                ["NCBI", "CircaDB", "PubMed", "GEO Datasets", "UniProt", "Other"])
            f_source_ref = st.text_input("Source Reference *", placeholder="PMID, GEO accession, or URL")

        f_role = st.text_area("Functional Role / Notes", placeholder="Describe the gene's seasonal/photoperiod role...")
        f_contributor = st.text_input("Your Name (optional)", placeholder="Anonymous if left blank")

        submitted = st.form_submit_button("Submit Contribution")

        if submitted:
            if not f_gene or not f_source_ref:
                st.error("Gene Symbol and Source Reference are required.")
            else:
                ins_cursor = conn.cursor()
                ins_cursor.execute("""
                    INSERT INTO community_contributions
                    (gene_symbol, season_or_condition, expression_level, fold_change,
                     functional_role, pathway, tissue_type, source_db, source_reference,
                     contributor_name)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    f_gene.upper().strip(), f_condition, f_expression, f_fold,
                    f_role, f_pathway, f_tissue, f_source_db, f_source_ref,
                    f_contributor if f_contributor else "Anonymous"
                ))
                conn.commit()
                st.success(f"✅ Thank you! Your data for {f_gene.upper()} is now live and publicly visible.")
                st.balloons()

    st.divider()
    st.markdown("### Recent Community Submissions")
    recent_query = """
        SELECT gene_symbol, season_or_condition, expression_level, source_db,
               contributor_name, submitted_at
        FROM community_contributions
        ORDER BY submitted_at DESC
        LIMIT 15
    """
    recent_df = pd.read_sql(recent_query, conn)
    if not recent_df.empty:
        st.dataframe(recent_df, use_container_width=True)
    else:
        st.caption("No community submissions yet. Be the first!")

# ════════════════════════════════════════════════════════════════
# TAB 3 — BROWSE
# ════════════════════════════════════════════════════════════════
with tab_browse:
    category_filter = st.selectbox("Filter by category",
        ["All", "Circadian", "Hormonal", "Immune", "Metabolic", "Mood/Brain", "Other"])

    all_query = "SELECT gene_symbol, full_name, category, chromosome, organism FROM genes ORDER BY gene_symbol"
    all_genes = pd.read_sql(all_query, conn)
    if category_filter != "All":
        all_genes = all_genes[all_genes['category'] == category_filter]
    st.dataframe(all_genes, use_container_width=True)
    st.caption(f"Showing {len(all_genes)} genes")

# ════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════
st.divider()
st.markdown("""
<div style="text-align:center; padding: 16px 0;">
    <p style="color:#64748b; font-size:13px;">
        Data sources: NCBI Gene · CircaDB · GEO Datasets · UniProt · PubMed · Community contributions
    </p>
    <p style="color:#475569; font-size:12px;">
        This is an open, publicly editable research database. Data accuracy of community contributions is not independently verified.
    </p>
</div>
""", unsafe_allow_html=True)
