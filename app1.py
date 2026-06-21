import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
from ncbi_live_search import full_live_lookup

# ── Page config (also helps with browser tab title for SEO) ────────
st.set_page_config(
    page_title="Seasonal Physiology Gene Database | Search Circadian & Seasonal Genes",
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
        port=int(st.secrets["DB_PORT"]),
        ssl_disabled=False
    )

conn = get_connection()

# Make sure community table exists (safe to re-run)
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

# Make sure ncbi_cache table exists (stores live NCBI/GEO lookups so we don't
# hit the API again for the same gene every time someone searches it)
_setup_cursor.execute("""
CREATE TABLE IF NOT EXISTS ncbi_cache (
    id INT AUTO_INCREMENT PRIMARY KEY,
    gene_symbol VARCHAR(30) NOT NULL UNIQUE,
    full_name VARCHAR(500),
    organism VARCHAR(150),
    chromosome VARCHAR(50),
    summary TEXT,
    ncbi_url VARCHAR(300),
    geo_datasets_json TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")
conn.commit()
_setup_cursor.close()

# ── Header ────────────────────────────────────────────────────────
st.title("🧬 Seasonal Physiology Gene Database")
st.markdown("**A public, community-curated database of gene expression across seasons and photoperiods (short-day / long-day)**")
st.caption("Research Project | Unnati Srivastava, University of Allahabad")
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

        # Curated seasonal data
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
            st.success(f"✅ Curated data found: **{df['full_name'][0]}** | {df['category'][0]}")
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(df, x='season', y='fold_change', color='season',
                    color_discrete_map={'Winter': '#60a5fa', 'Spring': '#4ade80',
                                         'Summer': '#f59e0b', 'Autumn': '#f87171'},
                    title=f"{symbol} — Seasonal Expression")
                fig.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                icons = {'Winter': '❄️', 'Spring': '🌱', 'Summer': '☀️', 'Autumn': '🍂'}
                expr_colors = {'HIGH': '🔴', 'NORMAL': '🟡', 'LOW': '🟢'}
                for _, row in df.iterrows():
                    st.markdown(f"**{icons[row['season']]} {row['season']}** — "
                                f"{expr_colors[row['expression_level']]} {row['expression_level']} | "
                                f"{row['fold_change']}x\n> {row['functional_role']}")
            st.dataframe(df[['season','expression_level','fold_change','pathway','tissue_type','study_reference']],
                         use_container_width=True)
        else:
            st.info(f"No curated data yet for '{symbol}'. Searching NCBI Gene & GEO live...")

            # ── Live NCBI fallback (cache-first) ──────────────────────
            cache_cursor = conn.cursor(dictionary=True)
            cache_cursor.execute(
                "SELECT * FROM ncbi_cache WHERE gene_symbol = %s", (symbol,)
            )
            cached = cache_cursor.fetchone()
            cache_cursor.close()

            import json as _json

            if cached:
                gene_info = {
                    "symbol": cached["gene_symbol"],
                    "full_name": cached["full_name"],
                    "organism": cached["organism"],
                    "chromosome": cached["chromosome"],
                    "summary": cached["summary"],
                    "ncbi_url": cached["ncbi_url"],
                }
                geo_datasets = _json.loads(cached["geo_datasets_json"] or "[]")
                st.caption(f"📦 Loaded from cache (first fetched {cached['fetched_at']})")
            else:
                with st.spinner("Querying NCBI..."):
                    live_result = full_live_lookup(symbol)
                gene_info = live_result["gene_info"]
                geo_datasets = live_result["geo_datasets"]

                # Save to cache for next time, if we found something
                if gene_info:
                    save_cursor = conn.cursor()
                    save_cursor.execute("""
                        INSERT INTO ncbi_cache
                            (gene_symbol, full_name, organism, chromosome, summary, ncbi_url, geo_datasets_json)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                        ON DUPLICATE KEY UPDATE
                            full_name=VALUES(full_name), organism=VALUES(organism),
                            chromosome=VALUES(chromosome), summary=VALUES(summary),
                            ncbi_url=VALUES(ncbi_url), geo_datasets_json=VALUES(geo_datasets_json),
                            fetched_at=CURRENT_TIMESTAMP
                    """, (
                        symbol, gene_info["full_name"], gene_info["organism"],
                        gene_info["chromosome"], gene_info["summary"], gene_info["ncbi_url"],
                        _json.dumps(geo_datasets)
                    ))
                    conn.commit()
                    save_cursor.close()

            if not gene_info:
                st.error(
                    f"'{symbol}' was not found in the local database or on NCBI Gene. "
                    "Check the spelling, or add it yourself in the Contribute tab."
                )
            else:
                st.success(f"🌐 Found via NCBI Gene: **{gene_info['symbol']}**")
                gcol1, gcol2 = st.columns([2, 1])
                with gcol1:
                    st.write(f"**Full name:** {gene_info['full_name']}")
                    st.write(f"**Organism:** {gene_info['organism']}")
                    st.write(f"**Summary:** {gene_info['summary'] or 'No summary available.'}")
                with gcol2:
                    st.write(f"**Chromosome:** {gene_info['chromosome']}")
                    st.markdown(f"[🔗 View full record on NCBI Gene]({gene_info['ncbi_url']})")

                st.markdown("##### Related GEO datasets (Short-Day / Long-Day / Photoperiod)")
                if geo_datasets:
                    for ds in geo_datasets:
                        with st.container(border=True):
                            st.markdown(f"**{ds['accession']}** — {ds['title']}")
                            st.caption(f"Organism: {ds['organism']} | Samples: {ds['n_samples']}")
                            st.write(ds['summary'] + ("..." if ds['summary'] else ""))
                            st.markdown(f"[View dataset on GEO]({ds['geo_url']})")
                    st.caption(
                        "⚠️ These are related GEO series, not auto-extracted numeric SD/LD expression values. "
                        "Open a dataset above to inspect actual values, then add a curated entry via the Contribute tab."
                    )
                else:
                    st.warning("No related short-day/long-day GEO datasets found for this gene.")

        # Community contributions for this gene (always shown, clearly labeled)
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

# ── Footer ───────────────────────────────────────────────────────
st.divider()
st.caption("Data sources: NCBI Gene · CircaDB · GEO Datasets · UniProt · PubMed · Community contributions")
st.caption("This is an open, publicly editable research database. Data accuracy of community contributions is not independently verified.")
