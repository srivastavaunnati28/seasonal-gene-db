import streamlit as st
import mysql.connector
import pandas as pd

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Seasonal Physiology Gene Database",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* Sidebar */
[data-testid="stSidebar"] {
    min-width: 210px !important;
    max-width: 210px !important;
    background-color: #f8f9fb;
    border-right: 1px solid #e5e7eb;
}
[data-testid="stSidebar"] .block-container { padding: 1rem 0.8rem; }

/* Main container */
.block-container { padding: 1.5rem 2rem 2rem 2rem !important; max-width: 1100px; }

/* Top header bar */
.top-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0 18px 0;
    border-bottom: 1.5px solid #e5e7eb;
    margin-bottom: 20px;
}
.logo-text {
    font-size: 20px;
    font-weight: 600;
    color: #0f6e56;
    letter-spacing: -0.4px;
}
.logo-sub {
    font-size: 12px;
    color: #6b7280;
    margin-top: 1px;
}

/* Stats cards row */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 22px;
}
.stat-box {
    background: #f0fdf7;
    border: 1px solid #bbf7d0;
    border-radius: 10px;
    padding: 12px 16px;
    text-align: center;
}
.stat-val {
    font-size: 22px;
    font-weight: 600;
    color: #065f46;
}
.stat-lbl {
    font-size: 11px;
    color: #6b7280;
    margin-top: 2px;
}

/* Gene card */
.gene-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.gene-title {
    font-size: 22px;
    font-weight: 600;
    color: #111827;
    letter-spacing: -0.5px;
}
.gene-meta {
    font-size: 12.5px;
    color: #6b7280;
    margin-top: 4px;
}
.tier-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #d1fae5;
    color: #065f46;
    font-size: 12px;
    font-weight: 500;
    padding: 4px 12px;
    border-radius: 20px;
    margin-top: 10px;
}
.tier2-badge {
    background: #dbeafe;
    color: #1e40af;
}
.tier3-badge {
    background: #fef9c3;
    color: #854d0e;
}

/* Expression boxes */
.expr-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin: 14px 0;
}
.expr-box {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 14px 16px;
}
.expr-box-label {
    font-size: 11px;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}
.expr-box-val {
    font-size: 24px;
    font-weight: 600;
    color: #111827;
}
.expr-up   { color: #059669; font-size: 12px; margin-top: 3px; }
.expr-down { color: #dc2626; font-size: 12px; margin-top: 3px; }
.expr-neutral { color: #9ca3af; font-size: 12px; margin-top: 3px; }

/* Bar chart rows */
.bar-section { margin: 14px 0; }
.bar-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
    font-size: 12px;
}
.bar-season {
    width: 36px;
    color: #6b7280;
    text-align: right;
    flex-shrink: 0;
}
.bar-bg {
    flex: 1;
    height: 11px;
    background: #f3f4f6;
    border-radius: 6px;
    overflow: hidden;
}
.bar-fill {
    height: 100%;
    border-radius: 6px;
}
.bar-ld  { background: #1d9e75; }
.bar-sd  { background: #d85a30; }
.bar-win { background: #3b82f6; }
.bar-sum { background: #f59e0b; }
.bar-val {
    width: 40px;
    text-align: right;
    color: #6b7280;
    font-size: 11px;
    flex-shrink: 0;
}

/* Section header */
.section-head {
    font-size: 11px;
    font-weight: 600;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin: 18px 0 10px;
    border-top: 1px solid #f3f4f6;
    padding-top: 14px;
}

/* External links row */
.links-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 8px;
}
.ext-link {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #f9fafb;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 5px 12px;
    font-size: 12px;
    color: #1d4ed8;
    text-decoration: none;
    cursor: pointer;
}
.ext-link:hover { background: #eff6ff; }

/* No-result box */
.no-result {
    text-align: center;
    padding: 60px 20px;
    color: #9ca3af;
    font-size: 14px;
}

/* Sidebar section headers */
.sb-head {
    font-size: 10px;
    font-weight: 600;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin: 16px 0 6px;
}

/* Responsive */
@media (max-width: 700px) {
    .stats-grid { grid-template-columns: 1fr 1fr; }
    .expr-grid  { grid-template-columns: 1fr; }
}
</style>
""", unsafe_allow_html=True)


# ─── DB Connection ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        port=int(st.secrets["mysql"]["port"]),
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
    )

@st.cache_data(ttl=300)
def run_query(query, params=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    result = cursor.fetchall()
    cursor.close()
    return result


# ─── Helper: Build external links ─────────────────────────────────────────────
def external_links_html(gene_symbol, ncbi_id="", uniprot_id="", geo_id="", pubmed_count=0):
    links = []
    if ncbi_id:
        links.append(f'<a class="ext-link" href="https://www.ncbi.nlm.nih.gov/gene/{ncbi_id}" target="_blank">🔗 NCBI Gene</a>')
    if uniprot_id:
        links.append(f'<a class="ext-link" href="https://www.uniprot.org/uniprot/{uniprot_id}" target="_blank">🔗 UniProt</a>')
    links.append(f'<a class="ext-link" href="https://circadb.hogeneschlab.org/query?gene={gene_symbol}" target="_blank">🔗 CircaDB</a>')
    if geo_id:
        links.append(f'<a class="ext-link" href="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={geo_id}" target="_blank">🔗 GEO Dataset</a>')
    pm_label = f"🔗 PubMed ({pubmed_count})" if pubmed_count else "🔗 PubMed"
    links.append(f'<a class="ext-link" href="https://pubmed.ncbi.nlm.nih.gov/?term={gene_symbol}+photoperiod+seasonal" target="_blank">{pm_label}</a>')
    return '<div class="links-row">' + "".join(links) + '</div>'


# ─── Helper: Tier badge ────────────────────────────────────────────────────────
def tier_badge(tier):
    if tier == 1:
        return '<span class="tier-badge">✅ Tier 1 — Curated Seasonal Data</span>'
    elif tier == 2:
        return '<span class="tier-badge tier2-badge">🔵 Tier 2 — Linked External Data</span>'
    else:
        return '<span class="tier-badge tier3-badge">🟡 Tier 3 — Predicted</span>'


# ─── Helper: Expression bar ────────────────────────────────────────────────────
def expr_bar(label, value, bar_class, max_val=3.0):
    pct = min(abs(value) / max_val * 100, 100)
    sign = "+" if value >= 0 else ""
    return f"""
    <div class="bar-row">
        <span class="bar-season">{label}</span>
        <div class="bar-bg"><div class="bar-fill {bar_class}" style="width:{pct:.0f}%"></div></div>
        <span class="bar-val">{sign}{value:.2f}</span>
    </div>"""


# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="logo-text">🌿 SeasonalPhysDB</div>', unsafe_allow_html=True)
    st.markdown('<div class="logo-sub">Photoperiod Gene Expression</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<div class="sb-head">Filter by Category</div>', unsafe_allow_html=True)
    category_filter = st.selectbox(
        "Category", ["All", "Circadian", "Photoperiodic", "Metabolic", "Hormonal", "Immune", "Neural"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="sb-head">Expression Pattern</div>', unsafe_allow_html=True)
    expr_filter = st.selectbox(
        "Expression",
        ["All", "LD upregulated", "SD upregulated", "Seasonal toggle"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="sb-head">Data Tier</div>', unsafe_allow_html=True)
    tier_filter = st.selectbox(
        "Tier",
        ["All tiers", "Tier 1 — Curated", "Tier 2 — Linked", "Tier 3 — Predicted"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown('<div class="sb-head">Navigation</div>', unsafe_allow_html=True)
    page = st.radio(
        "Page",
        ["🔍 Gene Search", "📋 Browse All", "📊 Photoperiod Compare", "🔗 Data Sources", "📤 Submit Data"],
        label_visibility="collapsed"
    )


# ─── Top header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-header">
    <div>
        <div class="logo-text">🌿 Seasonal Physiology Gene Database</div>
        <div class="logo-sub">A photoperiod- and season-linked gene expression resource, cross-referenced with NCBI, CircaDB, PubMed, GEO Datasets, and UniProt</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─── Stats row ────────────────────────────────────────────────────────────────
try:
    total_genes  = run_query("SELECT COUNT(*) AS n FROM genes")[0]["n"]
    curated      = run_query("SELECT COUNT(*) AS n FROM genes WHERE tier = 1")[0]["n"]
    linked_dbs   = 6
    publications = run_query("SELECT COUNT(*) AS n FROM publications")[0]["n"] if run_query("SHOW TABLES LIKE 'publications'") else "—"
except Exception:
    total_genes, curated, linked_dbs, publications = "—", "—", 6, "—"

st.markdown(f"""
<div class="stats-grid">
    <div class="stat-box"><div class="stat-val">{total_genes}</div><div class="stat-lbl">Total genes</div></div>
    <div class="stat-box"><div class="stat-val">{curated}</div><div class="stat-lbl">Curated entries</div></div>
    <div class="stat-box"><div class="stat-val">{linked_dbs}</div><div class="stat-lbl">Linked databases</div></div>
    <div class="stat-box"><div class="stat-val">{publications}</div><div class="stat-lbl">Publications</div></div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: Gene Search
# ══════════════════════════════════════════════════════════════════════════════
if "Gene Search" in page:

    search_col, _ = st.columns([3, 1])
    with search_col:
        query_input = st.text_input(
            "Search gene symbol",
            placeholder="e.g. CLOCK, PER2, TSH, AANAT…",
            label_visibility="visible"
        )

    if query_input.strip():
        try:
            # Adjust column names to match YOUR actual DB schema
            results = run_query(
                """
                SELECT g.*,
                       e.ld_expression, e.sd_expression,
                       e.winter_expression, e.summer_expression,
                       e.log2fc_ld_sd,
                       l.ncbi_id, l.uniprot_id, l.geo_id, l.pubmed_count
                FROM genes g
                LEFT JOIN expression_data e ON g.gene_id = e.gene_id
                LEFT JOIN external_links  l ON g.gene_id = l.gene_id
                WHERE g.gene_symbol LIKE %s
                   OR g.gene_name   LIKE %s
                LIMIT 20
                """,
                (f"%{query_input}%", f"%{query_input}%")
            )
        except Exception as ex:
            st.error(f"Database error: {ex}")
            results = []

        if not results:
            st.markdown(f'<div class="no-result">No results found for <strong>{query_input}</strong>.<br>Try another gene symbol or browse all genes.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f"**{len(results)} result(s)** for *{query_input}*")
            for row in results:
                symbol   = row.get("gene_symbol", "—")
                name     = row.get("gene_name", "")
                category = row.get("category", "—")
                organism = row.get("organism", "")
                tier     = int(row.get("tier", 3))

                ld_expr  = row.get("ld_expression")
                sd_expr  = row.get("sd_expression")
                win_expr = row.get("winter_expression")
                sum_expr = row.get("summer_expression")
                log2fc   = row.get("log2fc_ld_sd")

                ncbi_id  = row.get("ncbi_id", "")
                uni_id   = row.get("uniprot_id", "")
                geo_id   = row.get("geo_id", "")
                pm_count = row.get("pubmed_count", 0)

                # Expression boxes
                if ld_expr is not None and sd_expr is not None:
                    ld_val  = float(ld_expr)
                    sd_val  = float(sd_expr)
                    ratio   = ld_val / sd_val if sd_val else 0
                    trend   = "↑ Upregulated vs SD" if ratio > 1.2 else ("↓ Downregulated vs SD" if ratio < 0.8 else "~ Similar to SD")
                    t_class = "expr-up" if ratio > 1.2 else ("expr-down" if ratio < 0.8 else "expr-neutral")
                    expr_boxes = f"""
                    <div class="expr-grid">
                        <div class="expr-box">
                            <div class="expr-box-label">☀️ Long Day (LD)</div>
                            <div class="expr-box-val">{ld_val:.2f}×</div>
                            <div class="{t_class}">{trend}</div>
                        </div>
                        <div class="expr-box">
                            <div class="expr-box-label">🌙 Short Day (SD)</div>
                            <div class="expr-box-val">{sd_val:.2f}×</div>
                            <div class="expr-neutral">Baseline reference</div>
                        </div>
                    </div>"""
                else:
                    expr_boxes = "<p style='color:#9ca3af;font-size:13px'>Expression data not available for this entry.</p>"

                # Bar chart rows
                bars_html = '<div class="bar-section">'
                if ld_expr  is not None: bars_html += expr_bar("LD",  float(log2fc or 0),   "bar-ld")
                if sd_expr  is not None: bars_html += expr_bar("SD",  0.0,                  "bar-sd")
                if win_expr is not None: bars_html += expr_bar("Win", float(win_expr),       "bar-win")
                if sum_expr is not None: bars_html += expr_bar("Sum", float(sum_expr),       "bar-sum")
                bars_html += "</div>"

                st.markdown(f"""
                <div class="gene-card">
                    <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px">
                        <div>
                            <div class="gene-title">{symbol}</div>
                            <div class="gene-meta">{name} &nbsp;·&nbsp; Category: {category}{ " &nbsp;·&nbsp; <em>" + organism + "</em>" if organism else ""}</div>
                        </div>
                        <div style="flex-shrink:0">{tier_badge(tier)}</div>
                    </div>

                    <div class="section-head">Photoperiod & Season Comparison</div>
                    {expr_boxes}

                    <div class="section-head">Relative Expression (log₂FC)</div>
                    {bars_html}

                    <div class="section-head">Linked External Sources</div>
                    {external_links_html(symbol, ncbi_id, uni_id, geo_id, pm_count)}
                </div>
                """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: Browse All
# ══════════════════════════════════════════════════════════════════════════════
elif "Browse All" in page:
    st.subheader("Browse All Genes")

    # Build WHERE clause from sidebar filters
    where_clauses, params = [], []
    if category_filter != "All":
        where_clauses.append("category = %s"); params.append(category_filter)
    if tier_filter != "All tiers":
        tier_num = int(tier_filter.split()[1])
        where_clauses.append("tier = %s"); params.append(tier_num)
    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    try:
        rows = run_query(f"SELECT gene_symbol, gene_name, category, organism, tier FROM genes {where_sql} ORDER BY gene_symbol LIMIT 200", params)
        if rows:
            df = pd.DataFrame(rows)
            df.columns = ["Symbol", "Full Name", "Category", "Organism", "Tier"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No genes match the selected filters.")
    except Exception as ex:
        st.error(f"Database error: {ex}")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: Photoperiod Compare
# ══════════════════════════════════════════════════════════════════════════════
elif "Photoperiod Compare" in page:
    st.subheader("Compare Genes Across Photoperiods")
    genes_input = st.text_input("Enter gene symbols (comma-separated)", placeholder="CLOCK, PER2, CRY1, AANAT")

    if genes_input:
        symbols = [s.strip().upper() for s in genes_input.split(",") if s.strip()]
        try:
            placeholders = ",".join(["%s"] * len(symbols))
            rows = run_query(
                f"""SELECT g.gene_symbol, e.ld_expression, e.sd_expression,
                           e.winter_expression, e.summer_expression, e.log2fc_ld_sd
                    FROM genes g
                    LEFT JOIN expression_data e ON g.gene_id = e.gene_id
                    WHERE g.gene_symbol IN ({placeholders})""",
                symbols
            )
            if rows:
                df = pd.DataFrame(rows)
                df.columns = ["Gene", "LD expr", "SD expr", "Winter", "Summer", "log2FC (LD/SD)"]
                st.dataframe(df, use_container_width=True, hide_index=True)

                import streamlit as _st
                st.bar_chart(df.set_index("Gene")[["LD expr", "SD expr"]])
            else:
                st.info("No data found for the entered gene symbols.")
        except Exception as ex:
            st.error(f"Database error: {ex}")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: Data Sources
# ══════════════════════════════════════════════════════════════════════════════
elif "Data Sources" in page:
    st.subheader("Linked Data Sources")
    sources = [
        ("NCBI Gene", "https://www.ncbi.nlm.nih.gov/gene/", "Gene annotations, sequences, and functional data"),
        ("CircaDB",   "https://circadb.hogeneschlab.org/",   "Circadian gene expression profiles in mammals"),
        ("PubMed",    "https://pubmed.ncbi.nlm.nih.gov/",    "Literature references for seasonal physiology"),
        ("GEO Datasets", "https://www.ncbi.nlm.nih.gov/geo/", "High-throughput gene expression datasets"),
        ("UniProt",   "https://www.uniprot.org/",            "Protein sequence and functional annotation"),
        ("Ensembl",   "https://www.ensembl.org/",            "Genome browser and gene model data"),
    ]
    for name, url, desc in sources:
        st.markdown(f"""
        <div class="gene-card" style="padding:14px 20px">
            <div style="display:flex;align-items:center;justify-content:space-between">
                <div>
                    <strong>{name}</strong>
                    <div style="font-size:13px;color:#6b7280;margin-top:3px">{desc}</div>
                </div>
                <a class="ext-link" href="{url}" target="_blank">Visit →</a>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: Submit Data
# ══════════════════════════════════════════════════════════════════════════════
elif "Submit Data" in page:
    st.subheader("Contribute Gene Data")
    st.info("Submit new or corrected gene expression data for curation. All submissions are reviewed before inclusion.")

    with st.form("submit_form"):
        c1, c2 = st.columns(2)
        with c1:
            gene_sym   = st.text_input("Gene Symbol *", placeholder="e.g. CLOCK")
            gene_name  = st.text_input("Full Gene Name", placeholder="e.g. Circadian Locomotor Output Cycles Kaput")
            organism   = st.text_input("Organism", placeholder="e.g. Mus musculus")
        with c2:
            category   = st.selectbox("Category", ["Circadian", "Photoperiodic", "Metabolic", "Hormonal", "Immune", "Neural", "Other"])
            ld_val     = st.number_input("LD Expression (fold change)", min_value=0.0, step=0.01)
            sd_val     = st.number_input("SD Expression (fold change)", min_value=0.0, step=0.01)

        pubmed_ref = st.text_input("PubMed ID / DOI (supporting reference)")
        notes      = st.text_area("Additional notes / methodology", height=100)
        submitted  = st.form_submit_button("Submit for Review")

        if submitted:
            if not gene_sym:
                st.error("Gene symbol is required.")
            else:
                # Insert into a submissions table — adjust to your schema
                try:
                    conn = get_connection()
                    cur  = conn.cursor()
                    cur.execute(
                        """INSERT INTO submissions
                           (gene_symbol, gene_name, organism, category, ld_expression, sd_expression, pubmed_ref, notes)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                        (gene_sym, gene_name, organism, category, ld_val, sd_val, pubmed_ref, notes)
                    )
                    conn.commit()
                    cur.close()
                    st.success(f"✅ '{gene_sym}' submitted successfully. Thank you for contributing!")
                except Exception as ex:
                    st.error(f"Submission failed: {ex}")
