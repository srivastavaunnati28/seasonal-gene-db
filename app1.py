import streamlit as st
import mysql.connector

st.title("🔧 One-Time Database Setup")

if st.button("Create Tables & Insert Data"):
    conn = mysql.connector.connect(
        host="db4free.net",
        user="unnati2026",
        password="Unnati@2026",
        database="seasonalgenedb",
        port=3306
    )
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS genes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        gene_symbol VARCHAR(20) UNIQUE NOT NULL,
        full_name VARCHAR(200),
        organism VARCHAR(50),
        chromosome VARCHAR(10),
        gene_type VARCHAR(50),
        category VARCHAR(50)
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS seasons (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(20),
        start_month INT,
        end_month INT,
        hemisphere CHAR(1)
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gene_seasonal_function (
        id INT AUTO_INCREMENT PRIMARY KEY,
        gene_id INT,
        season_id INT,
        expression_level VARCHAR(10),
        fold_change DECIMAL(6,3),
        functional_role TEXT,
        pathway VARCHAR(200),
        biological_process VARCHAR(100),
        tissue_type VARCHAR(100),
        study_reference VARCHAR(200),
        FOREIGN KEY (gene_id) REFERENCES genes(id),
        FOREIGN KEY (season_id) REFERENCES seasons(id)
    )""")
    conn.commit()
    st.success("✅ Tables created!")
    
    seasons_data = [
        ('Winter', 12, 2, 'N'), ('Spring', 3, 5, 'N'),
        ('Summer', 6, 8, 'N'), ('Autumn', 9, 11, 'N'),
    ]
    cursor.executemany("INSERT IGNORE INTO seasons (name, start_month, end_month, hemisphere) VALUES (%s,%s,%s,%s)", seasons_data)
    conn.commit()
    
    genes_data = [
        ('CLOCK','Circadian Locomotor Output Cycles Kaput','Homo sapiens','4q12','protein-coding','Circadian'),
        ('BMAL1','Brain and Muscle ARNT-Like 1','Homo sapiens','11p15.3','protein-coding','Circadian'),
        ('CRY1','Cryptochrome Circadian Regulator 1','Homo sapiens','12q23.3','protein-coding','Circadian'),
        ('VDR','Vitamin D Receptor','Homo sapiens','12q13.11','protein-coding','Hormonal'),
        ('AANAT','Aralkylamine N-Acetyltransferase','Homo sapiens','17q25.1','protein-coding','Hormonal'),
        ('IL6','Interleukin-6','Homo sapiens','7p15.3','protein-coding','Immune'),
        ('TNF','Tumor Necrosis Factor Alpha','Homo sapiens','6p21.33','protein-coding','Immune'),
        ('LEP','Leptin','Homo sapiens','7q32.1','protein-coding','Metabolic'),
        ('UCP1','Uncoupling Protein 1','Homo sapiens','4q31.1','protein-coding','Metabolic'),
        ('SLC6A4','Serotonin Transporter','Homo sapiens','17q11.2','protein-coding','Mood/Brain'),
    ]
    cursor.executemany("INSERT IGNORE INTO genes (gene_symbol,full_name,organism,chromosome,gene_type,category) VALUES (%s,%s,%s,%s,%s,%s)", genes_data)
    conn.commit()
    
    expression_data = [
        ('CLOCK','Winter','HIGH',2.3,'Drives melatonin production during long nights','Circadian Rhythm','Photoperiodism','Suprachiasmatic Nucleus','PMID:28192901'),
        ('CLOCK','Spring','NORMAL',1.1,'Resets circadian phase as photoperiod lengthens','Circadian Rhythm','Phase Shift','Hypothalamus','PMID:30894687'),
        ('CLOCK','Summer','LOW',0.6,'Short dark phase compresses CLOCK activity','Circadian Rhythm','Photoperiodism','Suprachiasmatic Nucleus','PMID:31076454'),
        ('CLOCK','Autumn','NORMAL',1.3,'Prepares metabolic switch for winter','Circadian Rhythm','Seasonal Adapt.','Hypothalamus','PMID:29402395'),
        ('VDR','Winter','LOW',0.4,'Reduced UV-B suppresses immune gene expression','Vitamin D / Immune','Immune Modulation','Immune cells, Bone','PMID:29480918'),
        ('VDR','Spring','NORMAL',1.1,'Vitamin D recovery restores antimicrobials','Vitamin D Signaling','Innate Immunity','Skin, Lung','PMID:30087983'),
        ('VDR','Summer','HIGH',2.4,'Peak UV-B drives calcium absorption','Vitamin D / Calcium','Bone Remodelling','Intestine, Bone, Skin','PMID:31152777'),
        ('VDR','Autumn','NORMAL',1.3,'Stored Vitamin D buffers immune function','Vitamin D Signaling','Immune Maintenance','Liver, Kidney','PMID:28740998'),
        ('IL6','Winter','HIGH',3.1,'Cold drives IL-6 surge, elevates inflammation','JAK-STAT / NF-kB','Acute Phase','Liver, Macrophages','PMID:27683120'),
        ('IL6','Spring','NORMAL',1.2,'IL-6 normalises, allergy sensitisation begins','Allergic Inflammation','IgE Sensitisation','Mast cells','PMID:30412778'),
        ('IL6','Summer','LOW',0.6,'Vitamin D suppresses IL-6 via IL-10 pathway','Th1/Th2 Balance','Immune Tolerance','T cells','PMID:29785994'),
        ('IL6','Autumn','NORMAL',1.4,'Rising IL-6 prepares for winter pathogens','Pro-inflammatory','Immune Priming','Peripheral blood','PMID:28290498'),
        ('LEP','Winter','HIGH',2.8,'Elevated leptin signals energy surplus','Leptin-Melanocortin','Energy Homeostasis','Adipose, Hypothalamus','PMID:26983140'),
        ('LEP','Spring','NORMAL',1.2,'Leptin sensitivity restores, supports loss','Appetite Regulation','Caloric Restriction','Hypothalamus','PMID:29893683'),
        ('LEP','Summer','LOW',0.7,'Heat suppresses appetite and leptin','Thermosensory/Leptin','Thermogenesis','Adipose, Hypothalamus','PMID:31268436'),
        ('LEP','Autumn','NORMAL',1.5,'Rising leptin promotes fat deposition','PPAR-y / Adipogenesis','Lipid Storage','White Adipose','PMID:28290498'),
        ('SLC6A4','Winter','HIGH',2.2,'High SERT clears serotonin - linked to SAD','Serotonergic','Mood Regulation','Raphe nuclei, PFC','PMID:26999033'),
        ('SLC6A4','Spring','NORMAL',1.1,'SERT declines, serotonin rises, mood improves','Serotonergic','Antidepressant','Raphe nuclei','PMID:28965836'),
        ('SLC6A4','Summer','LOW',0.5,'Minimum SERT drives positive mood','Serotonergic/Dopamine','Reward Processing','Striatum, PFC','PMID:31406378'),
        ('SLC6A4','Autumn','NORMAL',1.3,'Rising SERT causes autumn melancholy','Serotonergic','Appetite & Mood','Gut, Brain','PMID:27683120'),
    ]
    
    for row in expression_data:
        cursor.execute("SELECT id FROM genes WHERE gene_symbol = %s", (row[0],))
        gene_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM seasons WHERE name = %s", (row[1],))
        season_id = cursor.fetchone()[0]
        cursor.execute("""
            INSERT INTO gene_seasonal_function 
            (gene_id, season_id, expression_level, fold_change, functional_role, pathway, biological_process, tissue_type, study_reference)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (gene_id, season_id, row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
    
    conn.commit()
    st.success(f"✅ {len(expression_data)} expression records inserted!")
    conn.close()
