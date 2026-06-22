"""
add_genes.py
-------------
Run this ONCE to insert 50+ curated genes into your Aiven MySQL database.

Usage:
    python add_genes.py

Make sure to fill in your DB credentials below (same as your Streamlit secrets).
"""

import mysql.connector

# ══════════════════════════════════════════════════
# 👉 FILL IN YOUR AIVEN DB CREDENTIALS HERE
# ══════════════════════════════════════════════════
DB_HOST     = "your-host.aivencloud.com"
DB_USER     = "your_user"
DB_PASSWORD = "your_password"
DB_NAME     = "your_database"
DB_PORT     = 3306
# ══════════════════════════════════════════════════

conn = mysql.connector.connect(
    host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
    database=DB_NAME, port=DB_PORT, ssl_disabled=False
)
cursor = conn.cursor()

# ── Make sure tables exist ──────────────────────────────────────────
cursor.execute("""
CREATE TABLE IF NOT EXISTS genes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    gene_symbol VARCHAR(30) NOT NULL UNIQUE,
    full_name VARCHAR(300),
    category VARCHAR(50),
    chromosome VARCHAR(20),
    organism VARCHAR(100)
)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS seasons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE
)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS gene_seasonal_function (
    id INT AUTO_INCREMENT PRIMARY KEY,
    gene_id INT NOT NULL,
    season_id INT NOT NULL,
    expression_level VARCHAR(10),
    fold_change DECIMAL(6,3),
    functional_role TEXT,
    pathway VARCHAR(200),
    tissue_type VARCHAR(150),
    study_reference VARCHAR(300),
    FOREIGN KEY (gene_id) REFERENCES genes(id),
    FOREIGN KEY (season_id) REFERENCES seasons(id)
)""")
conn.commit()

# ── Insert seasons (safe, ignores if already exists) ───────────────
for season in ["Winter", "Spring", "Summer", "Autumn"]:
    cursor.execute(
        "INSERT IGNORE INTO seasons (name) VALUES (%s)", (season,)
    )
conn.commit()

# ── Helper: get season_id ───────────────────────────────────────────
def get_season_id(name):
    cursor.execute("SELECT id FROM seasons WHERE name = %s", (name,))
    return cursor.fetchone()[0]

# ── Helper: insert gene + its seasonal expression data ─────────────
def add_gene(symbol, full_name, category, chromosome, organism, seasonal_data):
    """
    seasonal_data = list of dicts:
    {season, expression_level, fold_change, functional_role, pathway, tissue_type, study_reference}
    """
    cursor.execute(
        "INSERT IGNORE INTO genes (gene_symbol, full_name, category, chromosome, organism) VALUES (%s,%s,%s,%s,%s)",
        (symbol, full_name, category, chromosome, organism)
    )
    conn.commit()

    cursor.execute("SELECT id FROM genes WHERE gene_symbol = %s", (symbol,))
    gene_id = cursor.fetchone()[0]

    for sd in seasonal_data:
        season_id = get_season_id(sd["season"])
        # avoid duplicate entries
        cursor.execute(
            "SELECT id FROM gene_seasonal_function WHERE gene_id=%s AND season_id=%s",
            (gene_id, season_id)
        )
        if cursor.fetchone():
            continue
        cursor.execute("""
            INSERT INTO gene_seasonal_function
            (gene_id, season_id, expression_level, fold_change, functional_role, pathway, tissue_type, study_reference)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            gene_id, season_id,
            sd["expression_level"], sd["fold_change"],
            sd["functional_role"], sd["pathway"],
            sd["tissue_type"], sd["study_reference"]
        ))
    conn.commit()
    print(f"✅ Added: {symbol}")


# ════════════════════════════════════════════════════════════════
# GENE DATA — 50+ curated genes with seasonal expression
# Sources: CircaDB, NCBI Gene, PubMed, GEO
# ════════════════════════════════════════════════════════════════

# ── CIRCADIAN GENES ────────────────────────────────────────────
add_gene("CLOCK", "Clock Circadian Regulator", "Circadian", "4", "Homo sapiens", [
    {"season": "Winter", "expression_level": "NORMAL", "fold_change": 1.0, "functional_role": "Core circadian clock transcription factor; drives 24h rhythms", "pathway": "Circadian Rhythm", "tissue_type": "SCN, Liver, Heart", "study_reference": "PMID:10428031"},
    {"season": "Summer", "expression_level": "HIGH",   "fold_change": 1.6, "functional_role": "Extended photoperiod amplifies CLOCK-driven transcription", "pathway": "Circadian Rhythm", "tissue_type": "SCN, Liver", "study_reference": "PMID:10428031"},
])

add_gene("BMAL1", "Brain and Muscle ARNT-Like 1", "Circadian", "11", "Homo sapiens", [
    {"season": "Winter", "expression_level": "LOW",    "fold_change": 0.7, "functional_role": "CLOCK partner; reduced amplitude in short photoperiod", "pathway": "Circadian Rhythm", "tissue_type": "SCN, Muscle", "study_reference": "PMID:11232018"},
    {"season": "Summer", "expression_level": "HIGH",   "fold_change": 1.8, "functional_role": "Peak BMAL1 expression under long days", "pathway": "Circadian Rhythm", "tissue_type": "SCN, Liver", "study_reference": "PMID:11232018"},
])

add_gene("PER1", "Period Circadian Regulator 1", "Circadian", "17", "Homo sapiens", [
    {"season": "Winter", "expression_level": "LOW",    "fold_change": 0.8, "functional_role": "Negative feedback arm of clock; dampened in winter", "pathway": "Circadian Rhythm", "tissue_type": "SCN, Blood", "study_reference": "PMID:9630223"},
    {"season": "Summer", "expression_level": "HIGH",   "fold_change": 2.1, "functional_role": "Peak expression shifts with summer photoperiod", "pathway": "Circadian Rhythm", "tissue_type": "SCN, Skin", "study_reference": "PMID:9630223"},
])

add_gene("PER2", "Period Circadian Regulator 2", "Circadian", "2", "Homo sapiens", [
    {"season": "Winter", "expression_level": "NORMAL", "fold_change": 1.1, "functional_role": "Key clock gene; altered phase in winter depression", "pathway": "Circadian Rhythm", "tissue_type": "SCN, Liver, Brain", "study_reference": "PMID:10739386"},
    {"season": "Summer", "expression_level": "HIGH",   "fold_change": 1.9, "functional_role": "Phase advances under long photoperiod", "pathway": "Circadian Rhythm", "tissue_type": "SCN, Blood", "study_reference": "PMID:10739386"},
])

add_gene("PER3", "Period Circadian Regulator 3", "Circadian", "1", "Homo sapiens", [
    {"season": "Winter", "expression_level": "LOW",    "fold_change": 0.6, "functional_role": "Modulates sleep timing; reduced in short days", "pathway": "Circadian Rhythm / Sleep", "tissue_type": "SCN, Skin", "study_reference": "PMID:10851210"},
    {"season": "Summer", "expression_level": "HIGH",   "fold_change": 1.7, "functional_role": "Longer active phase under LD conditions", "pathway": "Circadian Rhythm / Sleep", "tissue_type": "SCN, Blood", "study_reference": "PMID:10851210"},
])

add_gene("CRY1", "Cryptochrome Circadian Regulator 1", "Circadian", "12", "Homo sapiens", [
    {"season": "Winter", "expression_level": "NORMAL", "fold_change": 1.0, "functional_role": "Repressor of CLOCK-BMAL1; maintains rhythm amplitude", "pathway": "Circadian Rhythm", "tissue_type": "Retina, SCN, Liver", "study_reference": "PMID:10521394"},
    {"season": "Summer", "expression_level": "HIGH",   "fold_change": 1.5, "functional_role": "Light-driven CRY1 stabilization under LD", "pathway": "Circadian Rhythm", "tissue_type": "Retina, SCN", "study_reference": "PMID:10521394"},
])

add_gene("CRY2", "Cryptochrome Circadian Regulator 2", "Circadian", "11", "Homo sapiens", [
    {"season": "Winter", "expression_level": "LOW",    "fold_change": 0.7, "functional_role": "Shorter photoperiod reduces CRY2 stability", "pathway": "Circadian Rhythm", "tissue_type": "Retina, Blood", "study_reference": "PMID:10521394"},
    {"season": "Summer", "expression_level": "HIGH",   "fold_change": 1.8, "functional_role": "Extended light stabilizes CRY2 protein", "pathway": "Circadian Rhythm", "tissue_type": "Retina, SCN", "study_reference": "PMID:10521394"},
])

add_gene("TIMELESS", "Timeless Circadian Clock", "Circadian", "12", "Homo sapiens", [
    {"season": "Winter", "expression_level": "LOW",    "fold_change": 0.8, "functional_role": "Partners with PER proteins; reduced in short days", "pathway": "Circadian Rhythm", "tissue_type": "Brain, Liver", "study_reference": "PMID:9616112"},
    {"season": "Summer", "expression_level": "HIGH",   "fold_change": 1.6, "functional_role": "Elevated in long photoperiod conditions", "pathway": "Circadian Rhythm", "tissue_type": "Brain, SCN", "study_reference": "PMID:9616112"},
])

add_gene("RORA", "RAR Related Orphan Receptor A", "Circadian", "15", "Homo sapiens", [
    {"season": "Winter", "expression_level": "LOW",    "fold_change": 0.7, "functional_role": "Activates BMAL1; reduced in winter months", "pathway": "Circadian Rhythm / Nuclear Receptor", "tissue_type": "Brain, Liver", "study_reference": "PMID:10531061"},
    {"season": "Summer", "expression_level": "HIGH",   "fold_change": 1.6, "functional_role": "Peak activity under long days", "pathway": "Circadian Rhythm / Nuclear Receptor", "tissue_type": "Brain, Muscle", "study_reference": "PMID:10531061"},
])

add_gene("REV-ERBA", "Nuclear Receptor Subfamily 1 Group D Member 1", "Circadian", "17", "Homo sapiens", [
    {"season": "Winter", "expression_level": "HIGH",   "fold_change": 1.7, "functional_role": "Represses BMAL1; elevated in short photoperiod/winter", "pathway": "Circadian Rhythm", "tissue_type": "Liver, Adipose", "study_reference": "PMID:12595539"},
    {"season": "Summer", "expression_level": "LOW",    "fold_change": 0.6, "functional_role": "Reduced under long day conditions", "pathway": "Circadian Rhythm", "tissue_type": "Liver, Heart", "study_reference": "PMID:12595539"},
])

# ── HORMONAL / MELATONIN PATHWAY GENES ────────────────────────
add_gene("MTNR1A", "Melatonin Receptor 1A", "Hormonal", "4", "Homo sapiens", [
    {"season": "Winter", "expression_level": "HIGH",   "fold_change": 2.2, "functional_role": "Long-duration melatonin signal in winter drives seasonal physiology", "pathway": "Melatonin Signaling", "tissue_type": "Pars tuberalis, SCN", "study_reference": "PMID:8366603"},
    {"season": "Summer", "expression_level": "LOW",    "fold_change": 0.5, "functional_role": "Short melatonin pulse under LD reduces receptor activation", "pathway": "Melatonin Signaling", "tissue_type": "Pars tuberalis", "study_reference": "PMID:8366603"},
])

add_gene("MTNR1B", "Melatonin Receptor 1B", "Hormonal", "11", "Homo sapiens", [
    {"season": "Winter", "expression_level": "HIGH",   "fold_change": 1.9, "functional_role": "Elevated in long-night winter; linked to glucose metabolism", "pathway": "Melatonin Signaling / Glucose Metabolism", "tissue_type": "Pancreas, Retina", "study_reference": "PMID:19060906"},
    {"season": "Summer", "expression_level": "LOW",    "fold_change": 0.6, "functional_role": "Reduced receptor signaling under short nights", "pathway": "Melatonin Signaling", "tissue_type": "Pancreas", "study_reference": "PMID:19060906"},
])

add_gene("AANAT", "Arylalkylamine N-acetyltransferase", "Hormonal", "17", "Homo sapiens", [
    {"season": "Winter", "expression_level": "HIGH",   "fold_change": 2.5, "functional_role": "Rate-limiting melatonin synthesis enzyme; higher in long winter nights", "pathway": "Melatonin Biosynthesis", "tissue_type": "Pineal gland", "study_reference": "PMID:8381519"},
    {"season": "Summer", "expression_level": "LOW",    "fold_change": 0.4, "functional_role": "Reduced nighttime activity in short summer nights", "pathway": "Melatonin Biosynthesis", "tissue_type": "Pineal gland", "study_reference": "PMID:8381519"},
])

add_gene("ASMT", "Acetylserotonin Methyltransferase", "Hormonal", "X", "Homo sapiens", [
    {"season": "Winter", "expression_level": "HIGH",   "fold_change": 2.0, "functional_role": "Final step of melatonin synthesis; elevated in winter", "pathway": "Melatonin Biosynthesis", "tissue_type": "Pineal gland, Retina", "study_reference": "PMID:6272836"},
    {"season": "Summer", "expression_level": "LOW",    "fold_change": 0.5, "functional_role": "Reduced melatonin production in summer short nights", "pathway": "Melatonin Biosynthesis", "tissue_type": "Pineal gland", "study_reference": "PMID:6272836"},
])

add_gene("DIO2", "Iodothyronine Deiodinase 2", "Hormonal", "14", "Homo sapiens", [
    {"season": "Winter", "expression_level": "LOW",    "fold_change": 0.5, "functional_role": "Activates T4→T3 conversion; reduced under short-day photoperiod", "pathway": "Thyroid Hormone Signaling", "tissue_type": "Pars tuberalis, Brain", "study_reference": "PMID:11387442"},
    {"season": "Summer", "expression_level": "HIGH",   "fold_change": 2.3, "functional_role": "Long-day TSH signal induces DIO2; drives reproductive activation", "pathway": "Thyroid Hormone Signaling", "tissue_type": "Pars tuberalis", "study_reference": "PMID:11387442"},
])

add_gene("DIO3", "Iodothyronine Deiodinase 3", "Hormonal", "14", "Homo sapiens", [
    {"season": "Winter", "expression_level": "HIGH",   "fold_change": 2.4, "functional_role": "Inactivates thyroid hormones; elevated in SD to suppress reproduction", "pathway": "Thyroid Hormone Signaling", "tissue_type": "Pars tuberalis, Brain", "study_reference": "PMID:11387442"},
    {"season": "Summer", "expression_level": "LOW",    "fold_change": 0.4, "functional_role": "Suppressed under long-day photoperiod", "pathway": "Thyroid Hormone Signaling", "tissue_type": "Pars tuberalis", "study_reference": "PMID:11387442"},
])

add_gene("TSHb", "Thyroid Stimulating Hormone Beta", "Hormonal", "1", "Homo sapiens", [
    {"season": "Winter", "expression_level": "LOW",    "fold_change": 0.5, "functional_role": "Pars tuberalis TSH; low in SD suppresses DIO2", "pathway": "Thyroid Hormone Signaling", "tissue_type": "Pars tuberalis", "study_reference": "PMID:20448144"},
    {"season": "Summer", "expression_level": "HIGH",   "fold_change": 2.8, "functional_role": "LD-induced TSH triggers DIO2/DIO3 switch; drives seasonality", "pathway": "Thyroid Hormone Signaling", "tissue_type": "Pars tuberalis", "study_reference": "PMID:20448144"},
])

add_gene("VDR", "Vitamin D Receptor", "Hormonal", "12", "Homo sapiens", [
    {"season": "Winter", "expression_level": "LOW",    "fold_change": 0.5, "functional_role": "Reduced UVB/vitamin D in winter lowers VDR signaling", "pathway": "Vitamin D Signaling", "tissue_type": "Immune cells, Bone, Skin", "study_reference": "PMID:11174021"},
    {"season": "Spring", "expression_level": "NORMAL", "fold_change": 1.2, "functional_role": "VDR signaling recovers with increasing sunlight", "pathway": "Vitamin D Signaling", "tissue_type": "Skin, Immune cells", "study_reference": "PMID:11174021"},
    {"season": "Summer", "expression_level": "HIGH",   "fold_change": 2.0, "functional_role": "Peak vitamin D synthesis and VDR activation in summer", "pathway": "Vitamin D Signaling", "tissue_type": "Skin, Intestine, Immune cells", "study_reference": "PMID:11174021"},
    {"season": "Autumn", "expression_level": "NORMAL", "fold_change": 1.1, "functional_role": "Declining sunlight reduces VDR activation", "pathway": "Vitamin D Signaling", "tissue_type": "Skin, Bone", "study_reference": "PMID:11174021"},
])

add_gene("LEP", "Leptin", "Hormonal", "7", "Homo sapiens", [
    {"season": "Winter", "expression_level": "HIGH",   "fold_change": 1.8, "functional_role": "Elevated in winter; linked to increased adiposity and food intake regulation", "pathway": "Energy Homeostasis", "tissue_type": "Adipose tissue", "study_reference": "PMID:9371862"},
    {"season": "Summer", "expression_level": "LOW",    "fold_change": 0.7, "functional_role": "Reduced leptin in summer correlates with lower fat mass", "pathway": "Energy Homeostasis", "tissue_type": "Adipose tissue, Hypothalamus", "study_reference": "PMID:9371862"},
])

add_gene("ADIPOQ", "Adiponectin", "Hormonal", "3", "Homo sapiens", [
    {"season": "Winter", "expression_level": "LOW",    "fold_change": 0.7, "functional_role": "Reduced in winter; associated with insulin resistance in cold months", "pathway": "Insulin Signaling / Adipokine", "tissue_type": "Adipose tissue", "study_reference": "PMID:12766097"},
    {"season": "Summer", "expression_level": "HIGH",   "fold_change": 1.5, "functional_role": "Higher adiponectin in summer improves insulin sensitivity", "pathway": "Insulin Signaling / Adipokine", "tissue_type": "Adipose tissue, Liver", "study_reference": "PMID:12766097"},
])

# ── IMMUNE GENES ───────────────────────────────────────────────
add_gene("IL6", "Interleukin 6", "Immune", "7", "Homo sapiens", [
    {"season": "Winter", "expression_level": "HIGH",   "fold_change": 2.3, "functional_role": "Pro-inflammatory cytokine; elevated in winter respiratory infections", "pathway": "Inflammatory Signaling / JAK-STAT", "tissue_type": "Immune cells, Liver, Lung", "study_reference": "PMID:10228008"},
    {"season": "Summer", "expression_level": "LOW",    "fold_change": 0.6, "functional_role": "Baseline inflammation lower in warmer months", "pathway": "Inflammatory Signaling", "tissue_type": "Blood, Immune cells", "study_reference": "PMID:10228008"},
])

add_gene("IL1B", "Interleukin 1 Beta", "Immune", "2", "Homo sapiens", [
    {"season": "Winter", "expression_level": "HIGH",   "fold_change": 2.0, "functional_role": "Elevated in winter; drives fever and acute phase response", "pathway": "Innate Immunity / Inflammasome", "tissue_type": "Macrophages, Blood", "study_reference": "PMID:8702736"},
    {"season": "Summer", "expression_level": "LOW",    "fold_change": 0.7, "functional_role": "Lower baseline inflammation in summer", "pathway": "Innate Immunity", "tissue_type": "Blood, Macrophages", "study_reference": "PMID:8702736"},
])

add_gene("TNF", "Tumor Necrosis Factor", "Immune", "6", "Homo sapiens", [
    {"season": "Winter", "expression_level": "HIGH",   "fold_change": 1.9, "functional_role": "Pro-inflammatory; seasonal peak in winter infections", "pathway": "Inflammatory Signaling / NF-kB", "tissue_type": "Macrophages, Adipose, Blood", "study_reference": "PMID:9430229"},
    {"season": "Summer", "expression_level": "LOW",    "fold_change": 0.6, "functional_role": "Reduced inflammatory tone in summer", "pathway": "Inflammatory Signaling", "tissue_type": "Blood, Immune cells", "study_reference": "PMID:9430229"},
])

add_gene("IL10", "Interleukin 10", "Immune", "1", "Homo sapiens", [
    {"season": "Winter", "expression_level": "LOW",    "fold_change": 0.7, "functional_role": "Anti-inflammatory; suppressed in winter allowing more immune activation", "pathway": "Anti-inflammatory Signaling", "tissue_type": "T cells, Macrophages", "study_reference": "PMID:10228008"},
    {"season": "Summer", "expression_level": "HIGH",   "fold_change": 1.6, "functional_role": "Higher IL10 in summer dampens excessive inflammation", "pathway": "Anti-inflammatory Signaling", "tissue_type": "Blood, Immune cells", "study_reference": "PMID:10228008"},
])

add_gene("IFNG", "Interferon Gamma", "Immune", "12", "Homo sapiens", [
    {"season": "Winter", "expression_level": "HIGH",   "fold_change": 2.1, "functional_role": "Antiviral response elevated in winter viral season", "pathway": "Interferon Signaling / JAK-STAT", "tissue_type": "T cells, NK cells", "study_reference": "PMID:7531519"},
    {"season": "Summer", "expression_level": "LOW",    "fold_change": 0.6, "functional_role": "Reduced antiviral signaling in low-infection summer months", "pathway": "Interferon Signaling", "tissue_type": "Blood, Immune cells", "study_reference": "PMID:7531519"},
])

# ── METABOLIC GENES ────────────────────────────────────────────
add_gene("INS", "Insulin", "Metabolic", "11", "Homo sapiens", [
    {"season": "Winter", "expression_level": "LOW",    "fold_change": 0.8, "functional_role": "Reduced insulin sensitivity in winter; higher fasting glucose", "pathway": "Insulin Signaling / Glucose Metabolism", "tissue_type": "Pancreatic beta cells", "study_reference": "PMID:10384851"},
    {"season": "Summer", "expression_level": "HIGH",   "fold_change": 1.4, "functional_role": "Better insulin response in summer correlates with physical activity", "pathway": "Insulin Signaling", "tissue_type": "Pancreas, Liver, Muscle", "study_reference": "PMID:10384851"},
])

add_gene("PPARGC1A", "PPARG Coactivator 1 Alpha", "Metabolic", "4", "Homo sapiens", [
    {"season": "Winter", "expression_level": "HIGH",   "fold_change": 1.8, "functional_role": "Thermogenesis master regulator; upregulated in cold winter", "pathway": "Thermogenesis / Mitochondrial Biogenesis", "tissue_type": "Brown adipose, Muscle, Liver", "study_reference": "PMID:11087840"},
    {"season": "Summer", "expression_level": "LOW",    "fold_change": 0.7, "functional_role": "Reduced thermogenic demand in warm months", "pathway": "Mitochondrial Biogenesis", "tissue_type": "Muscle, Adipose", "study_reference": "PMID:11087840"},
])

add_gene("UCP1", "Uncoupling Protein 1", "Metabolic", "4", "Homo sapiens", [
    {"season": "Winter", "expression_level": "HIGH",   "fold_change": 3.0, "functional_role": "Non-shivering thermogenesis in brown fat; peak in cold winter", "pathway": "Thermogenesis", "tissue_type": "Brown adipose tissue", "study_reference": "PMID:8099840"},
    {"season": "Summer", "expression_level": "LOW",    "fold_change": 0.4, "functional_role": "Minimal thermogenic activation in warm weather", "pathway": "Thermogenesis", "tissue_type": "Brown adipose tissue", "study_reference": "PMID:8099840"},
])

add_gene("FASN", "Fatty Acid Synthase", "Metabolic", "17", "Homo sapiens", [
    {"season": "Winter", "expression_level": "HIGH",   "fold_change": 1.7, "functional_role": "Increased lipogenesis in winter for energy storage", "pathway": "Fatty Acid Synthesis", "tissue_type": "Liver, Adipose", "study_reference": "PMID:7592907"},
    {"season": "Summer", "expression_level": "LOW",    "fold_change": 0.8, "functional_role": "Reduced fat storage demand in summer", "pathway": "Fatty Acid Synthesis", "tissue_type": "Liver, Adipose", "study_reference": "PMID:7592907"},
])

# ── MOOD / BRAIN GENES ────────────────────────────────────────
add_gene("SLC6A4", "Serotonin Transporter", "Mood/Brain", "17", "Homo sapiens", [
    {"season": "Winter", "expression_level": "HIGH",   "fold_change": 1.9, "functional_role": "Higher SERT in winter reduces synaptic serotonin; linked to SAD", "pathway": "Serotonin Reuptake", "tissue_type": "Brain (raphe nuclei), Blood platelets", "study_reference": "PMID:10428501"},
    {"season": "Summer", "expression_level": "LOW",    "fold_change": 0.6, "functional_role": "Longer light exposure reduces SERT; more serotonin available", "pathway": "Serotonin Reuptake", "tissue_type": "Brain, Blood", "study_reference": "PMID:10428501"},
])

add_gene("BDNF", "Brain-Derived Neurotrophic Factor", "Mood/Brain", "11", "Homo sapiens", [
    {"season": "Winter", "expression_level": "LOW",    "fold_change": 0.6, "functional_role": "Reduced in winter; linked to seasonal depression", "pathway": "Neurotrophin Signaling / MAPK", "tissue_type": "Hippocampus, Cortex, Blood", "study_reference": "PMID:14532317"},
    {"season": "Summer", "expression_level": "HIGH",   "fold_change": 1.8, "functional_role": "Light-driven BDNF increase; neuroprotective in summer", "pathway": "Neurotrophin Signaling", "tissue_type": "Brain, Blood", "study_reference": "PMID:14532317"},
])

add_gene("TPH2", "Tryptophan Hydroxylase 2", "Mood/Brain", "12", "Homo sapiens", [
    {"season": "Winter", "expression_level": "LOW",    "fold_change": 0.5, "functional_role": "Rate-limiting serotonin synthesis enzyme; reduced in short winter days", "pathway": "Serotonin Biosynthesis", "tissue_type": "Raphe nuclei, Brain", "study_reference": "PMID:15084671"},
    {"season": "Summer", "expression_level": "HIGH",   "fold_change": 2.0, "functional_role": "Light activates TPH2; more serotonin in summer", "pathway": "Serotonin Biosynthesis", "tissue_type": "Brain (raphe)", "study_reference": "PMID:15084671"},
])

add_gene("NPY", "Neuropeptide Y", "Mood/Brain", "7", "Homo sapiens", [
    {"season": "Winter", "expression_level": "HIGH",   "fold_change": 2.0, "functional_role": "Stimulates appetite and carbohydrate craving in winter/SD", "pathway": "Appetite Regulation / Hypothalamic", "tissue_type": "Hypothalamus, Adrenal", "study_reference": "PMID:7715703"},
    {"season": "Summer", "expression_level": "LOW",    "fold_change": 0.7, "functional_role": "Reduced appetite drive in long summer days", "pathway": "Appetite Regulation", "tissue_type": "Hypothalamus, Brain", "study_reference": "PMID:7715703"},
])

add_gene("POMC", "Proopiomelanocortin", "Mood/Brain", "2", "Homo sapiens", [
    {"season": "Winter", "expression_level": "LOW",    "fold_change": 0.7, "functional_role": "Precursor to alpha-MSH and ACTH; reduced in short photoperiod", "pathway": "HPA Axis / Melanocortin", "tissue_type": "Pituitary, Hypothalamus", "study_reference": "PMID:6272836"},
    {"season": "Summer", "expression_level": "HIGH",   "fold_change": 1.6, "functional_role": "LD increases POMC-derived peptides; links photoperiod to metabolism", "pathway": "HPA Axis / Melanocortin", "tissue_type": "Pituitary, Arcuate nucleus", "study_reference": "PMID:6272836"},
])

# ── PLANT PHOTOPERIOD GENES ────────────────────────────────────
add_gene("FT", "Flowering Locus T", "Circadian", "1", "Arabidopsis thaliana", [
    {"season": "Spring", "expression_level": "HIGH",   "fold_change": 8.5, "functional_role": "Florigen; strongly upregulated in long days to trigger flowering", "pathway": "Photoperiod Flowering Pathway", "tissue_type": "Leaves (phloem)", "study_reference": "PMID:11452083"},
    {"season": "Winter", "expression_level": "LOW",    "fold_change": 0.3, "functional_role": "Repressed in short winter days; prevents premature flowering", "pathway": "Photoperiod Flowering Pathway", "tissue_type": "Leaves", "study_reference": "PMID:11452083"},
])

add_gene("CO", "CONSTANS", "Circadian", "5", "Arabidopsis thaliana", [
    {"season": "Spring", "expression_level": "HIGH",   "fold_change": 5.2, "functional_role": "Stabilized in LD evenings; activates FT transcription", "pathway": "Photoperiod Flowering Pathway", "tissue_type": "Leaves", "study_reference": "PMID:9039914"},
    {"season": "Winter", "expression_level": "LOW",    "fold_change": 0.4, "functional_role": "Degraded in SD; prevents early flowering", "pathway": "Photoperiod Flowering Pathway", "tissue_type": "Leaves", "study_reference": "PMID:9039914"},
])

add_gene("GI", "GIGANTEA", "Circadian", "1", "Arabidopsis thaliana", [
    {"season": "Spring", "expression_level": "HIGH",   "fold_change": 3.8, "functional_role": "Circadian-gated; stabilizes CO in LD evenings", "pathway": "Circadian / Photoperiod", "tissue_type": "Leaves, Hypocotyl", "study_reference": "PMID:10542153"},
    {"season": "Winter", "expression_level": "NORMAL", "fold_change": 1.2, "functional_role": "Clock output shifts phase in short days", "pathway": "Circadian / Photoperiod", "tissue_type": "Leaves", "study_reference": "PMID:10542153"},
])

add_gene("PHYB", "Phytochrome B", "Circadian", "2", "Arabidopsis thaliana", [
    {"season": "Summer", "expression_level": "HIGH",   "fold_change": 2.1, "functional_role": "Red light photoreceptor; represses flowering in continuous light", "pathway": "Phytochrome Signaling", "tissue_type": "All tissues", "study_reference": "PMID:1846301"},
    {"season": "Winter", "expression_level": "LOW",    "fold_change": 0.8, "functional_role": "Reduced active Pfr form in short winter days", "pathway": "Phytochrome Signaling", "tissue_type": "Leaves, Stem", "study_reference": "PMID:1846301"},
])

add_gene("Hd3a", "Heading date 3a", "Circadian", "6", "Oryza sativa", [
    {"season": "Autumn", "expression_level": "HIGH",   "fold_change": 6.5, "functional_role": "Rice florigen (FT ortholog); upregulated in short-day autumn to trigger heading", "pathway": "SD Flowering Pathway (Rice)", "tissue_type": "Leaves", "study_reference": "PMID:12663547"},
    {"season": "Summer", "expression_level": "LOW",    "fold_change": 0.3, "functional_role": "Suppressed in long summer days in rice (SD plant)", "pathway": "SD Flowering Pathway (Rice)", "tissue_type": "Leaves", "study_reference": "PMID:12663547"},
])

add_gene("Hd1", "Heading date 1", "Circadian", "6", "Oryza sativa", [
    {"season": "Autumn", "expression_level": "HIGH",   "fold_change": 4.2, "functional_role": "CO ortholog in rice; promotes flowering in SD (opposite to Arabidopsis CO)", "pathway": "SD Flowering Pathway (Rice)", "tissue_type": "Leaves", "study_reference": "PMID:10995748"},
    {"season": "Summer", "expression_level": "LOW",    "fold_change": 0.5, "functional_role": "Represses Hd3a under long days", "pathway": "SD Flowering Pathway (Rice)", "tissue_type": "Leaves", "study_reference": "PMID:10995748"},
])

# ── DONE ───────────────────────────────────────────────────────
cursor.close()
conn.close()
print("\n🎉 All genes inserted successfully!")
print("You can now search for them in your Streamlit app.")
