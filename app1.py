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
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700;800&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp {
        background-color: #f3f9f8;
        background-image:
            radial-gradient(circle, rgba(15,140,130,0.10) 1.4px, transparent 1.4px),
            repeating-linear-gradient(115deg, rgba(15,140,130,0.05) 0px, rgba(15,140,130,0.05) 1.5px, transparent 1.5px, transparent 26px),
            linear-gradient(160deg, #f6fbfa 0%, #eef7f5 45%, #e9f4f0 100%);
        background-size: 22px 22px, 220px 220px, cover;
        background-attachment: fixed;
    }

    .ncbi-topstrip {
        background: #0c3b3f;
        color: #cdeae6;
        font-size: 12px;
        padding: 6px 16px;
        margin: -1rem -1rem 0 -1rem;
        letter-spacing: .4px;
    }

    .main-header {
        position: relative;
        background: linear-gradient(120deg, #ffffff 0%, #eaf6f4 60%, #e2f2ee 100%);
        border: 1px solid #bfe3dc;
        border-radius: 12px;
        padding: 28px 32px;
        margin: 10px 0 18px 0;
        overflow: hidden;
        box-shadow: 0 6px 24px rgba(15,60,60,0.08);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 18px;
    }
    .main-header-text { position: relative; z-index: 1; max-width: 620px; }
    .main-header-art { flex-shrink: 0; opacity: 0.92; }
    .main-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 32px;
        font-weight: 800;
        letter-spacing: .2px;
        margin: 0;
        color: #0b3d3f;
    }
    .main-subtitle {
        font-size: 14.5px;
        color: #34605e;
        margin-top: 8px;
        line-height: 1.55;
    }
    .affil {
        font-size: 13px;
        color: #4a7a76;
        font-style: italic;
    }

    .section-header {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        letter-spacing: .3px;
        color: #ffffff;
        background: linear-gradient(90deg, #0f8c82 0%, #12a396 100%);
        border-left: 4px solid #d99a1f;
        padding: 9px 14px;
        margin: 22px 0 12px 0;
        border-radius: 4px;
        text-transform: uppercase;
        font-size: 13.5px;
    }

    .result-box {
        background: #ffffff;
        border: 1px solid #cfe8e3;
        border-top: 3px solid #12a396;
        border-radius: 8px;
        padding: 18px 22px;
        margin-bottom: 16px;
        box-shadow: 0 2px 10px rgba(15,60,60,0.06);
    }
    .gene-name {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 26px;
        font-weight: 800;
        color: #0b3d3f;
        letter-spacing: .3px;
    }
    .gene-meta {
        font-size: 13.5px;
        color: #3f6b67;
        margin-top: 4px;
    }

    .photo-card {
        border-radius: 8px;
        padding: 14px;
        border: 1px solid #d7e9e5;
        height: 100%;
        box-shadow: 0 1px 4px rgba(15,60,60,0.06);
    }
    .photo-card-sd { background: #e6f5f3; border-top: 4px solid #12a396; }
    .photo-card-ld { background: #fbf1dc; border-top: 4px solid #d99a1f; }
    .photo-card-season { background: #e9f6ec; border-top: 4px solid #2f9e5e; }

    .photo-label {
        font-weight: 700;
        font-size: 14.5px;
        color: #123c3a;
        margin-bottom: 6px;
    }
    .photo-value {
        font-size: 13px;
        color: #2c4f4c;
        line-height: 1.55;
    }

    .source-tag {
        display: inline-block;
        background: #eaf6f4;
        border: 1px solid #b9dcd5;
        border-radius: 4px;
        padding: 3px 10px;
        margin: 2px 4px 2px 0;
        font-size: 12px;
        color: #0f5c56;
        font-weight: 700;
    }
    .source-tag-db { background: #e9f6ec; border-color: #9fd6b5; color: #1f7a45; }
    .source-tag-ncbi { background: #e6f5f3; border-color: #9edac9; color: #0f8c82; }
    .source-tag-go { background: #fbf1dc; border-color: #e6c98f; color: #9c6f17; }
    .source-tag-seed { background: #f1e9fb; border-color: #cfa9e8; color: #6a1a9c; }

    .xref-box {
        background: #f7fcfb;
        border: 1px solid #cfe8e3;
        border-left: 4px solid #12a396;
        border-radius: 6px;
        padding: 14px 16px;
        margin: 10px 0 16px 0;
        font-size: 13px;
        color: #24443f;
        line-height: 1.6;
    }
    .xref-label {
        font-weight: 700;
        color: #0f8c82;
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
    .evidence-single { background: #fbf1dc; color: #9c6f17; border: 1px solid #e6c98f; }
    .evidence-replicated { background: #e9f6ec; color: #1f7a45; border: 1px solid #9fd6b5; }

    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 2px solid #cfe8e3;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #2c4f4c;
        font-weight: 700;
        background: #e6f5f3;
        border-radius: 6px 6px 0 0;
        padding: 8px 14px;
    }
    .stTabs [aria-selected="true"] {
        color: #ffffff !important;
        background: #0f8c82 !important;
        border-bottom: 2px solid #d99a1f !important;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #cfe8e3;
        border-radius: 8px;
        overflow: hidden;
    }

    .stButton>button, .stDownloadButton>button, .stFormSubmitButton>button {
        background: #0f8c82 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 5px !important;
        font-weight: 700 !important;
    }
    .stButton>button:hover, .stDownloadButton>button:hover, .stFormSubmitButton>button:hover {
        background: #d99a1f !important;
        color: #1a1a1a !important;
    }

    section[data-testid="stSidebar"] {
        background: #eaf6f4;
        border-right: 2px solid #bfe3dc;
    }

    h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif; color: #123c3a; }

    @media (max-width: 900px) {
        .main-header { flex-direction: column; align-items: flex-start; }
        .main-header-art { display: none; }
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="ncbi-topstrip">🧬 PHYSIOLOGICAL RESEARCH RESOURCE &nbsp;·&nbsp; cross-referenced live with NCBI, PubMed, CircaDB, GEO, UniProt &amp; Gene Ontology</div>', unsafe_allow_html=True)


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

try:
    setup_cursor.execute("""
        ALTER TABLE gene_seasonal_function
        ADD COLUMN photoperiod_condition VARCHAR(5) DEFAULT NULL
    """)
    conn.commit()
except mysql.connector.Error:
    conn.rollback()

conn.commit()

_SCHEMA_MIGRATIONS = [
    ("gene_seasonal_function", "ADD COLUMN p_value DECIMAL(10,6) DEFAULT NULL"),
    ("gene_seasonal_function", "ADD COLUMN sample_size INT DEFAULT NULL"),
    ("gene_seasonal_function", "ADD COLUMN ci_lower DECIMAL(8,3) DEFAULT NULL"),
    ("gene_seasonal_function", "ADD COLUMN ci_upper DECIMAL(8,3) DEFAULT NULL"),
    ("gene_seasonal_function", "ADD COLUMN evidence_level VARCHAR(40) DEFAULT NULL"),
    ("genes", "ADD COLUMN hgnc_id VARCHAR(20) DEFAULT NULL"),
    ("genes", "ADD COLUMN ensembl_id VARCHAR(30) DEFAULT NULL"),
    ("genes", "ADD COLUMN uniprot_id VARCHAR(20) DEFAULT NULL"),
    ("genes", "ADD COLUMN symbol_validated_at TIMESTAMP NULL DEFAULT NULL"),
    ("community_contributions", "ADD COLUMN status VARCHAR(10) DEFAULT 'pending'"),
    ("community_contributions", "ADD COLUMN p_value DECIMAL(10,6) DEFAULT NULL"),
    ("community_contributions", "ADD COLUMN sample_size INT DEFAULT NULL"),
    ("community_contributions", "ADD COLUMN ci_lower DECIMAL(8,3) DEFAULT NULL"),
    ("community_contributions", "ADD COLUMN ci_upper DECIMAL(8,3) DEFAULT NULL"),
    ("community_contributions", "ADD COLUMN evidence_level VARCHAR(40) DEFAULT NULL"),
    ("community_contributions", "ADD COLUMN hgnc_id VARCHAR(20) DEFAULT NULL"),
    ("community_contributions", "ADD COLUMN ensembl_id VARCHAR(30) DEFAULT NULL"),
    ("community_contributions", "ADD COLUMN uniprot_id VARCHAR(20) DEFAULT NULL"),
    ("community_contributions", "ADD COLUMN reviewed_by VARCHAR(100) DEFAULT NULL"),
    ("community_contributions", "ADD COLUMN reviewed_at TIMESTAMP NULL DEFAULT NULL"),
]
for _table, _clause in _SCHEMA_MIGRATIONS:
    try:
        setup_cursor.execute(f"ALTER TABLE {_table} {_clause}")
        conn.commit()
    except mysql.connector.Error:
        conn.rollback()

setup_cursor.execute("""
CREATE TABLE IF NOT EXISTS dataset_meta (
    id INT PRIMARY KEY DEFAULT 1,
    version VARCHAR(20) DEFAULT 'v1.0',
    doi VARCHAR(100) DEFAULT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    notes VARCHAR(300) DEFAULT NULL
)""")
conn.commit()
setup_cursor.execute("SELECT COUNT(*) FROM dataset_meta")
if setup_cursor.fetchone()[0] == 0:
    setup_cursor.execute(
        "INSERT INTO dataset_meta (id, version, doi, notes) VALUES (1, %s, %s, %s)",
        ("v1.0", None, "Initial release")
    )
    conn.commit()

EVIDENCE_LEVELS = [
    "Direct experimental (this study)",
    "Inferred (homolog/ortholog)",
    "Predicted/computational",
    "Literature-established (secondary review)",
]

CONTRIBUTION_STATUS_LABELS = {
    "pending": "🕓 Pending Review",
    "approved": "✅ Approved",
    "rejected": "❌ Rejected",
}

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
    "Gene Ontology": {"url": "https://geneontology.org/",
                       "desc": "Controlled-vocabulary annotation of gene function, process, and location."},
}

# ════════════════════════════════════════════════════════════════
# CURATED SEED LIBRARY — established seasonal-physiology gene sets
# ════════════════════════════════════════════════════════════════
PARAMETER_LIBRARY = {
    "Photoperiod / Melatonin Pathway": {
        "keywords": ["melatonin", "photoperiod", "pineal", "short day", "long day",
                     "AANAT", "ASMT", "HIOMT"],
        "description": (
            "Day length is transduced by the retina → retinohypothalamic tract → SCN → "
            "PVN → superior cervical ganglion → pineal gland. The pineal converts "
            "serotonin to melatonin at night; the *duration* of nightly melatonin "
            "secretion (not its amplitude) encodes night length and is the core "
            "'calendar' signal of the mammalian/avian photoperiodic system."
        ),
        "seed_genes": [
            {"symbol": "AANAT", "role": "Rate-limiting enzyme for melatonin synthesis in the pineal gland; activity rises at night, encoding night length."},
            {"symbol": "ASMT", "role": "(HIOMT) Final enzymatic step converting N-acetylserotonin to melatonin."},
            {"symbol": "TPH1", "role": "Tryptophan hydroxylase 1; synthesizes serotonin, the precursor to melatonin, in the pineal gland."},
            {"symbol": "DDC", "role": "Dopa decarboxylase; contributes to serotonin synthesis upstream of melatonin."},
            {"symbol": "MTNR1A", "role": "Melatonin receptor 1 (MT1); mediates melatonin's phase-shifting and reproductive-axis effects."},
            {"symbol": "MTNR1B", "role": "Melatonin receptor 2 (MT2); implicated in metabolic/glucose regulation and circadian phase."},
            {"symbol": "GPR50", "role": "Melatonin-related orphan receptor; modulates MT1 signaling, implicated in seasonal metabolic adaptation."},
            {"symbol": "TSHB", "role": "Thyroid-stimulating hormone beta; induced in the pars tuberalis under long photoperiod, triggers the seasonal thyroid-hormone switch."},
            {"symbol": "DIO2", "role": "Type 2 deiodinase; locally activates T3, upregulated under long-day/summer-like photoperiod."},
            {"symbol": "DIO3", "role": "Type 3 deiodinase; inactivates T3, upregulated under short-day/winter-like photoperiod."},
            {"symbol": "EYA3", "role": "Transcriptional co-activator inducing TSHB under long photoperiod; core node of the seasonal switch."},
        ],
    },
    "Circadian Clock Core": {
        "keywords": ["circadian", "clock gene", "BMAL1", "CRY", "PER", "CLOCK"],
        "description": (
            "The core transcription-translation feedback loop that sets endogenous "
            "~24h rhythms, including the phase of pineal AANAT/melatonin rhythm "
            "that generates the photoperiodic signal itself."
        ),
        "seed_genes": [
            {"symbol": "CLOCK", "role": "Core positive-arm transcription factor; dimerizes with BMAL1 to drive E-box gene expression."},
            {"symbol": "ARNTL", "role": "(BMAL1) Obligate dimerization partner of CLOCK; essential positive-arm clock component."},
            {"symbol": "PER1", "role": "Negative-arm clock gene; represses CLOCK:BMAL1 activity, entrained by light."},
            {"symbol": "PER2", "role": "Negative-arm clock gene; central to peripheral clock synchronization and photoperiod encoding."},
            {"symbol": "CRY1", "role": "Negative-arm clock gene; represses CLOCK:BMAL1, modulates period length."},
            {"symbol": "CRY2", "role": "Negative-arm clock gene; paralog of CRY1 with overlapping repressor function."},
            {"symbol": "NR1D1", "role": "(Rev-erbα) Nuclear receptor linking clock output to metabolic gene regulation."},
            {"symbol": "RORA", "role": "Nuclear receptor; activates BMAL1 transcription, opposing Rev-erbα."},
        ],
    },
    "Seasonal Reproduction (HPG axis)": {
        "keywords": ["reproduction", "gonadotropin", "seasonal breeding", "kisspeptin", "GnRH"],
        "description": (
            "Downstream of the thyroid-hormone seasonal switch, this hypothalamic-"
            "pituitary-gonadal circuitry gates reproductive activity in and out of "
            "breeding season."
        ),
        "seed_genes": [
            {"symbol": "KISS1", "role": "Kisspeptin; primary upstream activator of GnRH neurons."},
            {"symbol": "KISS1R", "role": "Kisspeptin receptor (GPR54); mediates the kisspeptin signal onto GnRH neurons."},
            {"symbol": "GNRH1", "role": "Gonadotropin-releasing hormone; drives pituitary LH/FSH release."},
            {"symbol": "RFRP3", "role": "(NPVF) RFamide-related peptide; seasonally gates reproductive axis activity."},
            {"symbol": "TAC3", "role": "Neurokinin B; co-expressed with kisspeptin, modulates GnRH pulsatility."},
            {"symbol": "LHB", "role": "Luteinizing hormone beta subunit; pituitary output regulating gonadal function."},
            {"symbol": "FSHB", "role": "Follicle-stimulating hormone beta subunit; pituitary output regulating gametogenesis."},
        ],
    },
    "Thyroid-Hormone Seasonal Switch": {
        "keywords": ["thyroid", "deiodinase", "pars tuberalis", "TSH"],
        "description": (
            "The TSH–deiodinase feed-forward loop in the pars tuberalis/hypothalamus "
            "that converts the melatonin duration signal into a binary long-day vs. "
            "short-day physiological state (Nakao et al. 2008; Hanon et al. 2008)."
        ),
        "seed_genes": [
            {"symbol": "TSHB", "role": "Thyroid-stimulating hormone beta; pars tuberalis long-day output signal."},
            {"symbol": "TSHR", "role": "TSH receptor on pars tuberalis/ependymal cells; receives the TSHB signal."},
            {"symbol": "DIO2", "role": "Activates thyroid hormone (T3) locally; marks the long-day/summer state."},
            {"symbol": "DIO3", "role": "Inactivates thyroid hormone; marks the short-day/winter state."},
            {"symbol": "EYA3", "role": "Induces TSHB transcription under long photoperiod."},
        ],
    },
}

# ════════════════════════════════════════════════════════════════
# LIVE NCBI CROSS-REFERENCE (via NCBI E-utilities)
# ════════════════════════════════════════════════════════════════
@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def fetch_ncbi_gene_summary(gene_symbol: str, organism: str = "Homo sapiens"):
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


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def fetch_ncbi_gene_search(query_term: str, organism: str = "Homo sapiens", retmax: int = 15):
    try:
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        term = f"({query_term}[All Fields]) AND {organism}[Organism] AND alive[prop]"
        params = {"db": "gene", "term": term, "retmode": "json", "retmax": retmax}
        r = requests.get(search_url, params=params, timeout=8)
        r.raise_for_status()
        ids = r.json().get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []

        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        params2 = {"db": "gene", "id": ",".join(ids), "retmode": "json"}
        r2 = requests.get(summary_url, params=params2, timeout=8)
        r2.raise_for_status()
        result = r2.json().get("result", {})

        genes = []
        for gid in ids:
            item = result.get(gid)
            if not item:
                continue
            genes.append({
                "symbol": item.get("name", ""),
                "name": item.get("description", ""),
                "gene_id": gid,
                "url": f"https://www.ncbi.nlm.nih.gov/gene/{gid}",
            })
        return genes
    except Exception:
        return []


def uniprot_search_url(gene_symbol: str) -> str:
    return f"https://www.uniprot.org/uniprotkb?query={gene_symbol}+AND+organism_id:9606"


# ════════════════════════════════════════════════════════════════
# HGNC IDENTIFIER VALIDATION
# ════════════════════════════════════════════════════════════════
@st.cache_data(ttl=60 * 60 * 24 * 7, show_spinner=False)
def fetch_hgnc_info(gene_symbol: str):
    headers = {"Accept": "application/json"}
    try:
        url = f"https://rest.genenames.org/fetch/symbol/{gene_symbol.upper()}"
        r = requests.get(url, headers=headers, timeout=6)
        r.raise_for_status()
        docs = r.json().get("response", {}).get("docs", [])

        if not docs:
            search_url = f"https://rest.genenames.org/search/symbol/{gene_symbol.upper()}"
            r2 = requests.get(search_url, headers=headers, timeout=6)
            r2.raise_for_status()
            hits = r2.json().get("response", {}).get("docs", [])
            if not hits:
                return None
            hgnc_id = hits[0].get("hgnc_id")
            r3 = requests.get(f"https://rest.genenames.org/fetch/hgnc_id/{hgnc_id}",
                               headers=headers, timeout=6)
            r3.raise_for_status()
            docs = r3.json().get("response", {}).get("docs", [])
            if not docs:
                return None

        d = docs[0]
        uniprot_ids = d.get("uniprot_ids") or []
        return {
            "hgnc_id": d.get("hgnc_id", ""),
            "official_symbol": d.get("symbol", gene_symbol.upper()),
            "official_name": d.get("name", ""),
            "ensembl_id": d.get("ensembl_gene_id", "") or "",
            "uniprot_id": uniprot_ids[0] if uniprot_ids else "",
            "locus_type": d.get("locus_type", ""),
            "hgnc_url": f"https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/{d.get('hgnc_id','')}",
        }
    except Exception:
        return None


def hgnc_badge(hgnc_info):
    if hgnc_info:
        return (f'<span class="source-tag source-tag-db">✔ HGNC validated · '
                f'{hgnc_info["hgnc_id"]}</span>')
    return '<span class="source-tag" style="background:#fdf0e3;border-color:#e6c393;color:#9c5a17;">⚠ Not HGNC-validated</span>'


def evidence_level_badge(level: str) -> str:
    if not level:
        return '<span class="evidence-badge evidence-single">Evidence level not specified</span>'
    colors = {
        "Direct experimental (this study)": "evidence-replicated",
        "Inferred (homolog/ortholog)": "evidence-single",
        "Predicted/computational": "evidence-single",
        "Literature-established (secondary review)": "evidence-replicated",
    }
    css_class = colors.get(level, "evidence-single")
    return f'<span class="evidence-badge {css_class}">{level}</span>'


def is_valid_source_reference(ref: str) -> bool:
    import re
    ref = ref.strip()
    if not ref:
        return False
    patterns = [
        r'^(PMID:?\s*)?\d{4,9}$',
        r'^10\.\d{4,9}/\S+$',
        r'^GSE\d+$', r'^GSM\d+$', r'^GDS\d+$',
    ]
    return any(re.match(p, ref, re.IGNORECASE) for p in patterns)


@st.cache_data(ttl=60 * 5, show_spinner=False)
def get_dataset_meta(_conn):
    try:
        df = pd.read_sql("SELECT version, doi, last_updated, notes FROM dataset_meta WHERE id = 1", _conn)
        if not df.empty:
            return df.iloc[0].to_dict()
    except Exception:
        pass
    return {"version": "v1.0", "doi": None, "last_updated": None, "notes": None}


def generate_bibtex_citation(meta: dict) -> str:
    year = "2026"
    version = meta.get("version") or "v1.0"
    doi_line = f"  doi = {{{meta['doi']}}},\n" if meta.get("doi") else ""
    return (
        "@misc{seasonal_gene_db_" + year + ",\n"
        "  author = {S. Unnati},\n"
        "  title = {Seasonal Physiology Gene Database},\n"
        f"  year = {{{year}}},\n"
        f"  note = {{Version {version}}},\n"
        f"{doi_line}"
        "  howpublished = {\\url{https://seasonal-gene-db-wb4nzf4rwezxmhzrtrcimr.streamlit.app/}}\n"
        "}"
    )


def evidence_badge(n_sources: int) -> str:
    if n_sources >= 2:
        return '<span class="evidence-badge evidence-replicated">Replicated across ≥2 entries</span>'
    return '<span class="evidence-badge evidence-single">Single curated entry</span>'


@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)
def fetch_pubmed_photoperiod_papers(gene_symbol: str, max_results: int = 8):
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
# LIVE GENE ONTOLOGY CROSS-REFERENCE (via EBI QuickGO)
# ════════════════════════════════════════════════════════════════
@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def fetch_go_terms(query: str, limit: int = 8):
    try:
        url = "https://www.ebi.ac.uk/QuickGO/services/ontology/go/search"
        params = {"query": query, "limit": limit}
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
        results = data.get("results", [])
        return [
            {"id": item.get("id"), "name": item.get("name"), "aspect": item.get("aspect")}
            for item in results if item.get("id")
        ]
    except Exception:
        return []


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def fetch_go_annotated_genes(go_id: str, taxon_id: int = 9606, limit: int = 25):
    try:
        url = "https://www.ebi.ac.uk/QuickGO/services/annotation/search"
        params = {"goId": go_id, "taxonId": taxon_id,
                   "geneProductType": "protein", "limit": limit}
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
        results = data.get("results", [])
        symbols = set()
        for item in results:
            sym = item.get("symbol") or item.get("geneProductId")
            if sym:
                symbols.add(sym)
        return sorted(symbols)
    except Exception:
        return []


def render_venn(sets_dict: dict):
    names = list(sets_dict.keys())
    colors = ["#205493", "#e8820c", "#1f9d55"]

    fig = go.Figure()
    fig.update_xaxes(visible=False, range=[-2.2, 2.2])
    fig.update_yaxes(visible=False, range=[-1.8, 1.8], scaleanchor="x", scaleratio=1)

    if len(names) == 2:
        A, B = sets_dict[names[0]], sets_dict[names[1]]
        centers = [(-0.55, 0), (0.55, 0)]
        radius = 1.1
        for (cx, cy), color in zip(centers, colors[:2]):
            fig.add_shape(type="circle", x0=cx - radius, y0=cy - radius,
                           x1=cx + radius, y1=cy + radius,
                           line_color=color, fillcolor=color, opacity=0.35)
        fig.add_annotation(x=-1.1, y=0.85, text=f"<b>{names[0]}</b>", showarrow=False, font=dict(size=13, color=colors[0]))
        fig.add_annotation(x=1.1, y=0.85, text=f"<b>{names[1]}</b>", showarrow=False, font=dict(size=13, color=colors[1]))
        fig.add_annotation(x=-0.95, y=0, text=str(len(A - B)), showarrow=False, font=dict(size=16))
        fig.add_annotation(x=0.95, y=0, text=str(len(B - A)), showarrow=False, font=dict(size=16))
        fig.add_annotation(x=0, y=0, text=str(len(A & B)), showarrow=False, font=dict(size=16, color="#1a1a1a"))
    elif len(names) >= 3:
        names = names[:3]
        A, B, C = sets_dict[names[0]], sets_dict[names[1]], sets_dict[names[2]]
        centers = [(-0.55, 0.35), (0.55, 0.35), (0, -0.55)]
        radius = 1.15
        for (cx, cy), color in zip(centers, colors):
            fig.add_shape(type="circle", x0=cx - radius, y0=cy - radius,
                           x1=cx + radius, y1=cy + radius,
                           line_color=color, fillcolor=color, opacity=0.3)
        fig.add_annotation(x=-1.15, y=1.35, text=f"<b>{names[0]}</b>", showarrow=False, font=dict(size=12, color=colors[0]))
        fig.add_annotation(x=1.15, y=1.35, text=f"<b>{names[1]}</b>", showarrow=False, font=dict(size=12, color=colors[1]))
        fig.add_annotation(x=0, y=-1.55, text=f"<b>{names[2]}</b>", showarrow=False, font=dict(size=12, color=colors[2]))

        only_a = len(A - B - C)
        only_b = len(B - A - C)
        only_c = len(C - A - B)
        ab = len((A & B) - C)
        ac = len((A & C) - B)
        bc = len((B & C) - A)
        abc = len(A & B & C)

        fig.add_annotation(x=-0.85, y=0.65, text=str(only_a), showarrow=False, font=dict(size=15))
        fig.add_annotation(x=0.85, y=0.65, text=str(only_b), showarrow=False, font=dict(size=15))
        fig.add_annotation(x=0, y=-0.95, text=str(only_c), showarrow=False, font=dict(size=15))
        fig.add_annotation(x=0, y=0.55, text=str(ab), showarrow=False, font=dict(size=14))
        fig.add_annotation(x=-0.55, y=-0.15, text=str(ac), showarrow=False, font=dict(size=14))
        fig.add_annotation(x=0.55, y=-0.15, text=str(bc), showarrow=False, font=dict(size=14))
        fig.add_annotation(x=0, y=0.1, text=f"<b>{abc}</b>", showarrow=False, font=dict(size=14, color="#1a1a1a"))

    fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10),
                       plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#123c3a')
    return fig


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
        4. Nakao, N., Ono, H., Yamamura, T., et al. (2008). Thyrotrophin in the pars
           tuberalis triggers photoperiodic response. Nature, 452(7185), 317-322.
        5. Hanon, E. A., Lincoln, G. A., Fustin, J. M., et al. (2008). Ancestral TSH
           mechanism signals summer in a photoperiodic mammal. Current Biology, 18(15), 1147-1152.
        """)
        st.caption("Individual gene entries also cite a PMID/reference — see the "
                   "'Reference (PMID)' column in each result table.")

    _meta = get_dataset_meta(conn)
    st.caption(
        f"**Dataset version:** {_meta.get('version') or 'v1.0'}"
        + (f" · DOI: {_meta.get('doi')}" if _meta.get('doi') else "")
        + (f"  \nLast updated: {_meta.get('last_updated')}" if _meta.get('last_updated') else "")
    )
    st.caption("Suggested citation for this tool:")
    st.code(
        "S.Unnati (2026). Seasonal Physiology Gene Database.\n"
        "https://seasonal-gene-db-wb4nzf4rwezxmhzrtrcimr.streamlit.app/",
        language=None
    )
    with st.expander("Export as BibTeX"):
        st.code(generate_bibtex_citation(_meta), language=None)

# ════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════
st.markdown("""
<div class="main-header">
    <div class="main-header-text">
        <p class="main-title">🧬 SEASONAL PHYSIOLOGY GENE DATABASE</p>
        <p class="main-subtitle">A photoperiod- and season-linked gene expression resource, cross-referenced live with NCBI, CircaDB, PubMed, GEO Datasets, UniProt, and Gene Ontology.</p>
        <p class="affil">Photoperiod &amp; Melatonin · Circadian Clock Core · Seasonal Reproduction · Thyroid-Hormone Switch</p>
    </div>
    <div class="main-header-art">
        <svg width="230" height="170" viewBox="0 0 230 170" xmlns="http://www.w3.org/2000/svg">
            <path d="M 20 20 C 45 45, 45 65, 20 85 C -5 105, -5 125, 20 150" fill="none" stroke="#12a396" stroke-width="2.5" opacity="0.85"></path>
            <path d="M 55 20 C 30 45, 30 65, 55 85 C 80 105, 80 125, 55 150" fill="none" stroke="#d99a1f" stroke-width="2.5" opacity="0.85"></path>
            <line x1="22" y1="30" x2="53" y2="30" stroke="#7fb8b0" stroke-width="1.6"></line>
            <line x1="16" y1="50" x2="59" y2="50" stroke="#7fb8b0" stroke-width="1.6"></line>
            <line x1="20" y1="70" x2="55" y2="70" stroke="#7fb8b0" stroke-width="1.6"></line>
            <line x1="16" y1="90" x2="59" y2="90" stroke="#7fb8b0" stroke-width="1.6"></line>
            <line x1="20" y1="110" x2="55" y2="110" stroke="#7fb8b0" stroke-width="1.6"></line>
            <line x1="16" y1="130" x2="59" y2="130" stroke="#7fb8b0" stroke-width="1.6"></line>
            <rect x="80" y="118" width="7" height="18" fill="#12a396" opacity="0.75"></rect>
            <rect x="91" y="105" width="7" height="31" fill="#d99a1f" opacity="0.75"></rect>
            <rect x="102" y="95" width="7" height="41" fill="#2f9e5e" opacity="0.75"></rect>
            <rect x="113" y="112" width="7" height="24" fill="#12a396" opacity="0.75"></rect>
            <g transform="translate(175,35)" stroke="#d99a1f" stroke-width="2" fill="none" opacity="0.9">
                <circle r="10" fill="#fbf1dc" stroke="#d99a1f"></circle>
                <line x1="0" y1="-16" x2="0" y2="-20"></line>
                <line x1="0" y1="16" x2="0" y2="20"></line>
                <line x1="-16" y1="0" x2="-20" y2="0"></line>
                <line x1="16" y1="0" x2="20" y2="0"></line>
                <line x1="-11" y1="-11" x2="-14" y2="-14"></line>
                <line x1="11" y1="11" x2="14" y2="14"></line>
                <line x1="-11" y1="11" x2="-14" y2="14"></line>
                <line x1="11" y1="-11" x2="14" y2="-14"></line>
            </g>
            <g transform="translate(205,80)" stroke="#12a396" stroke-width="1.8" opacity="0.9">
                <line x1="0" y1="-13" x2="0" y2="13"></line>
                <line x1="-11.3" y1="-6.5" x2="11.3" y2="6.5"></line>
                <line x1="-11.3" y1="6.5" x2="11.3" y2="-6.5"></line>
            </g>
            <g transform="translate(150,80)" opacity="0.9">
                <path d="M 0 12 C -8 2, -8 -10, 0 -14 C 8 -10, 8 2, 0 12 Z" fill="#e0685a" stroke="#c94f42" stroke-width="1"></path>
                <line x1="0" y1="12" x2="0" y2="-10" stroke="#c94f42" stroke-width="1"></line>
            </g>
            <g transform="translate(180,125)" opacity="0.9">
                <path d="M 0 15 C 0 0, -10 -5, -12 -14 C -3 -12, 0 -2, 0 8" fill="#2f9e5e"></path>
                <path d="M 0 15 C 0 2, 9 -3, 11 -11 C 3 -9, 0 0, 0 8" fill="#5cbd7f"></path>
                <line x1="0" y1="15" x2="0" y2="20" stroke="#2f9e5e" stroke-width="2"></line>
            </g>
        </svg>
    </div>
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
    ["🔍 Universal Search", "📊 Compare Genes", "✍️ Contribute Data",
     "🗂 Browse All Genes", "🧪 Methodology", "🔐 Admin: Bulk Import"]
)


def match_seed_library(query: str):
    q = query.strip().lower()
    if not q:
        return {}
    matches = {}
    for pname, pdata in PARAMETER_LIBRARY.items():
        name_hit = q in pname.lower()
        kw_hit = any(q in kw.lower() or kw.lower() in q for kw in pdata["keywords"])
        gene_hit = any(q == g["symbol"].lower() for g in pdata["seed_genes"])
        if name_hit or kw_hit or gene_hit:
            matches[pname] = pdata
    return matches


# ════════════════════════════════════════════════════════════════
# RELEVANCE GATE + UNIFIED RESULT TEMPLATE
#
# Scope: Photoperiod / Melatonin, Circadian Clock Core, Seasonal
# Reproduction (HPG axis), Thyroid-Hormone Seasonal Switch — plus
# whatever is curated into the SQL tables under that scope.
#
# 🔧 FIX: when the query is an EXACT gene symbol (e.g. "DIO2"), the
# search now returns ONLY that gene — no sibling genes from the same
# pathway are pulled in, and the pathway-wide description block is
# suppressed (it used to mention other gene names, which read as if
# "other genes' data" was being shown). A new `matched_via_exact_gene`
# flag tells the UI layer to skip the multi-gene pathway description
# and go straight to that one gene's card + graphs.
# ════════════════════════════════════════════════════════════════

def get_seed_role_for_gene(symbol: str):
    for pname, pdata in PARAMETER_LIBRARY.items():
        for g in pdata["seed_genes"]:
            if g["symbol"].upper() == symbol.upper():
                return pname, g["role"]
    return None, None


def get_relevant_genes(raw_query: str, conn):
    """
    Relevance gate for the universal search box.

    Returns:
        matched_genes (set[str])
        matched_parameters (dict)   — only populated for PATHWAY/keyword
                                       searches, never for an exact-gene
                                       search (see matched_via_exact_gene)
        db_pathway_hit (bool)
        matched_via_exact_gene (bool) — True if the query resolved to one
                                       exact gene symbol. UI should render
                                       ONLY that gene, with no pathway-wide
                                       description block.
    """
    q = raw_query.strip()
    symbol = q.upper()
    matched_genes = set()
    matched_parameters = {}
    db_pathway_hit = False
    matched_via_exact_gene = False

    if not q:
        return matched_genes, matched_parameters, db_pathway_hit, matched_via_exact_gene

    exact_match_found = False

    # (a) Exact gene symbol already curated in this database
    try:
        exists_df = pd.read_sql(
            "SELECT DISTINCT gene_symbol FROM genes WHERE gene_symbol = %s",
            conn, params=[symbol]
        )
        if not exists_df.empty:
            matched_genes.add(symbol)
            exact_match_found = True
            matched_via_exact_gene = True
    except Exception:
        pass

    # (b) Exact gene symbol present in the literature seed library
    pname_hit, _ = get_seed_role_for_gene(symbol)
    if pname_hit:
        matched_genes.add(symbol)
        exact_match_found = True
        matched_via_exact_gene = True
        # NOTE: we deliberately do NOT add the whole pathway to
        # matched_parameters here anymore — an exact-gene search should
        # stay scoped to that one gene, not surface every sibling gene's
        # name via the pathway description text.

    if exact_match_found:
        return matched_genes, matched_parameters, db_pathway_hit, matched_via_exact_gene

    # (c) Query matches a defined pathway/parameter name or keyword —
    #     pull in every gene belonging to that pathway (this path is
    #     only reached for non-exact / pathway-style searches, e.g.
    #     "melatonin", "thyroid switch")
    seed_matches = match_seed_library(q)
    for pname, pdata in seed_matches.items():
        matched_parameters[pname] = pdata
        for g in pdata["seed_genes"]:
            matched_genes.add(g["symbol"].upper())

    # (d) Query matches this database's own curated pathway/functional-role text
    try:
        like = f"%{q}%"
        kw_df = pd.read_sql(
            """SELECT DISTINCT g.gene_symbol
               FROM gene_seasonal_function gsf
               JOIN genes g ON gsf.gene_id = g.id
               WHERE g.full_name LIKE %s OR gsf.pathway LIKE %s OR gsf.functional_role LIKE %s""",
            conn, params=[like, like, like]
        )
        if not kw_df.empty:
            db_pathway_hit = True
            matched_genes |= set(s.upper() for s in kw_df['gene_symbol'].tolist())
    except Exception:
        pass

    return matched_genes, matched_parameters, db_pathway_hit, matched_via_exact_gene


def render_gene_card(symbol: str, conn, raw_query: str, refs_used: set):
    """
    Single, unified card layout used for EVERY gene the search returns —
    whether it was found in the curated DB, the literature seed library,
    a DB pathway-keyword match, or a combination of these. Structure never
    changes based on source; only the content within each fixed section does.
    """
    seed_pname, seed_role = get_seed_role_for_gene(symbol)

    gene_query = """
        SELECT g.full_name, g.category, g.hgnc_id, g.ensembl_id, g.uniprot_id,
               s.name AS season, gsf.expression_level,
               gsf.fold_change, gsf.functional_role,
               gsf.pathway, gsf.tissue_type, gsf.study_reference,
               gsf.photoperiod_condition, gsf.p_value, gsf.sample_size,
               gsf.ci_lower, gsf.ci_upper, gsf.evidence_level
        FROM gene_seasonal_function gsf
        JOIN genes g ON gsf.gene_id = g.id
        JOIN seasons s ON gsf.season_id = s.id
        WHERE g.gene_symbol = %s
        ORDER BY FIELD(s.name, 'Winter','Spring','Summer','Autumn')
    """
    try:
        df = pd.read_sql(gene_query, conn, params=[symbol])
    except Exception:
        df = pd.DataFrame()

    full_name = df['full_name'][0] if not df.empty else (
        f"{seed_pname} gene set member" if seed_pname else symbol
    )
    category = df['category'][0] if not df.empty else (seed_pname or "Uncategorized")
    n_evidence = df['study_reference'].nunique() if not df.empty else 0

    hgnc_info = None
    stored_hgnc = df['hgnc_id'][0] if not df.empty else None
    if not df.empty and pd.notna(stored_hgnc) and stored_hgnc:
        hgnc_info = {
            "hgnc_id": stored_hgnc,
            "ensembl_id": df['ensembl_id'][0] if pd.notna(df['ensembl_id'][0]) else "",
            "uniprot_id": df['uniprot_id'][0] if pd.notna(df['uniprot_id'][0]) else "",
        }
    else:
        hgnc_info = fetch_hgnc_info(symbol)
        if hgnc_info and not df.empty:
            try:
                upd = conn.cursor()
                upd.execute(
                    "UPDATE genes SET hgnc_id=%s, ensembl_id=%s, uniprot_id=%s, symbol_validated_at=NOW() "
                    "WHERE gene_symbol=%s",
                    (hgnc_info["hgnc_id"], hgnc_info["ensembl_id"], hgnc_info["uniprot_id"], symbol)
                )
                conn.commit()
            except Exception:
                conn.rollback()

    # ── Fixed Section 1: header ──────────────────────────────────
    id_line = ""
    if hgnc_info:
        id_line = (f'<div class="gene-meta">HGNC: {hgnc_info.get("hgnc_id","—")}'
                    f' &nbsp;·&nbsp; Ensembl: {hgnc_info.get("ensembl_id") or "—"}'
                    f' &nbsp;·&nbsp; UniProt: {hgnc_info.get("uniprot_id") or "—"}</div>')
    st.markdown(f"""
    <div class="result-box">
        <span class="gene-name">{symbol}</span>{evidence_badge(max(n_evidence, 1 if seed_role else 0))}
        {hgnc_badge(hgnc_info)}
        <div class="gene-meta">{full_name} &nbsp;·&nbsp; Category: {category}</div>
        {id_line}
    </div>
    """, unsafe_allow_html=True)

    # ── Fixed Section 2: known role (curated functional_role, else seed role) ──
    st.markdown('<div class="section-header">Known Role in Photoperiod / Seasonal Physiology</div>', unsafe_allow_html=True)
    role_text = None
    if not df.empty and df['functional_role'].dropna().any():
        role_text = " ".join(df['functional_role'].dropna().unique().tolist())
    elif seed_role:
        role_text = seed_role
    if role_text:
        st.markdown(f'<div class="xref-box">{role_text}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="xref-box">No curated functional description yet for this gene in this database\'s defined scope.</div>', unsafe_allow_html=True)

    # ── Fixed Section 3: Season / Photoperiod comparison ─────────
    st.markdown('<div class="section-header">Photoperiod & Season Comparison</div>', unsafe_allow_html=True)
    if not df.empty:
        df['photoperiod_condition'] = df.apply(
            lambda r: r['photoperiod_condition'] if r['photoperiod_condition']
            else SEASON_TO_PHOTOPERIOD.get(r['season'], 'INT'),
            axis=1
        )
        sd_rows = df[df['photoperiod_condition'] == 'SD']
        ld_rows = df[df['photoperiod_condition'] == 'LD']

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
            season_icons = {'Winter': '❄️', 'Spring': '🌱', 'Summer': '☀️', 'Autumn': '🍂'}
            for _, r in df.iterrows():
                st.markdown(f"""<div class="photo-value">
                    {season_icons.get(r['season'], '')} <b>{r['season']}</b>: {r['expression_level']} ({r['fold_change']}x)
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        fig = px.bar(df, x='season', y='fold_change', color='season',
                     color_discrete_map={'Winter': '#1f5fa8', 'Spring': '#1f9d55',
                                          'Summer': '#e8820c', 'Autumn': '#b0453f'},
                     title=f"{symbol} — Fold Change by Season")
        fig.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#123c3a')
        fig.update_yaxes(title_text="Fold Change (relative to baseline)")
        fig.update_xaxes(title_text="Season")
        st.plotly_chart(fig, use_container_width=True, key=f"chart_{symbol}")

        # ── Venn diagram: up/down-regulated vs statistically significant seasons ──
        up_seasons = set(df.loc[df['fold_change'] > 1, 'season'])
        down_seasons = set(df.loc[df['fold_change'] < 1, 'season'])
        sig_seasons = set(df.loc[pd.to_numeric(df['p_value'], errors='coerce') < 0.05, 'season'])
        if up_seasons or down_seasons or sig_seasons:
            st.markdown('<div class="section-header">Venn Diagram — Regulation vs Significance by Season</div>', unsafe_allow_html=True)
            st.caption(f"How {symbol}'s seasons split across up-regulated, down-regulated, "
                       "and statistically significant (p < 0.05) fold-change values.")
            venn_fig = render_venn({
                "Up-regulated": up_seasons,
                "Down-regulated": down_seasons,
                "Significant (p<0.05)": sig_seasons
            })
            st.plotly_chart(venn_fig, use_container_width=True, key=f"venn_{symbol}")

        st.markdown('<div class="section-header">Evidence Grading (per row)</div>', unsafe_allow_html=True)
        for _, r in df.iterrows():
            stat_bits = []
            if pd.notna(r.get('p_value')):
                stat_bits.append(f"p = {r['p_value']}")
            if pd.notna(r.get('sample_size')):
                stat_bits.append(f"n = {int(r['sample_size'])}")
            if pd.notna(r.get('ci_lower')) and pd.notna(r.get('ci_upper')):
                stat_bits.append(f"95% CI [{r['ci_lower']}, {r['ci_upper']}]")
            stat_str = " &nbsp;·&nbsp; ".join(stat_bits) if stat_bits else "No p-value/CI/sample size curated for this row"
            st.markdown(
                f'{r["season"]} ({r["photoperiod_condition"]}): {evidence_level_badge(r.get("evidence_level"))} '
                f'&nbsp; <span style="font-size:12px;color:#35526e;">{stat_str}</span>',
                unsafe_allow_html=True
            )

        st.markdown('<div class="section-header">Full Data Table</div>', unsafe_allow_html=True)
        st.dataframe(
            df[['season', 'photoperiod_condition', 'expression_level', 'fold_change',
                'p_value', 'sample_size', 'ci_lower', 'ci_upper', 'evidence_level',
                'pathway', 'tissue_type', 'study_reference']].rename(columns={
                'season': 'Season', 'photoperiod_condition': 'Photoperiod',
                'expression_level': 'Expression', 'fold_change': 'Fold Change',
                'p_value': 'p-value', 'sample_size': 'n', 'ci_lower': 'CI Lower',
                'ci_upper': 'CI Upper', 'evidence_level': 'Evidence Level',
                'pathway': 'Pathway', 'tissue_type': 'Tissue', 'study_reference': 'Reference (PMID)'
            }),
            use_container_width=True
        )
        for ref in df['study_reference'].dropna().unique().tolist():
            refs_used.add(f"Curated study reference: {ref}")

        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download this gene's data as CSV", csv_bytes,
                            file_name=f"{symbol}_seasonal_data.csv", mime="text/csv",
                            key=f"dl_{symbol}")
    else:
        st.markdown(f"""
        <div class="xref-box">
            No quantitative season/photoperiod fold-change data has been curated yet for
            <b>{symbol}</b> in the SQL database — it is shown here on the strength of its
            established literature role (see above). Because there's no numeric data on file,
            no fold-change chart can be generated for it yet.<br><br>
            👉 Use the <b>Contribute Data</b> tab to add curated numeric data for {symbol}
            (with a PMID/DOI/GEO reference) — once approved by an admin, this section will
            automatically show its Short-Day vs Long-Day chart and seasonal trend graph.
        </div>
        """, unsafe_allow_html=True)

    # ── Fixed Section 4: Community-contributed data (approved only) ──
    try:
        comm_df = pd.read_sql(
            """SELECT season_or_condition AS "Season/Condition", expression_level AS "Expression",
                      fold_change AS "Fold Change", p_value AS "p-value", sample_size AS "n",
                      evidence_level AS "Evidence Level", functional_role AS "Functional Role",
                      pathway AS "Pathway", tissue_type AS "Tissue", source_db AS "Source DB",
                      source_reference AS "Reference", contributor_name AS "Contributor",
                      submitted_at AS "Submitted"
               FROM community_contributions
               WHERE gene_symbol = %s AND status = 'approved'
               ORDER BY submitted_at DESC""",
            conn, params=[symbol]
        )
    except Exception:
        comm_df = pd.DataFrame()
    if not comm_df.empty:
        st.markdown('<div class="section-header">🌍 Community-Contributed Data (Reviewed)</div>', unsafe_allow_html=True)
        st.caption("Approved by an admin after review. Still independently verify against the listed source before citing.")
        st.dataframe(comm_df, use_container_width=True)

    # ── Fixed Section 5: live NCBI cross-reference (enrichment only) ──
    st.markdown('<div class="section-header">🔬 Live NCBI Gene Cross-Reference</div>', unsafe_allow_html=True)
    with st.spinner(f"Checking NCBI Gene for {symbol}..."):
        ncbi_info = fetch_ncbi_gene_summary(symbol)
    if ncbi_info:
        st.markdown(f"""
        <div class="xref-box">
            <span class="xref-label">Official name:</span> {ncbi_info['official_name']}<br>
            <span class="xref-label">Chromosome:</span> {ncbi_info['chromosome']}
            &nbsp;·&nbsp; <span class="xref-label">Map location:</span> {ncbi_info['map_location']}<br>
            <span class="xref-label">NCBI summary:</span> {ncbi_info['summary']}<br><br>
            <a href="{ncbi_info['ncbi_url']}" target="_blank">View full NCBI Gene record →</a>
            &nbsp;|&nbsp;
            <a href="{uniprot_search_url(symbol)}" target="_blank">View on UniProt →</a>
        </div>
        """, unsafe_allow_html=True)
        refs_used.add(f"NCBI Gene ID {ncbi_info['gene_id']} — {ncbi_info['ncbi_url']}")
    else:
        st.markdown(f'<div class="xref-box">No live NCBI Gene record could be confirmed for human "{symbol}" at this time. This does not affect the curated result above.</div>', unsafe_allow_html=True)

    # ── Fixed Section 6: relevant literature (PubMed enrichment) ─
    st.markdown('<div class="section-header">📄 Related Literature (PubMed)</div>', unsafe_allow_html=True)
    with st.spinner(f"Checking PubMed for {symbol}..."):
        papers = fetch_pubmed_photoperiod_papers(symbol, max_results=5)
    if papers:
        for p in papers:
            st.markdown(
                f'<div class="xref-box"><b>{p["title"]}</b><br>'
                f'{p["authors"]} — <i>{p["journal"]}</i> ({p["year"]})<br>'
                f'<a href="{p["url"]}" target="_blank">View on PubMed →</a></div>',
                unsafe_allow_html=True
            )
            refs_used.add(f"PubMed ID {p['pmid']} — {p['url']}")
    else:
        st.markdown('<div class="xref-box">No PubMed articles specifically linking this gene to photoperiod/seasonal/circadian terms were found live.</div>', unsafe_allow_html=True)

    if seed_pname:
        refs_used.add("Nakao et al. 2008, Nature 452:317-322 — thyrotrophin/pars tuberalis photoperiodic switch")
        refs_used.add("Hanon et al. 2008, Current Biology 18:1147-1152 — ancestral TSH mechanism")


# ════════════════════════════════════════════════════════════════
# TAB 1 — UNIVERSAL SEARCH (gene symbol OR pathway/parameter, one box)
# ════════════════════════════════════════════════════════════════
with tab_search:
    st.markdown('<div class="section-header" style="margin-top:0;">Search Any Gene or Pathway</div>', unsafe_allow_html=True)
    st.caption(
        "Type an exact gene symbol (e.g. CLOCK, AANAT, MTNR1A, DIO2) for a full seasonal profile "
        "of ONLY that gene, or a pathway/parameter keyword (e.g. melatonin, photoperiod, seasonal "
        "reproduction, thyroid) to find every related gene. Results are limited to this database's "
        "defined photoperiod/seasonal-physiology scope — unrelated genes or pathways will return Not Found."
    )

    raw_query = st.text_input("Search", placeholder="e.g. CLOCK  •  DIO2  •  melatonin  •  photoperiod  •  seasonal reproduction",
                               label_visibility="collapsed")

    if raw_query.strip():
        matched_genes, matched_parameters, db_pathway_hit, matched_via_exact_gene = get_relevant_genes(raw_query, conn)
        refs_used = set()

        if not matched_genes and not matched_parameters:
            st.markdown(f"""
            <div class="xref-box" style="border-left-color:#b0453f;">
                <span class="xref-label" style="color:#b0453f;">❌ Not Found</span><br>
                <b>"{raw_query.strip()}"</b> is not related to any gene or pathway currently
                defined in this database's scope: <b>Photoperiod / Melatonin Pathway</b>,
                <b>Circadian Clock Core</b>, <b>Seasonal Reproduction (HPG axis)</b>, and the
                <b>Thyroid-Hormone Seasonal Switch</b> — or their curated genes.<br><br>
                This database intentionally does not return results for genes/pathways outside
                its defined seasonal-physiology scope, even if they exist in general databases
                like NCBI Gene. Try a term related to one of the pathways above, or:
                <ul>
                    <li>Double-check the gene symbol spelling</li>
                    <li>See the <b>Browse All Genes</b> tab for everything currently curated</li>
                    <li>Use the <b>Contribute Data</b> tab to add a gene/pathway to this database's scope</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Pathway/parameter description — ONLY shown for pathway/keyword
            # searches, never for an exact-gene search (fix: avoids showing
            # sibling gene names when someone searches one specific gene).
            if not matched_via_exact_gene:
                for pname, pdata in matched_parameters.items():
                    st.markdown(f'<div class="section-header">🧬 Pathway — {pname}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="xref-box">{pdata["description"]}</div>', unsafe_allow_html=True)

            gene_list = sorted(matched_genes)
            if matched_via_exact_gene:
                st.caption(f"Showing results for **{gene_list[0]}** only.")
            else:
                st.caption(f"{len(gene_list)} gene(s) matched within this database's defined scope.")

            # SAME unified card for every matched gene, regardless of which
            # layer (curated DB / seed library / DB pathway text) found it.
            # For an exact-gene search, gene_list has exactly one entry.
            for symbol in gene_list:
                render_gene_card(symbol, conn, raw_query.strip(), refs_used)

            # ── Visual summary across all matched genes ───────────
            # For an exact-gene search this naturally covers ONLY that one
            # gene (gene_list has a single symbol), so the SD/LD bar chart,
            # seasonal trend line, and heatmap below are all specific to
            # the gene that was searched.
            if len(gene_list) >= 1:
                st.markdown('<div class="section-header">📊 Seasonal & Photoperiod Visual Summary</div>', unsafe_allow_html=True)
                placeholders_v = ",".join(["%s"] * len(gene_list))
                try:
                    visual_df = pd.read_sql(
                        f"""SELECT g.gene_symbol, s.name AS season, gsf.fold_change, gsf.photoperiod_condition
                            FROM gene_seasonal_function gsf
                            JOIN genes g ON gsf.gene_id = g.id
                            JOIN seasons s ON gsf.season_id = s.id
                            WHERE g.gene_symbol IN ({placeholders_v})""",
                        conn, params=gene_list
                    )
                except Exception:
                    visual_df = pd.DataFrame()

                if not visual_df.empty:
                    visual_df['photoperiod_condition'] = visual_df.apply(
                        lambda r: r['photoperiod_condition'] if r['photoperiod_condition']
                        else SEASON_TO_PHOTOPERIOD.get(r['season'], 'INT'),
                        axis=1
                    )
                    season_order = [s for s in ['Winter', 'Spring', 'Summer', 'Autumn']
                                     if s in visual_df['season'].unique()]

                    photo_summary = (
                        visual_df[visual_df['photoperiod_condition'].isin(['SD', 'LD'])]
                        .groupby(['gene_symbol', 'photoperiod_condition'])['fold_change']
                        .mean()
                        .reset_index()
                    )
                    if not photo_summary.empty:
                        fig_photo = px.bar(
                            photo_summary, x='gene_symbol', y='fold_change',
                            color='photoperiod_condition', barmode='group',
                            color_discrete_map={'SD': '#22d3c8', 'LD': '#e8b93a'},
                            title=f'❄️ Short-Day vs ☀️ Long-Day Fold Change — "{raw_query.strip()}"',
                            labels={'gene_symbol': 'Gene', 'fold_change': 'Fold Change',
                                    'photoperiod_condition': 'Photoperiod'}
                        )
                        fig_photo.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#123c3a')
                        st.plotly_chart(fig_photo, use_container_width=True, key="photoperiod_comparison")
                    else:
                        st.caption("No SD/LD-labeled data yet for the matched gene(s) — this chart needs at least one curated row tagged SD or LD.")

                    season_trend = (
                        visual_df.groupby('season')['fold_change'].mean()
                        .reindex(season_order)
                        .reset_index()
                    )
                    if not season_trend.empty:
                        fig_trend = px.line(
                            season_trend, x='season', y='fold_change', markers=True,
                            title=f'Average Seasonal Fold-Change Trend — "{raw_query.strip()}"',
                            labels={'season': 'Season', 'fold_change': 'Avg. Fold Change'}
                        )
                        fig_trend.update_traces(line_color='#22d3c8', marker=dict(size=10, color='#e8b93a'))
                        fig_trend.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#123c3a')
                        st.plotly_chart(fig_trend, use_container_width=True, key="season_trend")

                    pivot = visual_df.pivot_table(index='gene_symbol', columns='season',
                                                   values='fold_change', aggfunc='mean')
                    pivot = pivot[[c for c in season_order if c in pivot.columns]]
                    fig_heat = px.imshow(
                        pivot, text_auto=".2f", aspect="auto",
                        color_continuous_scale="RdBu_r",
                        labels=dict(x="Season", y="Gene", color="Fold Change"),
                        title="Fold Change Heatmap — Gene × Season"
                    )
                    fig_heat.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#123c3a')
                    st.plotly_chart(fig_heat, use_container_width=True, key="heatmap_genes")
                else:
                    st.caption(f"No curated fold-change data yet for **{'/'.join(gene_list)}** — these charts need at least "
                               "one curated database row with a numeric fold-change value. Add one via the "
                               "**Contribute Data** tab (with admin approval) to unlock the graphs.")

            st.markdown('<div class="section-header">📚 References Used in This Result</div>', unsafe_allow_html=True)
            if refs_used:
                for ref in sorted(refs_used):
                    st.markdown(f"- {ref}")
            st.caption("Also see the full reference list and linked source databases in the sidebar.")

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
        symbols = symbols[:6]

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
                fig_cmp.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#123c3a')
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
        st.caption("Try comparing core clock genes, e.g. **CLOCK, PER2, BMAL1, CRY1**, "
                   "or melatonin-pathway genes, e.g. **AANAT, ASMT, MTNR1A, MTNR1B**.")

# ════════════════════════════════════════════════════════════════
# TAB 3 — CONTRIBUTE
# ════════════════════════════════════════════════════════════════
with tab_contribute:
    st.markdown('<div class="section-header">Add Your Own Curated Data</div>', unsafe_allow_html=True)
    st.caption(
        "Submissions go into a **moderation queue** and are reviewed by an admin before appearing "
        "publicly or in search results (see the Admin tab). A real, checkable source is required — "
        "a PMID (e.g. 21781060), a DOI (e.g. 10.1038/nature06738), or a GEO accession "
        "(e.g. GSE123456). Plain URLs are not accepted, since links break and can't be verified later."
    )

    with st.form("contribute_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            f_gene = st.text_input("Gene Symbol *", placeholder="e.g. PER2")
            f_condition = st.selectbox("Season / Photoperiod Condition *",
                ["Winter (SD)", "Spring (Intermediate)", "Summer (LD)", "Autumn (Intermediate)",
                 "SD (Short-Day, general)", "LD (Long-Day, general)"])
            f_expression = st.selectbox("Expression Level *", ["HIGH", "NORMAL", "LOW"])
            f_fold = st.number_input("Fold Change", min_value=0.0, max_value=20.0, value=1.0, step=0.1)
            f_evidence = st.selectbox("Evidence Level *", EVIDENCE_LEVELS)
        with c2:
            f_pathway = st.text_input("Pathway", placeholder="e.g. Melatonin Synthesis, Circadian Rhythm")
            f_tissue = st.text_input("Tissue Type", placeholder="e.g. Liver, SCN, Pineal Gland")
            f_source_db = st.selectbox("Source Database *",
                ["NCBI", "CircaDB", "PubMed", "GEO Datasets", "UniProt", "Gene Ontology", "Other"])
            f_source_ref = st.text_input("Source Reference * (PMID / DOI / GEO accession)",
                                          placeholder="e.g. 21781060  or  10.1038/nature06738  or  GSE123456")

        st.markdown("**Statistical detail (optional but strongly encouraged)**")
        s1, s2, s3 = st.columns(3)
        with s1:
            f_pvalue = st.number_input("p-value", min_value=0.0, max_value=1.0, value=None,
                                        step=0.001, format="%.4f", placeholder="e.g. 0.032")
        with s2:
            f_n = st.number_input("Sample size (n)", min_value=0, value=None, step=1, placeholder="e.g. 12")
        with s3:
            ci_col1, ci_col2 = st.columns(2)
            f_ci_lower = ci_col1.number_input("95% CI lower", value=None, step=0.1, format="%.2f")
            f_ci_upper = ci_col2.number_input("95% CI upper", value=None, step=0.1, format="%.2f")

        f_role = st.text_area("Functional Role / Notes", placeholder="Describe the gene's seasonal/photoperiod role...")
        f_contributor = st.text_input("Your Name (optional)", placeholder="Anonymous if left blank")

        submitted = st.form_submit_button("Submit for Review")

        if submitted:
            if not f_gene or not f_source_ref:
                st.error("Gene Symbol and Source Reference are required.")
            elif not is_valid_source_reference(f_source_ref):
                st.error(
                    "Source Reference must be a PMID (digits only, optionally prefixed 'PMID'), "
                    "a DOI (starting with '10.'), or a GEO accession (GSE/GSM/GDS + digits). "
                    "Plain URLs aren't accepted — please find the underlying PMID/DOI/accession."
                )
            else:
                symbol_clean = f_gene.upper().strip()
                hgnc_info = fetch_hgnc_info(symbol_clean)
                ins_cursor = conn.cursor()
                ins_cursor.execute("""
                    INSERT INTO community_contributions
                    (gene_symbol, season_or_condition, expression_level, fold_change,
                     functional_role, pathway, tissue_type, source_db, source_reference,
                     contributor_name, status, p_value, sample_size, ci_lower, ci_upper,
                     evidence_level, hgnc_id, ensembl_id, uniprot_id)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'pending',%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    symbol_clean, f_condition, f_expression, f_fold,
                    f_role, f_pathway, f_tissue, f_source_db, f_source_ref.strip(),
                    f_contributor if f_contributor else "Anonymous",
                    f_pvalue, f_n, f_ci_lower, f_ci_upper, f_evidence,
                    hgnc_info["hgnc_id"] if hgnc_info else None,
                    hgnc_info["ensembl_id"] if hgnc_info else None,
                    hgnc_info["uniprot_id"] if hgnc_info else None,
                ))
                conn.commit()
                if hgnc_info:
                    st.success(
                        f"Thank you. Your submission for {symbol_clean} (HGNC-validated: {hgnc_info['hgnc_id']}) "
                        f"is now in the moderation queue and will appear publicly once an admin approves it."
                    )
                else:
                    st.warning(
                        f"Submitted for {symbol_clean}, but this symbol could not be validated against HGNC "
                        f"(it may be non-human, an unofficial alias, or a typo). It has been queued for review; "
                        f"an admin can still approve it manually if the symbol is correct."
                    )

    st.markdown('<div class="section-header">Recent Community Submissions</div>', unsafe_allow_html=True)
    recent_query = """
        SELECT gene_symbol AS "Gene", season_or_condition AS "Condition",
               expression_level AS "Expression", evidence_level AS "Evidence Level",
               status AS "Status", source_db AS "Source",
               contributor_name AS "Contributor", submitted_at AS "Submitted"
        FROM community_contributions
        ORDER BY submitted_at DESC
        LIMIT 15
    """
    recent_df = pd.read_sql(recent_query, conn)
    if not recent_df.empty:
        recent_df["Status"] = recent_df["Status"].map(lambda s: CONTRIBUTION_STATUS_LABELS.get(s, s))
        st.dataframe(recent_df, use_container_width=True)
        st.caption("Only 'Approved' submissions appear in the Universal Search results and gene cards.")
    else:
        st.caption("No community submissions yet.")

# ════════════════════════════════════════════════════════════════
# TAB 4 — BROWSE
# ════════════════════════════════════════════════════════════════
with tab_browse:
    st.markdown('<div class="section-header">Browse & Filter All Genes</div>', unsafe_allow_html=True)

    fcol1, fcol2 = st.columns([1, 2])
    with fcol1:
        category_filter = st.selectbox("Filter by category",
            ["All", "Circadian", "Hormonal", "Immune", "Metabolic", "Mood/Brain", "Other"])
    with fcol2:
        pathway_filter = st.text_input("Filter by pathway/functional-role keyword (optional)",
                                        placeholder="e.g. melatonin, photoperiod, thyroid")

    all_query = "SELECT gene_symbol AS Symbol, full_name AS \"Full Name\", category AS Category, chromosome AS Chromosome, organism AS Organism FROM genes ORDER BY gene_symbol"
    all_genes = pd.read_sql(all_query, conn)
    if category_filter != "All":
        all_genes = all_genes[all_genes['Category'] == category_filter]

    if pathway_filter.strip():
        kw_query = """
            SELECT DISTINCT g.gene_symbol
            FROM gene_seasonal_function gsf
            JOIN genes g ON gsf.gene_id = g.id
            WHERE gsf.pathway LIKE %s OR gsf.functional_role LIKE %s
        """
        like = f"%{pathway_filter.strip()}%"
        kw_matches = pd.read_sql(kw_query, conn, params=[like, like])
        matching_symbols = set(kw_matches['gene_symbol']) if not kw_matches.empty else set()
        all_genes = all_genes[all_genes['Symbol'].isin(matching_symbols)]

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
    hormonal, immune, metabolic, or mood/brain physiology. Its defined pathway
    scope is: **Photoperiod / Melatonin Pathway**, **Circadian Clock Core**,
    **Seasonal Reproduction (HPG axis)**, and the **Thyroid-Hormone Seasonal
    Switch** — plus any gene/pathway curated into the SQL tables under this
    scope. Searches outside this scope are reported as **Not Found**, even if
    a general resource like NCBI Gene or Gene Ontology has an entry for the
    term — see point 6 below.

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

    **5. Live cross-referencing (enrichment, not a discovery mechanism)**
    Once a gene has been confirmed relevant to this database's defined scope
    (via the curated DB or the literature seed library), its entry is enriched
    with a live NCBI Gene lookup (via NCBI E-utilities, for official nomenclature
    and gene summary) and a live PubMed search (for photoperiod/seasonal/circadian
    literature). These live calls never introduce a gene into a result on their
    own — they only add detail to genes already judged in-scope.

    **6. Universal search behavior — unified, scope-gated, single-gene-safe results**
    The single Search box accepts either an exact gene symbol or a pathway/
    parameter keyword (e.g. "melatonin", "photoperiod", "seasonal reproduction").
    A query is first checked against this database's defined scope: (a) exact
    gene symbols already curated in the database, (b) exact gene symbols in the
    literature seed library, (c) pathway/parameter names or keywords from the
    seed library, and (d) this database's own curated pathway/functional-role
    text. **A query is only treated as "found" if at least one of these matches.**
    If the query resolves to an **exact gene symbol** (e.g. "DIO2"), results are
    scoped to that gene alone — no sibling genes from the same pathway are pulled
    in, and the pathway-wide description is suppressed, so search, cards, and every
    chart (season/photoperiod bar chart, SD-vs-LD comparison, seasonal trend line,
    heatmap) all reflect only the gene that was searched. Only a **pathway/keyword**
    search (e.g. "melatonin") intentionally pulls in every gene belonging to that
    pathway. If none of the four checks match, the app reports a clean
    **"Not Found"**, explicitly naming the database's defined pathway scope, rather
    than falling back to an unrelated live NCBI/GO hit for the raw search term.

    **7. Community contributions**
    Data submitted via the Contribute tab is published immediately and is
    **not independently verified** by the project author before appearing
    publicly. It is visually and structurally separated from author-curated
    entries throughout the app. Users citing this tool for research purposes
    should verify community-submitted rows against the original source listed.

    **8. Limitations**
    - Organism is not uniformly controlled for across all entries; check the
      "Organism" field in Browse All Genes where relevant.
    - Tissue type varies by study and is not normalized.
    - Live NCBI/PubMed enrichment defaults to human data; results for other
      organisms may require adapting the lookup functions.
    - This is a curation and cross-referencing tool, not a primary data source —
      always confirm critical values against the cited original publication or
      database record before use in a manuscript.
    - A gene with no curated numeric row in the SQL database (only a literature
      role in the seed library) will not have a fold-change graph until such
      data is contributed and approved.

    **9. Identifier validation (HGNC)**
    Every gene symbol shown in a result card is checked against the official
    **HGNC** registry (rest.genenames.org) and, where matched, displayed with
    its stable **HGNC ID**, **Ensembl Gene ID**, and **UniProt accession** —
    so entries are traceable by ID, not just by a free-text symbol that could
    be an outdated alias or a typo. A "⚠ Not HGNC-validated" badge appears
    where no match was found (common for non-human symbols or aliases);
    this is a caution flag, not proof the gene doesn't exist.

    **10. Statistical rigor**
    Curated rows may carry a **p-value**, **sample size (n)**, and **95%
    confidence interval** alongside the expression call and fold change.
    Where these are absent, the table shows this explicitly rather than
    implying a value that wasn't reported in the source. Fold-change alone,
    without a reported p-value, should be treated as descriptive rather
    than as evidence of statistical significance.

    **11. Evidence grading**
    Each curated row is tagged with one of four evidence tiers: **Direct
    experimental (this study)**, **Inferred (homolog/ortholog)**,
    **Predicted/computational**, or **Literature-established (secondary
    review)** — the last covering the textbook-level seed gene sets in
    the Photoperiod/Melatonin, Circadian Clock, Seasonal Reproduction, and
    Thyroid-Switch pathways. This distinguishes primary experimental
    findings from literature synthesis and computational prediction.

    **12. Community contribution moderation**
    Submissions via the Contribute tab now enter a **pending-review queue**
    and are only shown in search results or gene cards after an admin
    approves them in the Admin tab. Submitted source references must be a
    verifiable **PMID, DOI, or GEO accession** — plain URLs are rejected —
    and the gene symbol is checked against HGNC at submission time.

    **13. Dataset versioning & citation**
    The database carries an explicit **version label** and **last-updated
    timestamp** (shown in the sidebar), optionally linked to a **DOI**
    (e.g. via Zenodo) once the project author registers one. A ready-made
    **BibTeX citation** is available in the sidebar for anyone citing this
    tool in a manuscript.
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
    st.markdown('<div class="section-header">🔐 Admin Panel — Moderation, Versioning & Import</div>', unsafe_allow_html=True)

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

        st.success("Authenticated. You can moderate contributions, manage versioning, or bulk import below.")

        # ── Moderation queue ───────────────────────────────────
        st.markdown('<div class="section-header">🗂 Review Pending Community Contributions</div>', unsafe_allow_html=True)
        pending_df = pd.read_sql(
            """SELECT id, gene_symbol, season_or_condition, expression_level, fold_change,
                      evidence_level, p_value, sample_size, source_db, source_reference,
                      hgnc_id, functional_role, contributor_name, submitted_at
               FROM community_contributions
               WHERE status = 'pending'
               ORDER BY submitted_at ASC""",
            conn
        )
        if pending_df.empty:
            st.caption("No pending submissions — moderation queue is empty.")
        else:
            st.caption(f"{len(pending_df)} submission(s) awaiting review.")
            for _, row in pending_df.iterrows():
                with st.expander(f"{row['gene_symbol']} — {row['season_or_condition']} — submitted by {row['contributor_name']}"):
                    hgnc_line = f"HGNC-validated ({row['hgnc_id']})" if pd.notna(row['hgnc_id']) and row['hgnc_id'] else "⚠ Not HGNC-validated"
                    st.markdown(f"""
                    - **Expression:** {row['expression_level']} ({row['fold_change']}x)
                    - **Evidence level:** {row['evidence_level'] or 'Not specified'}
                    - **Stats:** p={row['p_value']}, n={row['sample_size']}
                    - **Source:** {row['source_db']} — {row['source_reference']}
                    - **Symbol check:** {hgnc_line}
                    - **Notes:** {row['functional_role'] or '—'}
                    """)
                    admin_name = st.text_input("Reviewer name", value="Admin", key=f"reviewer_{row['id']}")
                    bcol1, bcol2 = st.columns(2)
                    if bcol1.button("✅ Approve", key=f"approve_{row['id']}"):
                        rc = conn.cursor()
                        rc.execute(
                            "UPDATE community_contributions SET status='approved', reviewed_by=%s, reviewed_at=NOW() WHERE id=%s",
                            (admin_name, int(row['id']))
                        )
                        conn.commit()
                        st.rerun()
                    if bcol2.button("❌ Reject", key=f"reject_{row['id']}"):
                        rc = conn.cursor()
                        rc.execute(
                            "UPDATE community_contributions SET status='rejected', reviewed_by=%s, reviewed_at=NOW() WHERE id=%s",
                            (admin_name, int(row['id']))
                        )
                        conn.commit()
                        st.rerun()

        # ── Dataset versioning & citation ───────────────────────
        st.markdown('<div class="section-header">🏷 Dataset Versioning & Citation</div>', unsafe_allow_html=True)
        current_meta = get_dataset_meta(conn)
        vcol1, vcol2 = st.columns(2)
        with vcol1:
            new_version = st.text_input("Version label", value=current_meta.get("version") or "v1.0")
            new_doi = st.text_input("DOI (optional, e.g. from Zenodo)", value=current_meta.get("doi") or "")
        with vcol2:
            new_notes = st.text_area("Release notes", value=current_meta.get("notes") or "", height=100)
        if st.button("Save version info"):
            vc = conn.cursor()
            vc.execute(
                "UPDATE dataset_meta SET version=%s, doi=%s, notes=%s, last_updated=NOW() WHERE id=1",
                (new_version.strip(), new_doi.strip() or None, new_notes.strip() or None)
            )
            conn.commit()
            get_dataset_meta.clear()
            st.success("Dataset version info updated.")
            st.rerun()

        st.markdown('<div class="section-header">Bulk Import Genes from CSV</div>', unsafe_allow_html=True)
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
        batch_pathway = st.text_input(
            "Pathway label for this batch (optional, improves keyword search matching)",
            placeholder="e.g. Melatonin Synthesis, Photoperiod Response"
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
                            time.sleep(0.4)

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
                                    batch_pathway or "Imported dataset",
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
st.caption("Data sources: NCBI Gene · CircaDB · GEO Datasets · UniProt · Gene Ontology · PubMed · Community contributions")
st.caption("This is an open, publicly editable research database. Data accuracy of community contributions is not independently verified.")
st.caption("📚 Full reference list available in the sidebar. Suggested citation: Your Name (2026). "
           "*Seasonal Physiology Gene Database*. "
           "seasonal-gene-db-wb4nzf4rwezxmhzrtrcimr.streamlit.app")
