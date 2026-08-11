# 🧬 Seasonal Physiology Gene Database

A curated, **HGNC-validated**, statistically-graded research database of genes
involved in **photoperiod perception, melatonin signaling, the circadian
clock, seasonal reproduction, and the thyroid-hormone seasonal switch** —
cross-referenced live with **NCBI Gene, PubMed, CircaDB, GEO Datasets,
UniProt, and Gene Ontology**.

**🔗 Live app:** https://seasonal-gene-db-wb4nzf4rwezxmhzrtrcimr.streamlit.app/

Built for students and researchers working in chronobiology, seasonal
physiology, and comparative endocrinology who need a single, citable,
scope-limited resource instead of hunting across five different databases.

---

## ✨ Features

- **🔍 Universal search** — one search box for gene symbols *or* pathway
  keywords (e.g. `CLOCK`, `melatonin`, `photoperiod`, `seasonal reproduction`).
  Results are strictly limited to this database's defined scope — searches
  outside that scope return a clean **"Not Found"** instead of unrelated
  noise from general databases.
- **🧾 Unified result template** — every matched gene is rendered with the
  same fixed structure (identity → known role → season/photoperiod
  comparison → statistics → live cross-references), regardless of which
  internal layer matched it.
- **🆔 HGNC / Ensembl / UniProt identifier validation** — gene symbols are
  checked against the official HGNC registry and resolved to stable IDs,
  not just matched by free-text symbol.
- **📊 Statistical rigor** — p-values, sample sizes, and 95% confidence
  intervals are tracked per curated data row, alongside a 4-tier
  **evidence grading** system (direct experimental / inferred / predicted /
  literature-established).
- **🌍 Moderated community contributions** — public submissions enter a
  review queue and require a verifiable PMID/DOI/GEO accession; nothing
  appears in search results until an admin approves it.
- **📈 Interactive visualizations** — season/photoperiod comparison charts,
  fold-change heatmaps, and multi-gene comparison tools (Plotly).
- **🏷️ Dataset versioning & citation** — version-labeled releases with an
  optional DOI (e.g. via Zenodo) and a ready-to-use BibTeX export.
- **🔗 Live cross-referencing** — confirmed in-scope genes are enriched with
  live NCBI Gene summaries and PubMed literature search results.

---

## 📖 Scope

This database is intentionally **not** a general-purpose gene database. It
covers four defined pathways:

| Pathway | Description |
|---|---|
| **Photoperiod / Melatonin Pathway** | Retina → SCN → pineal gland melatonin signaling that encodes night length |
| **Circadian Clock Core** | The core TTFL (CLOCK/BMAL1/PER/CRY) driving ~24h rhythms |
| **Seasonal Reproduction (HPG axis)** | Kisspeptin/GnRH circuitry gating breeding season |
| **Thyroid-Hormone Seasonal Switch** | Pars tuberalis TSH–deiodinase loop converting melatonin duration into a long-day/short-day physiological state |

Queries outside this scope are reported as **Not Found** by design — see the
in-app **Methodology** tab for full details on evidence grading, statistical
handling, and search logic.

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/) — app framework
- MySQL — curated data storage
- [Plotly](https://plotly.com/python/) — interactive charts
- NCBI E-utilities, EBI QuickGO, HGNC REST API — live data cross-referencing

---

## 🚀 Running Locally

```bash
git clone https://github.com/<your-username>/seasonal-gene-db.git
cd seasonal-gene-db
pip install -r requirements.txt
```

Create `.streamlit/secrets.toml` with your database credentials:

```toml
DB_HOST = "your-mysql-host"
DB_USER = "your-mysql-user"
DB_PASSWORD = "your-mysql-password"
DB_NAME = "your-database-name"
DB_PORT = "3306"
ADMIN_PASSWORD = "choose-an-admin-password"
```

Then run:

```bash
streamlit run app.py
```

The app auto-creates/migrates the required tables (`genes`,
`gene_seasonal_function`, `seasons`, `community_contributions`,
`dataset_meta`) on first launch.

---

## 🗂️ Database Schema (overview)

- **`genes`** — gene identity: symbol, full name, category, HGNC/Ensembl/UniProt IDs
- **`seasons`** — Winter / Spring / Summer / Autumn
- **`gene_seasonal_function`** — expression level, fold change, p-value,
  sample size, confidence interval, evidence level, pathway, tissue, and
  study reference per gene × season
- **`community_contributions`** — user-submitted rows with a moderation
  `status` (`pending` / `approved` / `rejected`)
- **`dataset_meta`** — current version label, DOI, and last-updated timestamp

---

## 🤝 Contributing

Data contributions go through the in-app **Contribute Data** tab (moderated
before publication). For code contributions:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Open a pull request describing the change

---

## 📚 Citation

If you use this database in your research, please cite:

```bibtex
@misc{seasonal_gene_db_2026,
  author = {S. Unnati},
  title = {Seasonal Physiology Gene Database},
  year = {2026},
  howpublished = {\url{https://seasonal-gene-db-wb4nzf4rwezxmhzrtrcimr.streamlit.app/}}
}
```

*(An up-to-date, version-stamped citation — including a DOI once registered
via Zenodo — is also available from the app's sidebar.)*

---

## 📄 License

- **Code:** MIT License (see [`LICENSE`](LICENSE))
- **Curated data:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
  — free to use with attribution

---

## 🔬 Data Sources

[NCBI Gene](https://www.ncbi.nlm.nih.gov/gene) ·
[PubMed](https://pubmed.ncbi.nlm.nih.gov/) ·
[CircaDB](http://circadb.hogeneschlab.org/) ·
[GEO Datasets](https://www.ncbi.nlm.nih.gov/geo/) ·
[UniProt](https://www.uniprot.org/) ·
[Gene Ontology](https://geneontology.org/) ·
[HGNC](https://www.genenames.org/)
