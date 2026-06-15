# 🧬 Seasonal Physiology Gene Database

A searchable web database for exploring **seasonal gene expression** 
in human physiology — built as part of physiology research.

---

## 🔬 About the Project

This database allows researchers to:
- Search any gene by symbol (CLOCK, VDR, IL6, etc.)
- View expression levels across **Winter / Spring / Summer / Autumn**
- Understand the **functional role** of each gene per season
- Explore **pathways, tissue types, and PubMed references**

---

## 🧪 Genes Covered

| Gene | Full Name | Category |
|------|-----------|----------|
| CLOCK | Circadian Locomotor Output Cycles Kaput | Circadian |
| BMAL1 | Brain and Muscle ARNT-Like 1 | Circadian |
| CRY1 | Cryptochrome Circadian Regulator 1 | Circadian |
| VDR | Vitamin D Receptor | Hormonal |
| AANAT | Aralkylamine N-Acetyltransferase | Hormonal |
| IL6 | Interleukin-6 | Immune |
| TNF | Tumor Necrosis Factor Alpha | Immune |
| LEP | Leptin | Metabolic |
| UCP1 | Uncoupling Protein 1 | Metabolic |
| SLC6A4 | Serotonin Transporter | Mood/Brain |

---

## 🌍 Seasons Covered

| Season | Months | Key Biology |
|--------|--------|-------------|
| ❄️ Winter | Dec – Feb | High melatonin, inflammation, SAD |
| 🌱 Spring | Mar – May | Circadian reset, allergy onset |
| ☀️ Summer | Jun – Aug | Peak Vitamin D, low inflammation |
| 🍂 Autumn | Sep – Nov | Immune priming, fat deposition |

---

## 🛠️ Built With

- **Python 3.11**
- **MySQL** — relational gene database
- **Streamlit** — interactive web interface
- **Plotly** — seasonal expression charts
- **Pandas** — data processing
- **BioPython** — gene data fetching (NCBI)

✅ ---
## 📊 Database Schema

genes ──────────────────── gene_seasonal_function ──── seasons
(gene_symbol, full_name,   (expression_level,          (name,
 organism, chromosome,      fold_change,                 start_month,
 category)                  functional_role,             end_month,
                            pathway, tissue_type,        hemisphere)
                            study_reference)


---

## 🚀 How to Run Locally

**1. Clone the repository**
```bash
git clone https://github.com/unnatisrivastava952/seasonal-gene-db
cd seasonal-gene-db
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Setup MySQL database**
```bash
mysql -u root -p
source setup_db.sql
```

**4. Run the app**
```bash
streamlit run app1.py
```

---

## 🌐 Live Demo

👉 [Click here to open the database](#)  
*(Link will be updated after deployment)*

---

## 📁 Data Sources

- [NCBI Gene Database](https://www.ncbi.nlm.nih.gov/gene)
- [GEO Datasets](https://www.ncbi.nlm.nih.gov/geo)
- [UniProt](https://www.uniprot.org)
- [CircaDB](http://circadb.hogeneschlab.org)
- PubMed references included per gene entry

---

## 👩‍🔬 Author

**Unnati Srivastava**  
Research Assistant  
University of Allahabad, Prayagraj  
[LinkedIn](https://www.linkedin.com/in/unnati-srivastava-24166731b)  
✅ [GitHub](https://github.com/unnatisrivastava952/seasonal-gene-db)

---

## 📄 License

This project is for academic and research purposes.




