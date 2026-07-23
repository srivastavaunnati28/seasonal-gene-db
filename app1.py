import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import time

# ════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Seasonal Physiology Gene Database | NCBI-linked Research Resource",
    page_icon="🧬",
    layout="wide"
)

# ════════════════════════════════════════════════════════════════
# CSS — NCBI-inspired colorful scientific database style
# ════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    .stApp { background-color: #f5f8fb; }

    /* NCBI-style top utility strip */
    .ncbi-topstrip {
        background: #205493;
        color: #ffffff;
        font-size: 12px;
        padding: 5px 16px;
        margin: -1rem -1rem 0 -1rem;
        letter-spacing: .3px;
    }

    /* NCBI-style blue gradient banner */
    .main-header {
        background: linear-gradient(90deg, #1a3a5c 0%, #2c6fad 55%, #3a8fc2 100%);
        border-radius: 8px;
        padding: 22px 26px;
        margin: 10px 0 18px 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }
    .main-title {
        font-size: 30px;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
    }
    .main-subtitle {
        font-size: 14.5px;
        color: #e3edf7;
        margin-top: 6px;
    }
    .affil {
        font-size: 13px;
        color: #cfe0f0;
        font-style: italic;
    }

    /* Section headers - NCBI teal/orange accent style, rotating colors */
    .section-header {
        font-size: 18px;
        font-weight: 800;
        color: #ffffff;
        background: #2c6fad;
        border-left: 6px solid #ff8c1a;
        padding: 8px 14px;
        margin: 20px 0 12px 0;
        border-radius: 4px;
    }

    /* Result panel - NCBI record card look */
    .result-box {
        background: linear-gradient(180deg, #eaf3fc 0%, #ffffff 100%);
        border: 1px solid #a9c9e8;
        border-top: 5px solid #205493;
        border-radius: 8px;
        padding: 18px 22px;
        margin-bottom: 16px;
        box-shadow: 0 1px 4px rgba(32,84,147,0.12);
    }
    .gene-name {
        font-size: 26px;
        font-weight: 900;
        color: #0b3d61;
        letter-spacing: .5px;
    }
    .gene-meta {
        font-size: 13.5px;
        color: #35526e;
        margin-top: 4px;
    }

    /* Photoperiod comparison cards - bright NCBI-esque trio */
    .photo-card {
        border-radius: 8px;
        padding: 14px;
        border: 1px solid #d0d7de;
        height: 100%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .photo-card-sd { background: #e3edfb; border-top: 5px solid #1f5fa8; }
    .photo-card-ld { background: #fff2df; border-top: 5px solid #e8820c; }
    .photo-card-season { background: #e4f7ea; border-top: 5px solid #1f9d55; }

    .photo-label {
        font-weight: 800;
        font-size: 14.5px;
        color: #1a1a1a;
        margin-bottom: 6px;
    }
    .photo-value {
        font-size: 13px;
        color: #2b2b2b;
        line-height: 1.55;
    }

    /* Source badges - colorful NCBI database chips */
    .source-tag {
        display: inline-block;
        background: #eef3fb;
        border: 1px solid #b9cce4;
        border-radius: 4px;
        padding: 3px 10px;
        margin: 2px 4px 2px 0;
        font-size: 12px;
        color: #1a5276;
        font-weight: 700;
    }

    /* Live cross-reference panel */
    .xref-box {
        background: #ffffff;
        border: 1px solid #cfe0f0;
        border-left: 5px solid #205493;
        border-radius: 6px;
        padding: 14px 16px;
        margin: 10px 0 16px 0;
        font-size: 13px;
        color: #263a4d;
        line-height: 1.6;
    }
    .xref-label {
        font-weight: 800;
        color: #205493;
        font-size: 13px;
    }
    .evidence-badge {
        display: inline-block;
        border-radius: 12px;
        padding: 3px 10px;
        font-size: 11px;
        font-weight: 800;
        margin-left: 8px;
    }
    .evidence-single { background: #fdf0e3; color: #9c5a17; border: 1px solid #e6c393; }
    .evidence-replicated { background: #e0f5e6; color: #157a3d; border: 1px solid #9edab3; }

    /* Tabs - NCBI blue underline style */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 3px solid #cfe0f0;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #35526e;
        font-weight: 700;
        background: #eaf3fc;
        border-radius: 6px 6px 0 0;
        padding: 8px 14px;
    }
    .stTabs [aria-selected="true"] {
        color: #ffffff !important;
        background: #205493 !important;
        border-bottom: 3px solid #ff8c1a !important;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #a9c9e8;
        border-radius: 8px;
        overflow: hidden;
    }

    /* Buttons - NCBI orange accent */
    .stButton>button, .stDownloadButton>button, .stFormSubmitButton>button {
        background: #205493 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 5px !important;
        font-weight: 700 !important;
    }
    .stButton>button:hover, .stDownloadButton>button:hover, .stFormSubmitButton>button:hover {
        background: #ff8c1a !important;
        color: #1a1a1a !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #eef3fb;
        border-right: 3px solid #205493;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="ncbi-topstrip">🧬 National-style research resource · cross-referenced live with NCBI, PubMed, CircaDB, GEO &amp; UniProt</div>', unsafe_allow_html=True)


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

# Community table
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

# Add photoperiod_condition column to gene_seasonal_function if missing
# (lets each curated row carry SD / LD / Intermediate alongside its season)
try:
    setup_cursor.execute("""
        ALTER TABLE gene_seasonal_function
        ADD COLUMN photoperiod_condition VARCHAR(5) DEFAULT NULL
    """)
    conn.commit()
except mysql.connector.Error:
    conn.rollback()  # column already exists, safe to ignore

conn.commit()

# Map each season to its typical photoperiod condition (used to backfill
# photoperiod_condition where it hasn't been manually set yet)
SEASON_TO_PHOTOPERIOD = {
    "Winter": "SD",
    "Summer": "LD",
    "Spring": "INT",
    "Autumn": "INT",
}

SOURCE_INFO = {
    "NCBI": {"url": "https://www.ncbi.nlm.nih.gov/gene",
             "desc": "Gene identity, chromosomal location, and official summaries."},
    "CircaDB": {"url": "http://circadb.hogeneschlab.org/",
                "desc": "Genome-wide circadian/diurnal expression across tissues."},
    "PubMed": {"url": "https://pubmed.ncbi.nlm.nih.gov/",
               "desc": "Peer-reviewed literature evidence for functional claims."},
    "GEO Datasets": {"url": "https://www.ncbi.nlm.nih.gov/geo/",
                      "desc": "Raw high-throughput expression datasets (microarray/RNA-seq)."},
    "UniProt": {"url": "https://www.uniprot.org/",
                "desc": "Protein function, pathways, post-translational modification."},
}

# ════════════════════════════════════════════════════════════════
# LIVE NCBI CROSS-REFERENCE (via NCBI E-utilities)
# ════════════════════════════════════════════════════════════════
@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def fetch_ncbi_gene_summary(gene_symbol: str, organism: str = "Homo sapiens"):
    """Look up a gene symbol against live NCBI Gene data.
    Returns None on any failure (network, rate limit, no match) so the
    rest of the app degrades gracefully rather than crashing."""
    try:
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "gene",
            "term": f"{gene_symbol}[sym] AND {organism}[orgn]",
            "retmode": "json",
        }
        r = requests.get(search_url, params=params, timeout=6)
        r.raise_for_status()
        ids = r.json().get("esearchresult", {}).get("idlist", [])
        if not ids:
            return None

        gene_id = ids[0]
        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        params2 = {"db": "gene", "id": gene_id, "retmode": "json"}
        r2 = requests.get(summary_url, params=params2, timeout=6)
        r2.raise_for_status()
        data = r2.json().get("result", {}).get(gene_id, {})
        if not data:
            return None

        return {
            "gene_id": gene_id,
            "official_symbol": data.get("name") or gene_symbol,
            "official_name": data.get("description", ""),
            "summary": data.get("summary", "") or "No summary text available from NCBI for this gene.",
            "chromosome": data.get("chromosome", "N/A"),
            "map_location": data.get("maplocation", "N/A"),
            "ncbi_url": f"https://www.ncbi.nlm.nih.gov/gene/{gene_id}",
        }
    except Exception:
        return None


def uniprot_search_url(gene_symbol: str) -> str:
    return f"https://www.uniprot.org/uniprotkb?query={gene_symbol}+AND+organism_id:9606"


def evidence_badge(n_sources: int) -> str:
    if n_sources >= 2:
        return '<span class="evidence-badge evidence-replicated">Replicated across ≥2 entries</span>'
    return '<span class="evidence-badge evidence-single">Single curated entry</span>'


@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)
def fetch_pubmed_photoperiod_papers(gene_symbol: str, max_results: int = 8):
    """Live PubMed search for papers mentioning this gene alongside
    photoperiod/seasonal/circadian terms. Used as a fallback whenever the
    gene has no curated entry yet, so a search never comes back empty-handed.
    Returns a list of dicts (title, authors, journal, year, url, pmid)."""
    try:
        term = (
            f'{gene_symbol}[Title/Abstract] AND '
            f'(photoperiod[Title/Abstract] OR "short day"[Title/Abstract] OR '
            f'"long day"[Title/Abstract] OR seasonal[Title/Abstract] OR circadian[Title/Abstract])'
        )
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {"db": "pubmed", "term": term, "retmode": "json",
                  "retmax": max_results, "sort": "relevance"}
        r = requests.get(search_url, params=params, timeout=6)
        r.raise_for_status()
        ids = r.json().get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []

        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        params2 = {"db": "pubmed", "id": ",".join(ids), "retmode": "json"}
        r2 = requests.get(summary_url, params=params2, timeout=6)
        r2.raise_for_status()
        result = r2.json().get("result", {})

        papers = []
        for pmid in ids:
            item = result.get(pmid)
            if not item:
                continue
            authors = item.get("authors", [])
            first_author = authors[0]["name"] if authors else "Unknown"
            author_str = f"{first_author} et al." if len(authors) > 1 else first_author
            papers.append({
                "pmid": pmid,
                "title": (item.get("title", "") or "Untitled").rstrip("."),
                "journal": item.get("fulljournalname") or item.get("source", ""),
                "year": (item.get("pubdate", "")[:4]) if item.get("pubdate") else "",
                "authors": author_str,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            })
        return papers
    except Exception:
        return []


# ════════════════════════════════════════════════════════════════
# SIDEBAR — References
# ════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="section-header" style="margin-top:0;">📚 References</div>', unsafe_allow_html=True)

    with st.expander("Data source databases", expanded=True):
        for name, info in SOURCE_INFO.items():
            st.markdown(f"**{name}** — {info['desc']} [↗]({info['url']})")

    with st.expander("Key literature", expanded=False):
        st.markdown("""
        1. Han, G., Wu, X., Xiao, X., Guo, T., Li, D., Zhang, H., ... & Chen, H. (2026).
           RhythmInsight: An Interactive Web Platform for Circadian and Diurnal Rhythmic Analysis and Visualization.
           Journal of Biological Rhythms, 07487304261437377.
        2. Johnson, C. H., & Rust, M. J. (Eds.). (2021). Circadian rhythms in bacteria and microbiomes.
           Berlin: Springer International Publishing.
        3. Glynn, E. F., Chen, J., & Mushegian, A. R. (2006).
           Detecting periodic patterns in unevenly spaced gene expression time series using Lomb–Scargle periodograms.
           Bioinformatics, 22(3), 310-316.
        """)
        st.caption("Individual gene entries also cite a PMID/reference — see the "
                   "'Reference (PMID)' column in each result table.")

    st.caption("Suggested citation for this tool:")
    st.code(
        "S.Unnati (2026). Seasonal Physiology Gene Database.\n"
        "https://seasonal-gene-db-wb4nzf4rwezxmhzrtrcimr.streamlit.app/",
        language=None
    )

# ════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════
st.markdown("""
<div class="main-header">
    <p class="main-title">🧬 Seasonal Physiology Gene Database</p>
    <p class="main-subtitle">A photoperiod- and season-linked gene expression resource, cross-referenced with NCBI, CircaDB, PubMed, GEO Datasets, and UniProt.</p>
</div>
""", unsafe_allow_html=True)

with st.expander("ℹ️ About this database — Short-Day (SD) vs Long-Day (LD) vs Season"):
    st.markdown("""
    This database records gene expression along **two linked but distinct axes**:

    - **Photoperiod condition (SD / LD):** the actual physiological trigger — hours of light vs dark
      a tissue or organism was exposed to in the underlying study. **SD** = short-day / winter-like
      (~8h light), **LD** = long-day / summer-like (~16h light).
    - **Season:** the calendar-based label conventionally used to describe when SD/LD-like conditions
      occur naturally (Winter ≈ SD, Summer ≈ LD, Spring/Autumn ≈ intermediate).

    Each gene's entry below shows **both axes side by side**, so the data can be read either way —
    by season for general context, or by photoperiod condition for the underlying experimental
    framing used in cited studies.
    """)

st.markdown('<div class="section-header">🔗 Linked Data Sources</div>', unsafe_allow_html=True)
src_cols = st.columns(len(SOURCE_INFO))
for col, (name, info) in zip(src_cols, SOURCE_INFO.items()):
    with col:
        with st.popover(name, use_container_width=True):
            st.markdown(f"**{name}**")
            st.write(info["desc"])
            st.markdown(f"[Visit official site →]({info['url']})")

tab_search, tab_compare, tab_contribute, tab_browse, tab_methods, tab_admin = st.tabs(
    ["🔍 Search", "📊 Compare Genes", "✍️ Contribute Data", "🗂 Browse All Genes",
     "🧪 Methodology", "🔐 Admin: Bulk Import"]
)

# ════════════════════════════════════════════════════════════════
# TAB 1 — SEARCH (SD | LD | Season side-by-side)
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
            n_evidence = df['study_reference'].nunique() if 'study_reference' in df.columns else len(df)
            st.markdown(f"""
            <div class="result-box">
                <span class="gene-name">{symbol}</span>{evidence_badge(n_evidence)}
                <div class="gene-meta">{df['full_name'][0]} &nbsp;·&nbsp; Category: {df['category'][0]}</div>
            </div>
            """, unsafe_allow_html=True)

            # ── Live NCBI cross-reference ─────────────────────────
            with st.expander("🔬 Live NCBI cross-reference", expanded=False):
                with st.spinner("Querying NCBI Gene..."):
                    ncbi = fetch_ncbi_gene_summary(symbol)
                if ncbi:
                    st.markdown(f"""
                    <div class="xref-box">
                        <span class="xref-label">Official name:</span> {ncbi['official_name']}<br>
                        <span class="xref-label">Chromosome:</span> {ncbi['chromosome']}
                        &nbsp;·&nbsp; <span class="xref-label">Map location:</span> {ncbi['map_location']}<br>
                        <span class="xref-label">NCBI summary:</span> {ncbi['summary']}<br><br>
                        <a href="{ncbi['ncbi_url']}" target="_blank">View full NCBI Gene record →</a>
                        &nbsp;|&nbsp;
                        <a href="{uniprot_search_url(symbol)}" target="_blank">View on UniProt →</a>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="xref-box">
                        Could not retrieve a live NCBI record for <b>{symbol}</b> automatically
                        (symbol may be non-standard, organism-ambiguous, or NCBI was unreachable).
                        You can check manually:<br>
                        <a href="https://www.ncbi.nlm.nih.gov/gene/?term={symbol}" target="_blank">Search NCBI Gene →</a>
                        &nbsp;|&nbsp;
                        <a href="{uniprot_search_url(symbol)}" target="_blank">Search UniProt →</a>
                    </div>
                    """, unsafe_allow_html=True)

            # ── SD | LD | Season comparison row ──────────────────
            # Backfill photoperiod_condition from season where not explicitly set
            df['photoperiod_condition'] = df.apply(
                lambda r: r['photoperiod_condition'] if r['photoperiod_condition']
                else SEASON_TO_PHOTOPERIOD.get(r['season'], 'INT'),
                axis=1
            )

            sd_rows = df[df['photoperiod_condition'] == 'SD']
            ld_rows = df[df['photoperiod_condition'] == 'LD']
            season_rows = df  # full season breakdown, all 4

            st.markdown('<div class="section-header">Photoperiod & Season Comparison</div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)

            with c1:
                st.markdown('<div class="photo-card photo-card-sd">', unsafe_allow_html=True)
                st.markdown('<div class="photo-label">❄️ Short-Day (SD)</div>', unsafe_allow_html=True)
                if not sd_rows.empty:
                    for _, r in sd_rows.iterrows():
                        st.markdown(f"""<div class="photo-value">
                            <b>{r['expression_level']}</b> ({r['fold_change']}x)<br>
                            {r['functional_role']}<br>
                            <i>Tissue: {r['tissue_type']}</i>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.markdown('<div class="photo-value">No SD-specific data curated yet.</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="photo-card photo-card-ld">', unsafe_allow_html=True)
                st.markdown('<div class="photo-label">☀️ Long-Day (LD)</div>', unsafe_allow_html=True)
                if not ld_rows.empty:
                    for _, r in ld_rows.iterrows():
                        st.markdown(f"""<div class="photo-value">
                            <b>{r['expression_level']}</b> ({r['fold_change']}x)<br>
                            {r['functional_role']}<br>
                            <i>Tissue: {r['tissue_type']}</i>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.markdown('<div class="photo-value">No LD-specific data curated yet.</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with c3:
                st.markdown('<div class="photo-card photo-card-season">', unsafe_allow_html=True)
                st.markdown('<div class="photo-label">📅 By Season</div>', unsafe_allow_html=True)
                season_icons = {'Winter':'❄️','Spring':'🌱','Summer':'☀️','Autumn':'🍂'}
                for _, r in season_rows.iterrows():
                    st.markdown(f"""<div class="photo-value">
                        {season_icons.get(r['season'],'')} <b>{r['season']}</b>: {r['expression_level']} ({r['fold_change']}x)
                    </div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Bar chart, all 4 seasons ──────────────────────────
            fig = px.bar(df, x='season', y='fold_change', color='season',
                color_discrete_map={'Winter': '#1f5fa8', 'Spring': '#1f9d55',
                                     'Summer': '#e8820c', 'Autumn': '#b0453f'},
                title=f"{symbol} — Fold Change by Season")
            fig.update_layout(showlegend=False, plot_bgcolor='white', paper_bgcolor='white',
                               font_color='#1a1a1a')
            fig.update_yaxes(title_text="Fold Change (relative to baseline)")
            fig.update_xaxes(title_text="Season")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown('<div class="section-header">Full Data Table</div>', unsafe_allow_html=True)
            st.dataframe(
                df[['season', 'photoperiod_condition', 'expression_level', 'fold_change',
                    'pathway', 'tissue_type', 'study_reference']].rename(columns={
                    'season': 'Season', 'photoperiod_condition': 'Photoperiod',
                    'expression_level': 'Expression', 'fold_change': 'Fold Change',
                    'pathway': 'Pathway', 'tissue_type': 'Tissue', 'study_reference': 'Reference (PMID)'
                }),
                use_container_width=True
            )

            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download this gene's data as CSV", csv_bytes,
                                file_name=f"{symbol}_seasonal_data.csv", mime="text/csv")
        else:
            st.info(f"No curated seasonal/photoperiod data yet for '{symbol}'. Use the Contribute tab to add it.")

            # ── Live NCBI identity check (even without curated data) ──
            with st.spinner("Checking NCBI Gene..."):
                ncbi_fallback = fetch_ncbi_gene_summary(symbol)
            if ncbi_fallback:
                st.markdown(f"""
                <div class="xref-box">
                    <span class="xref-label">Confirmed via NCBI:</span> {ncbi_fallback['official_name']}
                    (Chromosome {ncbi_fallback['chromosome']})<br>
                    <a href="{ncbi_fallback['ncbi_url']}" target="_blank">View NCBI Gene record →</a>
                    &nbsp;|&nbsp;
                    <a href="{uniprot_search_url(symbol)}" target="_blank">View on UniProt →</a>
                </div>
                """, unsafe_allow_html=True)

            # ── Live PubMed literature search fallback ─────────────
            st.markdown('<div class="section-header">📖 Live Literature Search — PubMed</div>', unsafe_allow_html=True)
            st.caption(
                f"No curated entry exists yet for {symbol}, so here is real, current PubMed literature "
                f"mentioning it alongside photoperiod, seasonal, or circadian terms — fetched live."
            )
            with st.spinner("Searching PubMed..."):
                papers = fetch_pubmed_photoperiod_papers(symbol)

            if papers:
                for p in papers:
                    st.markdown(f"""
                    <div class="xref-box">
                        <a href="{p['url']}" target="_blank"><b>{p['title']}</b></a><br>
                        <span style="color:#555;">{p['authors']} &nbsp;·&nbsp; {p['journal']} &nbsp;·&nbsp; {p['year']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.caption("Titles and links only, pulled live from PubMed — full abstracts are available via the links above.")
            else:
                st.markdown(f"""
                <div class="xref-box">
                    No PubMed papers directly link <b>{symbol}</b> to photoperiod/seasonal/circadian terms yet.<br>
                    <a href="https://pubmed.ncbi.nlm.nih.gov/?term={symbol}" target="_blank">Search PubMed for {symbol} generally →</a>
                </div>
                """, unsafe_allow_html=True)

        # Community contributions
        comm_query = """
            SELECT season_or_condition AS "Season/Condition", expression_level AS "Expression",
                   fold_change AS "Fold Change", functional_role AS "Functional Role",
                   pathway AS "Pathway", tissue_type AS "Tissue", source_db AS "Source DB",
                   source_reference AS "Reference", contributor_name AS "Contributor",
                   submitted_at AS "Submitted"
            FROM community_contributions
            WHERE gene_symbol = %s
            ORDER BY submitted_at DESC
        """
        comm_df = pd.read_sql(comm_query, conn, params=[symbol])
        if not comm_df.empty:
            st.markdown('<div class="section-header">🌍 Community-Contributed Data</div>', unsafe_allow_html=True)
            st.caption("Submitted directly by users — not independently verified by the project author.")
            st.dataframe(comm_df, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# TAB 2 — COMPARE GENES (multi-gene, side-by-side)
# ════════════════════════════════════════════════════════════════
with tab_compare:
    st.markdown('<div class="section-header">Compare Multiple Genes</div>', unsafe_allow_html=True)
    st.caption("Enter 2–6 gene symbols separated by commas to compare their seasonal fold-change profiles "
               "on one chart — useful for spotting shared or opposing photoperiod responses across a pathway.")

    compare_input = st.text_input("Gene symbols (comma-separated)",
                                   placeholder="e.g. CLOCK, PER2, BMAL1, CRY1")

    if compare_input:
        symbols = [s.strip().upper() for s in compare_input.split(",") if s.strip()]
        symbols = symbols[:6]  # cap to keep the chart readable

        if len(symbols) < 2:
            st.warning("Enter at least two gene symbols, separated by commas.")
        else:
            placeholders = ",".join(["%s"] * len(symbols))
            compare_query = f"""
                SELECT g.gene_symbol, s.name AS season, gsf.fold_change,
                       gsf.expression_level, gsf.photoperiod_condition
                FROM gene_seasonal_function gsf
                JOIN genes g ON gsf.gene_id = g.id
                JOIN seasons s ON gsf.season_id = s.id
                WHERE g.gene_symbol IN ({placeholders})
                ORDER BY g.gene_symbol, FIELD(s.name, 'Winter','Spring','Summer','Autumn')
            """
            cmp_df = pd.read_sql(compare_query, conn, params=symbols)

            found = sorted(cmp_df['gene_symbol'].unique().tolist()) if not cmp_df.empty else []
            missing = [s for s in symbols if s not in found]
            if missing:
                st.info(f"No curated data yet for: {', '.join(missing)}")

            if not cmp_df.empty:
                fig_cmp = px.bar(
                    cmp_df, x='season', y='fold_change', color='gene_symbol',
                    barmode='group',
                    category_orders={'season': ['Winter', 'Spring', 'Summer', 'Autumn']},
                    title="Fold Change by Season — Selected Genes",
                    labels={'gene_symbol': 'Gene', 'season': 'Season', 'fold_change': 'Fold Change'}
                )
                fig_cmp.update_layout(plot_bgcolor='white', paper_bgcolor='white', font_color='#1a1a1a')
                st.plotly_chart(fig_cmp, use_container_width=True)

                st.markdown('<div class="section-header">Comparison Table</div>', unsafe_allow_html=True)
                st.dataframe(
                    cmp_df.rename(columns={
                        'gene_symbol': 'Gene', 'season': 'Season',
                        'fold_change': 'Fold Change', 'expression_level': 'Expression',
                        'photoperiod_condition': 'Photoperiod'
                    }),
                    use_container_width=True
                )
    else:
        st.caption("Try comparing core clock genes, e.g. **CLOCK, PER2, BMAL1, CRY1**.")

# ════════════════════════════════════════════════════════════════
# TAB 3 — CONTRIBUTE
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
                st.success(f"Thank you. Your data for {f_gene.upper()} is now live and publicly visible.")

    st.markdown('<div class="section-header">Recent Community Submissions</div>', unsafe_allow_html=True)
    recent_query = """
        SELECT gene_symbol AS "Gene", season_or_condition AS "Condition",
               expression_level AS "Expression", source_db AS "Source",
               contributor_name AS "Contributor", submitted_at AS "Submitted"
        FROM community_contributions
        ORDER BY submitted_at DESC
        LIMIT 15
    """
    recent_df = pd.read_sql(recent_query, conn)
    if not recent_df.empty:
        st.dataframe(recent_df, use_container_width=True)
    else:
        st.caption("No community submissions yet.")

# ════════════════════════════════════════════════════════════════
# TAB 4 — BROWSE
# ════════════════════════════════════════════════════════════════
with tab_browse:
    category_filter = st.selectbox("Filter by category",
        ["All", "Circadian", "Hormonal", "Immune", "Metabolic", "Mood/Brain", "Other"])

    all_query = "SELECT gene_symbol AS Symbol, full_name AS \"Full Name\", category AS Category, chromosome AS Chromosome, organism AS Organism FROM genes ORDER BY gene_symbol"
    all_genes = pd.read_sql(all_query, conn)
    if category_filter != "All":
        all_genes = all_genes[all_genes['Category'] == category_filter]
    st.dataframe(all_genes, use_container_width=True)
    st.caption(f"Showing {len(all_genes)} genes")

# ════════════════════════════════════════════════════════════════
# TAB 5 — METHODOLOGY
# ════════════════════════════════════════════════════════════════
with tab_methods:
    st.markdown('<div class="section-header">Methodology & Data Curation</div>', unsafe_allow_html=True)

    st.markdown("""
    **1. Scope**
    This database catalogs gene expression changes associated with photoperiod
    (day length) and season, focused on genes with known roles in circadian,
    hormonal, immune, metabolic, or mood/brain physiology.

    **2. Photoperiod condition assignment**
    Each curated entry is labeled with a photoperiod condition — **SD** (Short-Day,
    ~8h light, winter-like), **LD** (Long-Day, ~16h light, summer-like), or
    **INT** (Intermediate, spring/autumn-like) — either taken directly from the
    experimental design of the cited study, or, where a study reports only a
    calendar season, backfilled using the conventional mapping:
    Winter → SD, Summer → LD, Spring/Autumn → Intermediate.

    **3. Expression level categories**
    - **HIGH** — expression elevated relative to the study's baseline/control condition
    - **NORMAL** — expression within the study's typical/baseline range
    - **LOW** — expression reduced relative to baseline
    
    Fold change values, where reported, are shown alongside these categories and
    should be read as *relative to the baseline defined in the cited source*, not
    as standardized across studies.

    **4. Evidence strength**
    Gene entries display an evidence badge:
    - **Single curated entry** — data drawn from one source/study
    - **Replicated across ≥2 entries** — corroborated by multiple curated records
    
    This badge reflects curation coverage in this database only, not a formal
    meta-analysis, and should not be read as a statement of scientific consensus.

    **5. Live cross-referencing**
    Gene symbols are checked against live NCBI Gene records (via NCBI E-utilities)
    at search time to confirm official nomenclature and surface the official gene
    summary. This is a validation aid, not a data source for the fold-change/
    expression values themselves, which come from the curated database.

    **6. Community contributions**
    Data submitted via the Contribute tab is published immediately and is
    **not independently verified** by the project author before appearing
    publicly. It is visually and structurally separated from author-curated
    entries throughout the app. Users citing this tool for research purposes
    should verify community-submitted rows against the original source listed.

    **7. Limitations**
    - Organism is not uniformly controlled for across all entries; check the
      "Organism" field in Browse All Genes where relevant.
    - Tissue type varies by study and is not normalized.
    - This is a curation and cross-referencing tool, not a primary data source —
      always confirm critical values against the cited original publication or
      database record before use in a manuscript.
    """)

    st.markdown('<div class="section-header">Suggested Citation</div>', unsafe_allow_html=True)
    st.code(
        "S.Unnati (2026). Seasonal Physiology Gene Database.\n"
        "https://seasonal-gene-db-wb4nzf4rwezxmhzrtrcimr.streamlit.app/",
        language=None
    )

# ════════════════════════════════════════════════════════════════
# TAB 6 — ADMIN: BULK IMPORT (password-protected)
# ════════════════════════════════════════════════════════════════
with tab_admin:
    st.markdown('<div class="section-header">Bulk Import Genes from CSV</div>', unsafe_allow_html=True)

    ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", None)

    if not ADMIN_PASSWORD:
        st.error(
            "No ADMIN_PASSWORD is set in your Streamlit secrets, so this tab is disabled. "
            "Add `ADMIN_PASSWORD = \"your-chosen-password\"` to your app's Secrets "
            "(Streamlit Cloud → app settings → Secrets) and reload."
        )
    else:
        pwd = st.text_input("Admin password", type="password")
        if pwd != ADMIN_PASSWORD:
            if pwd:
                st.warning("Incorrect password.")
            st.stop()

        st.success("Authenticated. You can import gene data below.")
        st.caption(
            "Expected CSV format (like `All_288_genes.csv`): a `gene_name` column, "
            "any number of individual replicate columns, and **mean_SD**, **mean_LD**, "
            "and **log2FC** summary columns. Other formats can be adapted — ask if yours differs."
        )

        uploaded = st.file_uploader("Upload gene CSV", type=["csv"])

        colA, colB, colC = st.columns(3)
        with colA:
            batch_category = st.selectbox(
                "Category to assign to all imported genes",
                ["Circadian", "Hormonal", "Immune", "Metabolic", "Mood/Brain", "Sensory", "Other"]
            )
        with colB:
            batch_organism = st.text_input("Organism", value="Mus musculus")
        with colC:
            batch_tissue = st.text_input("Tissue type", value="Eyes")

        batch_reference = st.text_input(
            "Study reference (PMID, GEO accession, or short label)",
            placeholder="e.g. GSE123456 or PMID 12345678"
        )
        autofill_ncbi = st.checkbox(
            "Auto-fill official gene name via live NCBI lookup (slower — ~0.4s per gene)",
            value=False
        )

        if uploaded is not None:
            raw_df = pd.read_csv(uploaded)
            st.write(f"Preview — {len(raw_df)} rows detected:")
            st.dataframe(raw_df.head(10), use_container_width=True)

            required_cols = {"gene_name", "mean_SD", "mean_LD", "log2FC"}
            missing_cols = required_cols - set(raw_df.columns)

            if missing_cols:
                st.error(f"CSV is missing required columns: {', '.join(missing_cols)}")
            else:
                if st.button(f"Import all {len(raw_df)} genes into the database", type="primary"):
                    ins_cursor = conn.cursor()

                    # Look up season_id for Winter (=SD) and Summer (=LD)
                    ins_cursor.execute("SELECT id, name FROM seasons WHERE name IN ('Winter','Summer')")
                    season_ids = {name: sid for sid, name in ins_cursor.fetchall()}

                    progress = st.progress(0.0, text="Starting import...")
                    inserted, updated, skipped = 0, 0, 0
                    total = len(raw_df)

                    for i, row in raw_df.iterrows():
                        symbol = str(row["gene_name"]).strip().upper()
                        if not symbol:
                            skipped += 1
                            continue

                        full_name = symbol
                        chromosome = "N/A"
                        if autofill_ncbi:
                            ncbi = fetch_ncbi_gene_summary(symbol, organism=batch_organism)
                            if ncbi:
                                full_name = ncbi["official_name"] or symbol
                                chromosome = ncbi["chromosome"] or "N/A"
                            time.sleep(0.4)  # stay under NCBI's unauthenticated rate limit

                        # Upsert into genes table
                        ins_cursor.execute(
                            "SELECT id FROM genes WHERE gene_symbol = %s", (symbol,)
                        )
                        existing = ins_cursor.fetchone()

                        if existing:
                            gene_id = existing[0]
                            ins_cursor.execute(
                                "UPDATE genes SET full_name=%s, category=%s, chromosome=%s, organism=%s WHERE id=%s",
                                (full_name, batch_category, chromosome, batch_organism, gene_id)
                            )
                            updated += 1
                        else:
                            ins_cursor.execute(
                                "INSERT INTO genes (gene_symbol, full_name, category, chromosome, organism) "
                                "VALUES (%s,%s,%s,%s,%s)",
                                (symbol, full_name, batch_category, chromosome, batch_organism)
                            )
                            gene_id = ins_cursor.lastrowid
                            inserted += 1

                        log2fc = float(row["log2FC"])

                        def expression_from_log2fc(val):
                            if val >= 0.5:
                                return "HIGH"
                            elif val <= -0.5:
                                return "LOW"
                            return "NORMAL"

                        # Remove any prior rows for this gene+season+tissue combo to avoid duplicates on re-import
                        for season_name, photoperiod, mean_col in [
                            ("Winter", "SD", "mean_SD"), ("Summer", "LD", "mean_LD")
                        ]:
                            if season_name not in season_ids:
                                continue
                            season_id = season_ids[season_name]

                            ins_cursor.execute(
                                "DELETE FROM gene_seasonal_function "
                                "WHERE gene_id=%s AND season_id=%s AND tissue_type=%s AND study_reference=%s",
                                (gene_id, season_id, batch_tissue, batch_reference)
                            )
                            ins_cursor.execute(
                                """INSERT INTO gene_seasonal_function
                                   (gene_id, season_id, expression_level, fold_change,
                                    functional_role, pathway, tissue_type, study_reference,
                                    photoperiod_condition)
                                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                                (
                                    gene_id, season_id,
                                    expression_from_log2fc(log2fc),
                                    round(log2fc, 3),
                                    f"Imported from bulk CSV — mean expression ({mean_col}) = {row[mean_col]}, log2FC = {round(log2fc,3)}",
                                    "Imported dataset",
                                    batch_tissue,
                                    batch_reference,
                                    photoperiod
                                )
                            )

                        progress.progress((i + 1) / total, text=f"Importing {symbol} ({i+1}/{total})")

                    conn.commit()
                    progress.empty()
                    st.success(
                        f"Import complete — {inserted} new genes added, {updated} existing genes updated, "
                        f"{skipped} rows skipped. Each imported gene now has Winter(SD)/Summer(LD) entries "
                        f"for tissue '{batch_tissue}'."
                    )
                    st.info("Note: fold_change stored here is the CSV's **log2FC** value, not a linear fold change. "
                             "This is noted in each entry's functional_role text for transparency.")

# ════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════
st.divider()
st.caption("Data sources: NCBI Gene · CircaDB · GEO Datasets · UniProt · PubMed · Community contributions")
st.caption("This is an open, publicly editable research database. Data accuracy of community contributions is not independently verified.")
st.caption("📚 Full reference list available in the sidebar. Suggested citation: Your Name (2026). "
           "*Seasonal Physiology Gene Database*. "
           "seasonal-gene-db-wb4nzf4rwezxmhzrtrcimr.streamlit.app")
