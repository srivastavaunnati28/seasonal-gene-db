import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px

# ════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Seasonal Physiology Gene Database | NCBI-linked Research Resource",
    page_icon="🧬",
    layout="wide"
)

# ════════════════════════════════════════════════════════════════
# CSS — Clean white/light scientific journal style
# ════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    .main-header { border-bottom: 3px solid #1a5276; padding-bottom: 12px; margin-bottom: 4px; }
    .main-title { font-size: 30px; font-weight: 700; color: #1a5276; margin: 0; }
    .main-subtitle { font-size: 15px; color: #444; margin-top: 4px; }
    .affil { font-size: 13px; color: #777; font-style: italic; }
    .section-header {
        font-size: 18px; font-weight: 700; color: #1a5276;
        border-left: 4px solid #1a5276; padding-left: 10px; margin: 18px 0 10px 0;
    }
    .result-box {
        background: #f8f9fa; border: 1px solid #d0d7de; border-radius: 6px;
        padding: 18px 20px; margin-bottom: 14px;
    }
    .gene-name { font-size: 24px; font-weight: 800; color: #0b3d61; }
    .gene-meta { font-size: 13px; color: #555; margin-top: 2px; }
    .photo-card { border-radius: 6px; padding: 14px; border: 1px solid #d0d7de; height: 100%; }
    .photo-card-sd { background: #eef3fb; border-left: 4px solid #2c5f8a; }
    .photo-card-ld { background: #fff8ee; border-left: 4px solid #c97a1c; }
    .photo-card-season { background: #eef9f1; border-left: 4px solid #2e8b57; }
    .photo-label { font-weight: 700; font-size: 14px; color: #1a1a1a; margin-bottom: 4px; }
    .photo-value { font-size: 13px; color: #333; line-height: 1.5; }
    .tier-badge {
        display: inline-block; padding: 4px 12px; border-radius: 4px;
        font-size: 12px; font-weight: 700; margin-bottom: 10px;
    }
    .tier-1 { background: #d4edda; color: #155724; border: 1px solid #28a745; }
    .tier-2 { background: #fff3cd; color: #856404; border: 1px solid #ffc107; }
    .stTabs [data-baseweb="tab-list"] { border-bottom: 2px solid #d0d7de; }
    .stTabs [data-baseweb="tab"] { color: #555; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #1a5276 !important; border-bottom: 3px solid #1a5276 !important; }
    [data-testid="stDataFrame"] { border: 1px solid #d0d7de; border-radius: 6px; }
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
setup_cursor = conn.cursor()

setup_cursor.execute("""
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

try:
    setup_cursor.execute("ALTER TABLE gene_seasonal_function ADD COLUMN photoperiod_condition VARCHAR(5) DEFAULT NULL")
    conn.commit()
except mysql.connector.Error:
    conn.rollback()

conn.commit()

SEASON_TO_PHOTOPERIOD = {"Winter": "SD", "Summer": "LD", "Spring": "INT", "Autumn": "INT"}

SOURCE_INFO = {
    "NCBI": {"url": "https://www.ncbi.nlm.nih.gov/gene", "desc": "Gene identity, chromosomal location, and official summaries."},
    "CircaDB": {"url": "http://circadb.hogeneschlab.org/", "desc": "Genome-wide circadian/diurnal expression across tissues."},
    "PubMed": {"url": "https://pubmed.ncbi.nlm.nih.gov/", "desc": "Peer-reviewed literature evidence for functional claims."},
    "GEO Datasets": {"url": "https://www.ncbi.nlm.nih.gov/geo/", "desc": "Raw high-throughput expression datasets (microarray/RNA-seq)."},
    "UniProt": {"url": "https://www.uniprot.org/", "desc": "Protein function, pathways, post-translational modification."},
}

# ════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════
st.markdown("""
<div class="main-header">
    <p class="main-title">🧬 Seasonal Physiology Gene Database</p>
    <p class="main-subtitle">A photoperiod- and season-linked gene expression resource, cross-referenced with NCBI, CircaDB, PubMed, GEO Datasets, and UniProt.</p>
</div>
""", unsafe_allow_html=True)

with st.expander("ℹ️ About this database — data tiers explained"):
    st.markdown("""
    Every gene in this database is searchable, but **not every gene has the same depth of data** —
    and this database is explicit about that distinction rather than hiding it:

    - 🟢 **Tier 1 — Curated seasonal/photoperiod data:** A focused set of well-characterized genes
      with manually verified fold-change values, expression levels, and functional roles across
      seasons (Winter/Spring/Summer/Autumn) and photoperiod conditions (SD/LD), each backed by a
      specific cited paper (PMID).
    - 🟡 **Tier 2 — NCBI reference data:** All other genes in the database have real, automatically
      fetched NCBI summaries and linked PubMed articles, but **do not yet have curated seasonal
      fold-change values** — those numbers don't exist in any retrievable database and would need
      to be manually extracted from specific experiments to be added responsibly.

    This separation exists so that no number is presented as scientific fact unless it is genuinely
    sourced. Community contributors (see the Contribute tab) can help expand Tier 1 over time.
    """)

st.markdown('<div class="section-header">🔗 Linked Data Sources</div>', unsafe_allow_html=True)
src_cols = st.columns(len(SOURCE_INFO))
for col, (name, info) in zip(src_cols, SOURCE_INFO.items()):
    with col:
        with st.popover(name, use_container_width=True):
            st.markdown(f"**{name}**")
            st.write(info["desc"])
            st.markdown(f"[Visit official site →]({info['url']})")

tab_search, tab_contribute, tab_browse = st.tabs(["🔍 Search", "✍️ Contribute Data", "🗂 Browse All Genes"])

# ════════════════════════════════════════════════════════════════
# TAB 1 — SEARCH (tiered: curated seasonal data OR NCBI reference)
# ════════════════════════════════════════════════════════════════
with tab_search:
    gene_input = st.text_input("Search Gene Symbol",
                                placeholder="e.g. CLOCK, VDR, IL6, LEP, SLC6A4, or any gene in the database")

    if gene_input:
        symbol = gene_input.upper().strip()

        # ── Check Tier 1: curated seasonal data ────────────────
        query = """
            SELECT g.gene_symbol, g.full_name, g.category,
                   s.name AS season, gsf.expression_level,
                   gsf.fold_change, gsf.functional_role,
                   gsf.pathway, gsf.tissue_type, gsf.study_reference,
                   gsf.photoperiod_condition
            FROM gene_seasonal_function gsf
            JOIN genes g ON gsf.gene_id = g.id
            JOIN seasons s ON gsf.season_id = s.id
            WHERE g.gene_symbol = %s
            ORDER BY FIELD(s.name, 'Winter','Spring','Summer','Autumn')
        """
        df = pd.read_sql(query, conn, params=[symbol])

        if not df.empty:
            # ───────────── TIER 1 RESULT ─────────────
            st.markdown('<span class="tier-badge tier-1">🟢 TIER 1 — Curated Seasonal Data</span>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="result-box">
                <span class="gene-name">{symbol}</span>
                <div class="gene-meta">{df['full_name'][0]} &nbsp;·&nbsp; Category: {df['category'][0]}</div>
            </div>
            """, unsafe_allow_html=True)

            df['photoperiod_condition'] = df.apply(
                lambda r: r['photoperiod_condition'] if r['photoperiod_condition']
                else SEASON_TO_PHOTOPERIOD.get(r['season'], 'INT'),
                axis=1
            )
            sd_rows = df[df['photoperiod_condition'] == 'SD']
            ld_rows = df[df['photoperiod_condition'] == 'LD']

            st.markdown('<div class="section-header">Photoperiod & Season Comparison</div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown('<div class="photo-card photo-card-sd">', unsafe_allow_html=True)
                st.markdown('<div class="photo-label">❄️ Short-Day (SD)</div>', unsafe_allow_html=True)
                if not sd_rows.empty:
                    for _, r in sd_rows.iterrows():
                        st.markdown(f"""<div class="photo-value"><b>{r['expression_level']}</b> ({r['fold_change']}x)<br>{r['functional_role']}<br><i>Tissue: {r['tissue_type']}</i></div>""", unsafe_allow_html=True)
                else:
                    st.markdown('<div class="photo-value">No SD-specific data.</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="photo-card photo-card-ld">', unsafe_allow_html=True)
                st.markdown('<div class="photo-label">☀️ Long-Day (LD)</div>', unsafe_allow_html=True)
                if not ld_rows.empty:
                    for _, r in ld_rows.iterrows():
                        st.markdown(f"""<div class="photo-value"><b>{r['expression_level']}</b> ({r['fold_change']}x)<br>{r['functional_role']}<br><i>Tissue: {r['tissue_type']}</i></div>""", unsafe_allow_html=True)
                else:
                    st.markdown('<div class="photo-value">No LD-specific data.</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with c3:
                st.markdown('<div class="photo-card photo-card-season">', unsafe_allow_html=True)
                st.markdown('<div class="photo-label">📅 By Season</div>', unsafe_allow_html=True)
                season_icons = {'Winter':'❄️','Spring':'🌱','Summer':'☀️','Autumn':'🍂'}
                for _, r in df.iterrows():
                    st.markdown(f"""<div class="photo-value">{season_icons.get(r['season'],'')} <b>{r['season']}</b>: {r['expression_level']} ({r['fold_change']}x)</div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            fig = px.bar(df, x='season', y='fold_change', color='season',
                color_discrete_map={'Winter': '#2c5f8a', 'Spring': '#2e8b57', 'Summer': '#c97a1c', 'Autumn': '#a14a4a'},
                title=f"{symbol} — Fold Change by Season")
            fig.update_layout(showlegend=False, plot_bgcolor='white', paper_bgcolor='white', font_color='#1a1a1a')
            st.plotly_chart(fig, use_container_width=True)

            st.markdown('<div class="section-header">Full Data Table</div>', unsafe_allow_html=True)
            st.dataframe(df[['season','photoperiod_condition','expression_level','fold_change','pathway','tissue_type','study_reference']]
                .rename(columns={'season':'Season','photoperiod_condition':'Photoperiod','expression_level':'Expression',
                                  'fold_change':'Fold Change','pathway':'Pathway','tissue_type':'Tissue','study_reference':'Reference (PMID)'}),
                use_container_width=True)

        else:
            # ───────────── TIER 2: check genes table ─────────────
            gene_query = "SELECT id, gene_symbol, full_name, category, summary, ncbi_gene_id, uniprot_id FROM genes WHERE gene_symbol = %s"
            gene_df = pd.read_sql(gene_query, conn, params=[symbol])

            if not gene_df.empty:
                row = gene_df.iloc[0]
                st.markdown('<span class="tier-badge tier-2">🟡 TIER 2 — NCBI Reference Data</span>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="result-box">
                    <span class="gene-name">{symbol}</span>
                    <div class="gene-meta">{row['full_name']} &nbsp;·&nbsp; Category: {row['category']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.caption("No curated seasonal fold-change data exists yet for this gene. "
                           "Showing real NCBI/PubMed reference information instead.")

                if row['summary']:
                    st.markdown('<div class="section-header">NCBI Gene Summary</div>', unsafe_allow_html=True)
                    st.write(row['summary'])

                if row['ncbi_gene_id']:
                    st.markdown(f"[View full NCBI Gene record →](https://www.ncbi.nlm.nih.gov/gene/{row['ncbi_gene_id']})")
                if row['uniprot_id']:
                    st.markdown(f"[View UniProt entry →](https://www.uniprot.org/uniprotkb/{row['uniprot_id']})")

                pubmed_query = "SELECT pmid, title, journal, pub_year FROM gene_pubmed_links WHERE gene_id = %s ORDER BY pub_year DESC"
                try:
                    pubmed_df = pd.read_sql(pubmed_query, conn, params=[int(row['id'])])
                except Exception:
                    pubmed_df = pd.DataFrame()

                if not pubmed_df.empty:
                    st.markdown('<div class="section-header">📄 Linked PubMed Articles</div>', unsafe_allow_html=True)
                    for _, p in pubmed_df.iterrows():
                        st.markdown(f"- [{p['title']}](https://pubmed.ncbi.nlm.nih.gov/{p['pmid']}/) — *{p['journal']}* ({p['pub_year']})")
                else:
                    st.caption("No linked PubMed articles found yet for this gene.")

                st.info("Want to help fill this gap? Use the **Contribute Data** tab to add curated "
                        "seasonal/photoperiod values for this gene with a citation.")
            else:
                st.warning(f"'{symbol}' was not found in the database. Check spelling, or browse all available genes in the **Browse All Genes** tab.")

        # ── Community contributions (always shown if present) ──
        comm_query = """
            SELECT season_or_condition AS "Season/Condition", expression_level AS "Expression",
                   fold_change AS "Fold Change", functional_role AS "Functional Role",
                   pathway AS "Pathway", tissue_type AS "Tissue", source_db AS "Source DB",
                   source_reference AS "Reference", contributor_name AS "Contributor", submitted_at AS "Submitted"
            FROM community_contributions WHERE gene_symbol = %s ORDER BY submitted_at DESC
        """
        comm_df = pd.read_sql(comm_query, conn, params=[symbol])
        if not comm_df.empty:
            st.markdown('<div class="section-header">🌍 Community-Contributed Data</div>', unsafe_allow_html=True)
            st.caption("Submitted directly by users — not independently verified by the project author.")
            st.dataframe(comm_df, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# TAB 2 — CONTRIBUTE
# ════════════════════════════════════════════════════════════════
with tab_contribute:
    st.markdown('<div class="section-header">Add Your Own Curated Data</div>', unsafe_allow_html=True)
    st.caption("Submissions are published immediately and are not reviewed before appearing publicly. "
               "Please cite a real source (NCBI, CircaDB, PubMed, GEO, or UniProt) wherever possible.")

    with st.form("contribute_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            f_gene = st.text_input("Gene Symbol *", placeholder="e.g. PER2")
            f_condition = st.selectbox("Season / Photoperiod Condition *",
                ["Winter (SD)", "Spring (Intermediate)", "Summer (LD)", "Autumn (Intermediate)",
                 "SD (Short-Day, general)", "LD (Long-Day, general)"])
            f_expression = st.selectbox("Expression Level *", ["HIGH", "NORMAL", "LOW"])
            f_fold = st.number_input("Fold Change", min_value=0.0, max_value=20.0, value=1.0, step=0.1)
        with c2:
            f_pathway = st.text_input("Pathway", placeholder="e.g. Circadian Rhythm")
            f_tissue = st.text_input("Tissue Type", placeholder="e.g. Liver, SCN")
            f_source_db = st.selectbox("Source Database *", ["NCBI", "CircaDB", "PubMed", "GEO Datasets", "UniProt", "Other"])
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
                    (gene_symbol, season_or_condition, expression_level, fold_change, functional_role,
                     pathway, tissue_type, source_db, source_reference, contributor_name)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (f_gene.upper().strip(), f_condition, f_expression, f_fold, f_role, f_pathway,
                      f_tissue, f_source_db, f_source_ref, f_contributor if f_contributor else "Anonymous"))
                conn.commit()
                st.success(f"Thank you. Your data for {f_gene.upper()} is now live and publicly visible.")

    st.markdown('<div class="section-header">Recent Community Submissions</div>', unsafe_allow_html=True)
    recent_query = """
        SELECT gene_symbol AS "Gene", season_or_condition AS "Condition", expression_level AS "Expression",
               source_db AS "Source", contributor_name AS "Contributor", submitted_at AS "Submitted"
        FROM community_contributions ORDER BY submitted_at DESC LIMIT 15
    """
    recent_df = pd.read_sql(recent_query, conn)
    if not recent_df.empty:
        st.dataframe(recent_df, use_container_width=True)
    else:
        st.caption("No community submissions yet.")

# ════════════════════════════════════════════════════════════════
# TAB 3 — BROWSE (shows tier for every gene)
# ════════════════════════════════════════════════════════════════
with tab_browse:
    category_filter = st.selectbox("Filter by category",
        ["All", "Circadian", "Hormonal", "Immune", "Metabolic", "Mood/Brain", "Other"])

    browse_query = """
        SELECT g.gene_symbol AS Symbol, g.full_name AS "Full Name", g.category AS Category,
               g.chromosome AS Chromosome,
               CASE WHEN gsf.id IS NOT NULL THEN 'Tier 1 (Curated)' ELSE 'Tier 2 (NCBI Reference)' END AS "Data Tier"
        FROM genes g
        LEFT JOIN gene_seasonal_function gsf ON gsf.gene_id = g.id
        GROUP BY g.id, g.gene_symbol, g.full_name, g.category, g.chromosome, "Data Tier"
        ORDER BY g.gene_symbol
    """
    all_genes = pd.read_sql(browse_query, conn)
    if category_filter != "All":
        all_genes = all_genes[all_genes['Category'] == category_filter]
    st.dataframe(all_genes, use_container_width=True)
    st.caption(f"Showing {len(all_genes)} genes — every gene is searchable in the Search tab regardless of tier.")

# ════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════
st.divider()
st.caption("Data sources: NCBI Gene · CircaDB · GEO Datasets · UniProt · PubMed · Community contributions")
st.caption("This is an open, publicly editable research database. Data accuracy of community contributions is not independently verified.")
