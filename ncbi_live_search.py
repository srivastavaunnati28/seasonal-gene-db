"""
ncbi_live_search.py
--------------------
Live fallback search: when a gene isn't in your local MySQL DB,
fetch basic info from NCBI Gene and related expression datasets from NCBI GEO.

Drop this file next to your app1.py and import the functions you need.

Requires: requests (already in most environments; add to requirements.txt if missing)
"""

import requests
import time
import xml.etree.ElementTree as ET

NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
API_KEY = None  # optional: get a free NCBI API key to raise rate limit from 3/sec to 10/sec
# https://www.ncbi.nlm.nih.gov/account/settings/  -> create API key, then set API_KEY = "your_key"


def _params(extra: dict) -> dict:
    p = {"retmode": "json"}
    if API_KEY:
        p["api_key"] = API_KEY
    p.update(extra)
    return p


def search_ncbi_gene(gene_symbol: str, organism: str = None, retries: int = 2):
    """
    Look up a gene on NCBI Gene database.
    Returns a dict with basic gene info, or None if not found.
    """
    term = f"{gene_symbol}[gene]"
    if organism:
        term += f" AND {organism}[orgn]"

    for attempt in range(retries + 1):
        try:
            # Step 1: find the Gene ID
            r = requests.get(
                f"{NCBI_BASE}/esearch.fcgi",
                params=_params({"db": "gene", "term": term, "retmax": 1}),
                timeout=10,
            )
            r.raise_for_status()
            ids = r.json().get("esearchresult", {}).get("idlist", [])
            if not ids:
                return None

            gene_id = ids[0]
            time.sleep(0.34)  # respect NCBI's ~3 requests/sec limit without an API key

            # Step 2: get the summary for that Gene ID
            r2 = requests.get(
                f"{NCBI_BASE}/esummary.fcgi",
                params=_params({"db": "gene", "id": gene_id}),
                timeout=10,
            )
            r2.raise_for_status()
            doc = r2.json().get("result", {}).get(gene_id, {})

            return {
                "gene_id": gene_id,
                "symbol": doc.get("name", gene_symbol),
                "full_name": doc.get("description", "N/A"),
                "organism": doc.get("organism", {}).get("scientificname", organism or "N/A"),
                "chromosome": doc.get("chromosome", "N/A"),
                "summary": doc.get("summary", "No summary available."),
                "ncbi_url": f"https://www.ncbi.nlm.nih.gov/gene/{gene_id}",
            }

        except requests.exceptions.RequestException:
            if attempt < retries:
                time.sleep(1)
                continue
            return None


def search_geo_datasets(gene_symbol: str, organism: str = None, max_results: int = 5, retries: int = 2):
    """
    Search NCBI GEO (db='gds') for datasets related to this gene AND
    photoperiod terms (short day / long day / photoperiod).
    Returns a list of dicts with accession, title, summary, and link.
    NOTE: This returns *related dataset references*, not an automatically
    extracted numeric SD-vs-LD expression value (GEO supplementary files
    require per-dataset parsing, which can't be done generically/reliably
    for an arbitrary gene in real time).
    """
    term = f"{gene_symbol} AND (short day OR long day OR photoperiod OR daylength)"
    if organism:
        term += f" AND {organism}[orgn]"

    for attempt in range(retries + 1):
        try:
            r = requests.get(
                f"{NCBI_BASE}/esearch.fcgi",
                params=_params({"db": "gds", "term": term, "retmax": max_results}),
                timeout=10,
            )
            r.raise_for_status()
            ids = r.json().get("esearchresult", {}).get("idlist", [])
            if not ids:
                return []

            time.sleep(0.34)

            r2 = requests.get(
                f"{NCBI_BASE}/esummary.fcgi",
                params=_params({"db": "gds", "id": ",".join(ids)}),
                timeout=10,
            )
            r2.raise_for_status()
            result = r2.json().get("result", {})

            datasets = []
            for uid in ids:
                doc = result.get(uid, {})
                if not doc:
                    continue
                accession = doc.get("accession", "N/A")
                datasets.append({
                    "accession": accession,
                    "title": doc.get("title", "N/A"),
                    "summary": (doc.get("summary", "") or "")[:300],
                    "organism": doc.get("taxon", organism or "N/A"),
                    "n_samples": doc.get("n_samples", "N/A"),
                    "geo_url": f"https://www.ncbi.nlm.nih.gov/gds/?term={accession}",
                })
            return datasets

        except requests.exceptions.RequestException:
            if attempt < retries:
                time.sleep(1)
                continue
            return []


def full_live_lookup(gene_symbol: str, organism: str = None):
    """
    Convenience wrapper: returns combined NCBI Gene info + GEO dataset list.
    """
    gene_info = search_ncbi_gene(gene_symbol, organism)
    geo_datasets = search_geo_datasets(gene_symbol, organism)
    return {
        "gene_info": gene_info,
        "geo_datasets": geo_datasets,
    }


if __name__ == "__main__":
    # quick manual test (run this file directly: python ncbi_live_search.py)
    import json
    result = full_live_lookup("FT", "Arabidopsis thaliana")
    print(json.dumps(result, indent=2))
