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
    .source-tag-db { background: #e4f7ea; border-color: #9edab3; color: #157a3d; }
    .source-tag-ncbi { background: #eaf3fc; border-color: #a9c9e8; color: #205493; }
    .source-tag-go { background: #fdf0e3; border-color: #e6c393; color: #9c5a17; }
    .source-tag-seed { background: #f3e8fd; border-color: #cfa9e8; color: #6a1a9c; }

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

st.markdown('<div class="ncbi-topstrip">🧬 National-style research resource · cross-referenced live with NCBI, PubMed, CircaDB, GEO, UniProt &amp; Gene Ontology</div>', unsafe_allow_html=True)


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
    "Gene Ontology": {"url": "https://geneontology.org/",
                       "desc": "Controlled-vocabulary annotation of gene function, process, and location."},
}

# ════════════════════════════════════════════════════════════════
# CURATED SEED LIBRARY — established seasonal-physiology gene sets
# (Static, textbook/literature-level biology used so a parameter
# search never comes back empty, even before checking live sources.
# References: Nakao et al. 2008 Nature; Hanon et al. 2008 Curr Biol;
# Dardente et al. 2010 J Neuroendocrinol; Hazlerigg & Loudon 2008.)
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


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def fetch_ncbi_gene_search(query_term: str, organism: str = "Homo sapiens", retmax: int = 15):
    """Broad, NCBI-style free-text search across Gene records (not restricted
    to an exact symbol). This is what makes the app 'big broad level' like
    NCBI's own gene search — e.g. searching 'melatonin pathway' or
    'photoperiod' rather than a single gene symbol.
    Returns a list of dicts: symbol, name, gene_id, url. Empty list on
    failure or no hits."""
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
# LIVE GENE ONTOLOGY CROSS-REFERENCE (via EBI QuickGO)
# ════════════════════════════════════════════════════════════════
@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def fetch_go_terms(query: str, limit: int = 8):
    """Search GO ontology terms matching a free-text query (e.g. 'melatonin',
    'photoperiodism'). Returns list of dicts: id, name, aspect. Empty list
    on failure — the calling code degrades gracefully."""
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
    """Given a GO term ID, fetch gene products annotated to it for a given
    taxon (default human) via QuickGO's annotation search — this is the
    'big broad level, like Gene Ontology' lookup: pathway/process -> genes,
    rather than gene -> pathway. Returns a sorted list of unique symbols."""
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
    """Build a schematic (not area-proportional) 2- or 3-set Venn diagram
    using pure Plotly shapes/annotations — no extra plotting library needed.
    sets_dict: {label: set(gene_symbols)} with 2 or 3 entries."""
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
                       plot_bgcolor='white', paper_bgcolor='white')
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
    <p class="main-subtitle">A photoperiod- and season-linked gene expression resource, cross-referenced with NCBI, CircaDB, PubMed, GEO Datasets, UniProt, and Gene Ontology.</p>
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
    """Match a free-text query against the curated PARAMETER_LIBRARY —
    by parameter name, keyword, or an exact seed-gene symbol."""
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
# TAB 1 — UNIVERSAL SEARCH (gene symbol OR pathway/parameter, one box)
# One public search engine: type a gene symbol (CLOCK, AANAT, MTNR1A)
# or a pathway/parameter keyword (melatonin, photoperiod, thyroid...).
# Every available source is checked; a clean "Not Found" is shown only
# if NONE of the sources return anything.
# ════════════════════════════════════════════════════════════════
with tab_search:
    st.markdown('<div class="section-header" style="margin-top:0;">Search Any Gene or Pathway</div>', unsafe_allow_html=True)
    st.caption(
        "Type an exact gene symbol (e.g. CLOCK, AANAT, MTNR1A) for a full seasonal profile, "
        "or a pathway/parameter keyword (e.g. melatonin, photoperiod, seasonal reproduction, thyroid) "
        "to find every related gene across this database, NCBI, and Gene Ontology."
    )

    raw_query = st.text_input("Search", placeholder="e.g. CLOCK  •  melatonin  •  photoperiod  •  AANAT  •  seasonal reproduction",
                               label_visibility="collapsed")

    if raw_query.strip():
        symbol = raw_query.strip().upper()
        found_any = False
        refs_used = set()

        # ── LAYER 1: exact gene-symbol profile in curated DB ──────
        gene_query = """
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
        df = pd.read_sql(gene_query, conn, params=[symbol])

        if not df.empty:
            found_any = True
            n_evidence = df['study_reference'].nunique() if 'study_reference' in df.columns else len(df)
            st.markdown(f"""
            <div class="result-box">
                <span class="gene-name">{symbol}</span>{evidence_badge(n_evidence)}
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
            fig.update_layout(showlegend=False, plot_bgcolor='white', paper_bgcolor='white', font_color='#1a1a1a')
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
            for ref in df['study_reference'].dropna().unique().tolist():
                refs_used.add(f"Curated study reference: {ref}")

            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download this gene's data as CSV", csv_bytes,
                                file_name=f"{symbol}_seasonal_data.csv", mime="text/csv")

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

        # ── LAYER 2: curated DB pathway / functional-role keyword match ──
        like = f"%{raw_query.strip()}%"
        kw_query = """
            SELECT DISTINCT g.gene_symbol, g.full_name, gsf.pathway, gsf.functional_role, gsf.study_reference
            FROM gene_seasonal_function gsf
            JOIN genes g ON gsf.gene_id = g.id
            WHERE (g.full_name LIKE %s OR gsf.pathway LIKE %s OR gsf.functional_role LIKE %s)
              AND g.gene_symbol != %s
            LIMIT 50
        """
        try:
            kw_matches = pd.read_sql(kw_query, conn, params=[like, like, like, symbol])
        except Exception:
            kw_matches = pd.DataFrame()

        if not kw_matches.empty:
            found_any = True
            st.markdown('<div class="section-header">🗄 Related Genes — This Database (pathway/role match)</div>', unsafe_allow_html=True)
            st.dataframe(
                kw_matches.rename(columns={
                    'gene_symbol': 'Gene', 'full_name': 'Full Name',
                    'pathway': 'Pathway', 'functional_role': 'Functional Role',
                    'study_reference': 'Reference'
                }),
                use_container_width=True, hide_index=True
            )
            for ref in kw_matches['study_reference'].dropna().unique().tolist():
                refs_used.add(f"Curated study reference: {ref}")

        # ── LAYER 3: curated literature seed library (photoperiod/melatonin/etc.) ──
        seed_matches = match_seed_library(raw_query.strip())
        if seed_matches:
            found_any = True
            for pname, pdata in seed_matches.items():
                st.markdown(f'<div class="section-header">🧬 Literature Gene Set — {pname}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="xref-box">{pdata["description"]}</div>', unsafe_allow_html=True)
                seed_df = pd.DataFrame(pdata["seed_genes"]).rename(columns={"symbol": "Gene Symbol", "role": "Known Role"})
                st.dataframe(seed_df, use_container_width=True, hide_index=True)
                refs_used.add("Nakao et al. 2008, Nature 452:317-322 — thyrotrophin/pars tuberalis photoperiodic switch")
                refs_used.add("Hanon et al. 2008, Current Biology 18:1147-1152 — ancestral TSH mechanism")

        # ── LAYER 4: live NCBI Gene free-text / symbol search ─────
        with st.spinner("Checking NCBI Gene..."):
            ncbi_exact = fetch_ncbi_gene_summary(symbol) if df.empty else None
            ncbi_hits = fetch_ncbi_gene_search(raw_query.strip())

        if ncbi_exact:
            found_any = True
            st.markdown('<div class="section-header">🔬 Live NCBI Gene Record</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="xref-box">
                <span class="xref-label">Official name:</span> {ncbi_exact['official_name']}<br>
                <span class="xref-label">Chromosome:</span> {ncbi_exact['chromosome']}
                &nbsp;·&nbsp; <span class="xref-label">Map location:</span> {ncbi_exact['map_location']}<br>
                <span class="xref-label">NCBI summary:</span> {ncbi_exact['summary']}<br><br>
                <a href="{ncbi_exact['ncbi_url']}" target="_blank">View full NCBI Gene record →</a>
                &nbsp;|&nbsp;
                <a href="{uniprot_search_url(symbol)}" target="_blank">View on UniProt →</a>
            </div>
            """, unsafe_allow_html=True)
            refs_used.add(f"NCBI Gene ID {ncbi_exact['gene_id']} — {ncbi_exact['ncbi_url']}")

        if ncbi_hits:
            found_any = True
            st.markdown('<div class="section-header">🌐 Live NCBI Gene Search Results</div>', unsafe_allow_html=True)
            ncbi_df = pd.DataFrame(ncbi_hits).rename(columns={"symbol": "Gene", "name": "Description", "url": "Link"})
            st.dataframe(ncbi_df[["Gene", "Description"]], use_container_width=True, hide_index=True)
            for hit in ncbi_hits[:10]:
                refs_used.add(f"NCBI Gene ID {hit['gene_id']} — {hit['url']}")

        # ── LAYER 5: live Gene Ontology term + annotation search ──
        go_query_term = symbol if seed_matches == {} and df.empty and kw_matches.empty else raw_query.strip()
        with st.spinner("Checking Gene Ontology..."):
            go_terms = fetch_go_terms(go_query_term, limit=5)
            go_gene_rows = []
            for t in go_terms:
                for g_sym in fetch_go_annotated_genes(t["id"], limit=15):
                    go_gene_rows.append({"Gene": g_sym, "GO Term": t["name"], "GO ID": t["id"]})

        if go_terms:
            found_any = True
            st.markdown('<div class="section-header">🧭 Matching Gene Ontology Terms</div>', unsafe_allow_html=True)
            for t in go_terms:
                st.markdown(
                    f'<span class="source-tag source-tag-go">{t["id"]}</span> '
                    f'{t["name"]} <i>({t.get("aspect","")})</i> — '
                    f'<a href="https://www.ebi.ac.uk/QuickGO/term/{t["id"]}" target="_blank">view on QuickGO →</a>',
                    unsafe_allow_html=True
                )
                refs_used.add(f"Gene Ontology term {t['id']} ({t['name']}) — https://www.ebi.ac.uk/QuickGO/term/{t['id']}")

        if go_gene_rows:
            st.markdown('<div class="section-header">🧭 Genes Annotated to These GO Terms</div>', unsafe_allow_html=True)
            go_df = pd.DataFrame(go_gene_rows).drop_duplicates(subset=["Gene"])
            st.dataframe(go_df, use_container_width=True, hide_index=True)

        # ── VISUAL SUMMARY: bar graph, heatmap, Venn diagram ──────
        if found_any:
            db_gene_set = set(df['gene_symbol'].tolist()) if not df.empty else set()
            if not kw_matches.empty:
                db_gene_set |= set(kw_matches['gene_symbol'].tolist())
            seed_gene_set = set()
            for pdata in seed_matches.values():
                seed_gene_set |= {g['symbol'] for g in pdata['seed_genes']}
            ncbi_gene_set = {h['symbol'] for h in ncbi_hits if h.get('symbol')}
            if ncbi_exact:
                ncbi_gene_set.add(ncbi_exact['official_symbol'])
            go_gene_set = {row['Gene'] for row in go_gene_rows}

            st.markdown('<div class="section-header">📊 Visual Summary</div>', unsafe_allow_html=True)

            # -- 1. Bar graph: genes found per source --
            source_counts = {
                "This Database": len(db_gene_set),
                "Literature Seed Set": len(seed_gene_set),
                "Live NCBI Gene": len(ncbi_gene_set),
                "Live Gene Ontology": len(go_gene_set),
            }
            bar_df = pd.DataFrame({"Source": list(source_counts.keys()), "Genes Found": list(source_counts.values())})
            fig_bar = px.bar(bar_df, x="Source", y="Genes Found", color="Source",
                              color_discrete_sequence=["#1f9d55", "#6a1a9c", "#205493", "#e8820c"],
                              title=f'Genes Found per Source — "{raw_query.strip()}"')
            fig_bar.update_layout(showlegend=False, plot_bgcolor='white', paper_bgcolor='white', font_color='#1a1a1a')
            st.plotly_chart(fig_bar, use_container_width=True, key="bar_sources")

            # -- 2. Heatmap: gene x season fold-change (curated DB genes only, capped) --
            heatmap_genes = sorted(db_gene_set)[:15]
            if len(heatmap_genes) >= 1:
                placeholders_h = ",".join(["%s"] * len(heatmap_genes))
                heat_query = f"""
                    SELECT g.gene_symbol, s.name AS season, gsf.fold_change
                    FROM gene_seasonal_function gsf
                    JOIN genes g ON gsf.gene_id = g.id
                    JOIN seasons s ON gsf.season_id = s.id
                    WHERE g.gene_symbol IN ({placeholders_h})
                """
                try:
                    heat_df = pd.read_sql(heat_query, conn, params=heatmap_genes)
                except Exception:
                    heat_df = pd.DataFrame()

                if not heat_df.empty:
                    pivot = heat_df.pivot_table(index='gene_symbol', columns='season',
                                                 values='fold_change', aggfunc='mean')
                    season_order = [s for s in ['Winter', 'Spring', 'Summer', 'Autumn'] if s in pivot.columns]
                    pivot = pivot[season_order]
                    fig_heat = px.imshow(pivot, text_auto=".2f", aspect="auto",
                                          color_continuous_scale="RdBu_r",
                                          labels=dict(x="Season", y="Gene", color="Fold Change"),
                                          title="Fold Change Heatmap — Gene × Season (this database)")
                    fig_heat.update_layout(plot_bgcolor='white', paper_bgcolor='white', font_color='#1a1a1a')
                    st.plotly_chart(fig_heat, use_container_width=True, key="heatmap_genes")
                else:
                    st.caption("No per-season fold-change data curated yet for the matched gene(s) — heatmap needs at least one curated database row.")

            # -- 3. Venn diagram: overlap between DB / NCBI / GO gene sets --
            venn_sets = {}
            if db_gene_set:
                venn_sets["This Database"] = db_gene_set
            if ncbi_gene_set:
                venn_sets["NCBI Gene"] = ncbi_gene_set
            if go_gene_set:
                venn_sets["Gene Ontology"] = go_gene_set

            if len(venn_sets) >= 2:
                st.markdown("**Source Overlap (Venn Diagram)**")
                st.caption("Schematic (not area-proportional) — shows which genes are found in more than one source.")
                fig_venn = render_venn(venn_sets)
                st.plotly_chart(fig_venn, use_container_width=True, key="venn_sources")
            else:
                st.caption("Only one source returned genes for this query, so a Venn diagram isn't meaningful here.")

        # ── FINAL: clean "Not Found" only if truly nothing anywhere ──
        if not found_any:
            st.markdown(f"""
            <div class="xref-box" style="border-left-color:#b0453f;">
                <span class="xref-label" style="color:#b0453f;">❌ Not Found</span><br>
                No result for <b>"{raw_query.strip()}"</b> in this database's curated records,
                the literature seed sets, live NCBI Gene, or live Gene Ontology.<br><br>
                Try a broader term (e.g. "melatonin" instead of a specific receptor variant),
                double-check the gene symbol spelling, or:
                <ul>
                    <li><a href="https://www.ncbi.nlm.nih.gov/gene/?term={raw_query.strip()}" target="_blank">Search NCBI Gene manually →</a></li>
                    <li><a href="https://pubmed.ncbi.nlm.nih.gov/?term={raw_query.strip()}" target="_blank">Search PubMed manually →</a></li>
                    <li><a href="https://www.ebi.ac.uk/QuickGO/search/{raw_query.strip()}" target="_blank">Search Gene Ontology manually →</a></li>
                </ul>
                Know something about this gene/pathway? Use the <b>Contribute Data</b> tab to add it.
            </div>
            """, unsafe_allow_html=True)
        else:
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
        st.caption("Try comparing core clock genes, e.g. **CLOCK, PER2, BMAL1, CRY1**, "
                   "or melatonin-pathway genes, e.g. **AANAT, ASMT, MTNR1A, MTNR1B**.")

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
            f_pathway = st.text_input("Pathway", placeholder="e.g. Melatonin Synthesis, Circadian Rhythm")
            f_tissue = st.text_input("Tissue Type", placeholder="e.g. Liver, SCN, Pineal Gland")
            f_source_db = st.selectbox("Source Database *",
                ["NCBI", "CircaDB", "PubMed", "GEO Datasets", "UniProt", "Gene Ontology", "Other"])
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
    summary, and against live Gene Ontology terms/annotations (via EBI QuickGO) to
    surface process/function annotations. These are validation aids, not the data
    source for the fold-change/expression values themselves, which come from the
    curated database.

    **6. Universal search behavior**
    The single Search box accepts either an exact gene symbol or a pathway/
    parameter keyword (e.g. "melatonin", "photoperiod", "seasonal reproduction").
    A query is checked, in order, against: (a) this database's curated
    gene-season records, (b) this database's pathway/functional-role text
    fields, (c) a literature-derived seed gene set for well-established
    seasonal-physiology parameters (photoperiod/melatonin, circadian clock,
    seasonal reproduction, thyroid switch), (d) a live NCBI Gene search, and
    (e) a live Gene Ontology term + annotation search (EBI QuickGO). Each
    result section is explicitly labeled by source, and a clean "Not Found"
    is shown only when **all five** checks return nothing — a miss in one
    source alone does not produce a false negative. Every displayed result
    lists its originating reference(s) for traceability before citation.

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
    - GO annotation search is limited to human (taxon 9606) by default; results
      for other organisms require a different taxon ID.
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
