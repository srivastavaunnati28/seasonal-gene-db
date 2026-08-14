-- ════════════════════════════════════════════════════════════════
-- REAL CURATED DATA — Seasonal Physiology Gene Database
-- ════════════════════════════════════════════════════════════════
-- Every row below is sourced from an actual published, PMID-cited
-- study. Fold-change and p-value columns are left NULL where the
-- exact number could not be verified from the paper's main text
-- (they're typically locked in supplementary figures/tables) —
-- inventing those numbers would be scientifically dishonest, so
-- this script does not do that. Direction of change (HIGH/LOW,
-- SD/LD) IS directly reported in the cited papers' text.
--
-- Sources used:
--   [A] Nakao N, Ono H, Yamamura T, et al. (2008). Thyrotrophin in
--       the pars tuberalis triggers photoperiodic response.
--       Nature 452:317-322. PMID: 18354476
--   [B] Xia Q, Chu M, He X, et al. (2021). Identification of
--       Photoperiod-Induced LncRNAs and mRNAs in Pituitary Pars
--       Tuberalis of Sheep. Front Vet Sci 8:644474. PMID: 34414222
--
-- HOW TO RUN: paste this into your MySQL client (phpMyAdmin, MySQL
-- Workbench, or `mysql` CLI) connected to the same database your
-- Streamlit app uses. Safe to re-run — every INSERT checks for an
-- existing row first, so it won't create duplicates.
-- ════════════════════════════════════════════════════════════════

-- Ensure every gene referenced below exists in the genes table first.
INSERT INTO genes (gene_symbol, full_name, category, chromosome, organism)
SELECT * FROM (SELECT 'TSHB' AS gene_symbol, 'Thyroid Stimulating Hormone Subunit Beta' AS full_name, 'Hormonal' AS category, 'N/A' AS chromosome, 'Multi-species (quail, sheep)' AS organism) AS tmp
WHERE NOT EXISTS (SELECT 1 FROM genes WHERE gene_symbol = 'TSHB');

INSERT INTO genes (gene_symbol, full_name, category, chromosome, organism)
SELECT * FROM (SELECT 'DIO2', 'Iodothyronine Deiodinase 2', 'Hormonal', 'N/A', 'Coturnix japonica (quail)') AS tmp
WHERE NOT EXISTS (SELECT 1 FROM genes WHERE gene_symbol = 'DIO2');

INSERT INTO genes (gene_symbol, full_name, category, chromosome, organism)
SELECT * FROM (SELECT 'EYA3', 'EYA Transcriptional Coactivator And Phosphatase 3', 'Hormonal', 'N/A', 'Ovis aries (sheep)') AS tmp
WHERE NOT EXISTS (SELECT 1 FROM genes WHERE gene_symbol = 'EYA3');

INSERT INTO genes (gene_symbol, full_name, category, chromosome, organism)
SELECT * FROM (SELECT 'SIX1', 'SIX Homeobox 1', 'Hormonal', 'N/A', 'Ovis aries (sheep)') AS tmp
WHERE NOT EXISTS (SELECT 1 FROM genes WHERE gene_symbol = 'SIX1');

INSERT INTO genes (gene_symbol, full_name, category, chromosome, organism)
SELECT * FROM (SELECT 'DCT', 'Dopachrome Tautomerase', 'Other', 'N/A', 'Ovis aries (sheep)') AS tmp
WHERE NOT EXISTS (SELECT 1 FROM genes WHERE gene_symbol = 'DCT');

INSERT INTO genes (gene_symbol, full_name, category, chromosome, organism)
SELECT * FROM (SELECT 'CHGA', 'Chromogranin A', 'Hormonal', 'N/A', 'Ovis aries (sheep)') AS tmp
WHERE NOT EXISTS (SELECT 1 FROM genes WHERE gene_symbol = 'CHGA');

INSERT INTO genes (gene_symbol, full_name, category, chromosome, organism)
SELECT * FROM (SELECT 'FOS', 'Fos Proto-Oncogene, AP-1 Transcription Factor Subunit', 'Other', 'N/A', 'Ovis aries (sheep)') AS tmp
WHERE NOT EXISTS (SELECT 1 FROM genes WHERE gene_symbol = 'FOS');

INSERT INTO genes (gene_symbol, full_name, category, chromosome, organism)
SELECT * FROM (SELECT 'SOCS3', 'Suppressor Of Cytokine Signaling 3', 'Immune', 'N/A', 'Ovis aries (sheep)') AS tmp
WHERE NOT EXISTS (SELECT 1 FROM genes WHERE gene_symbol = 'SOCS3');

INSERT INTO genes (gene_symbol, full_name, category, chromosome, organism)
SELECT * FROM (SELECT 'TH', 'Tyrosine Hydroxylase', 'Mood/Brain', 'N/A', 'Ovis aries (sheep)') AS tmp
WHERE NOT EXISTS (SELECT 1 FROM genes WHERE gene_symbol = 'TH');

-- ────────────────────────────────────────────────────────────────
-- Curated season/photoperiod rows.
-- Winter season row = SD photoperiod condition; Summer season row = LD.
-- fold_change, p_value, sample_size, ci_lower, ci_upper are left NULL
-- (not verified from the cited paper's accessible text).
-- ────────────────────────────────────────────────────────────────

-- [A] TSHB — HIGH under LD — pars tuberalis — quail — Nakao et al. 2008
INSERT INTO gene_seasonal_function
    (gene_id, season_id, expression_level, functional_role, pathway,
     tissue_type, study_reference, photoperiod_condition, evidence_level)
SELECT g.id, s.id, 'HIGH',
       'Induced approximately 14h after dawn of the first long day; first wave of the photoperiodic gene-expression cascade in the pars tuberalis (Nakao et al. 2008, Japanese quail).',
       'Thyroid-Hormone Seasonal Switch', 'Pars tuberalis', 'PMID 18354476', 'LD',
       'Direct experimental (this study)'
FROM genes g, seasons s
WHERE g.gene_symbol = 'TSHB' AND s.name = 'Summer'
  AND NOT EXISTS (
      SELECT 1 FROM gene_seasonal_function gsf
      WHERE gsf.gene_id = g.id AND gsf.season_id = s.id
        AND gsf.tissue_type = 'Pars tuberalis' AND gsf.study_reference = 'PMID 18354476'
  );

-- [A] DIO2 — HIGH under LD — mediobasal hypothalamus — quail — Nakao et al. 2008
INSERT INTO gene_seasonal_function
    (gene_id, season_id, expression_level, functional_role, pathway,
     tissue_type, study_reference, photoperiod_condition, evidence_level)
SELECT g.id, s.id, 'HIGH',
       'Induced approximately 4h after TSHB induction under long day; second wave of the photoperiodic cascade, locally activates thyroid hormone (Nakao et al. 2008, Japanese quail).',
       'Thyroid-Hormone Seasonal Switch', 'Mediobasal hypothalamus', 'PMID 18354476', 'LD',
       'Direct experimental (this study)'
FROM genes g, seasons s
WHERE g.gene_symbol = 'DIO2' AND s.name = 'Summer'
  AND NOT EXISTS (
      SELECT 1 FROM gene_seasonal_function gsf
      WHERE gsf.gene_id = g.id AND gsf.season_id = s.id
        AND gsf.tissue_type = 'Mediobasal hypothalamus' AND gsf.study_reference = 'PMID 18354476'
  );

-- [B] EYA3 — HIGH under LD — pars tuberalis — sheep — Xia et al. 2021
INSERT INTO gene_seasonal_function
    (gene_id, season_id, expression_level, functional_role, pathway,
     tissue_type, study_reference, photoperiod_condition, evidence_level)
SELECT g.id, s.id, 'HIGH',
       'Notable long-photoperiod (LP)-induced candidate gene identified by RNA-seq comparison of short vs. long photoperiod in Sunite ewe pars tuberalis (Xia et al. 2021).',
       'Photoperiod / Melatonin Pathway', 'Pars tuberalis', 'PMID 34414222', 'LD',
       'Direct experimental (this study)'
FROM genes g, seasons s
WHERE g.gene_symbol = 'EYA3' AND s.name = 'Summer'
  AND NOT EXISTS (
      SELECT 1 FROM gene_seasonal_function gsf
      WHERE gsf.gene_id = g.id AND gsf.season_id = s.id
        AND gsf.tissue_type = 'Pars tuberalis' AND gsf.study_reference = 'PMID 34414222'
  );

-- [B] TSHB — HIGH under LD — pars tuberalis — sheep — Xia et al. 2021
INSERT INTO gene_seasonal_function
    (gene_id, season_id, expression_level, functional_role, pathway,
     tissue_type, study_reference, photoperiod_condition, evidence_level)
SELECT g.id, s.id, 'HIGH',
       'LP-induced candidate gene in Sunite ewe pars tuberalis RNA-seq (SP vs. LP comparison), corroborating the avian finding in a mammalian species (Xia et al. 2021).',
       'Thyroid-Hormone Seasonal Switch', 'Pars tuberalis', 'PMID 34414222', 'LD',
       'Direct experimental (this study)'
FROM genes g, seasons s
WHERE g.gene_symbol = 'TSHB' AND s.name = 'Summer'
  AND NOT EXISTS (
      SELECT 1 FROM gene_seasonal_function gsf
      WHERE gsf.gene_id = g.id AND gsf.season_id = s.id
        AND gsf.tissue_type = 'Pars tuberalis' AND gsf.study_reference = 'PMID 34414222'
  );

-- [B] SIX1 — HIGH under LD — pars tuberalis — sheep — Xia et al. 2021
INSERT INTO gene_seasonal_function
    (gene_id, season_id, expression_level, functional_role, pathway,
     tissue_type, study_reference, photoperiod_condition, evidence_level)
SELECT g.id, s.id, 'HIGH',
       'LP-induced candidate gene identified by RNA-seq in Sunite ewe pars tuberalis (Xia et al. 2021).',
       'Photoperiod / Melatonin Pathway', 'Pars tuberalis', 'PMID 34414222', 'LD',
       'Direct experimental (this study)'
FROM genes g, seasons s
WHERE g.gene_symbol = 'SIX1' AND s.name = 'Summer'
  AND NOT EXISTS (
      SELECT 1 FROM gene_seasonal_function gsf
      WHERE gsf.gene_id = g.id AND gsf.season_id = s.id
        AND gsf.tissue_type = 'Pars tuberalis' AND gsf.study_reference = 'PMID 34414222'
  );

-- [B] DCT — HIGH under LD — pars tuberalis — sheep — Xia et al. 2021
INSERT INTO gene_seasonal_function
    (gene_id, season_id, expression_level, functional_role, pathway,
     tissue_type, study_reference, photoperiod_condition, evidence_level)
SELECT g.id, s.id, 'HIGH',
       'LP-induced candidate gene identified by RNA-seq in Sunite ewe pars tuberalis (Xia et al. 2021).',
       'Photoperiod / Melatonin Pathway', 'Pars tuberalis', 'PMID 34414222', 'LD',
       'Direct experimental (this study)'
FROM genes g, seasons s
WHERE g.gene_symbol = 'DCT' AND s.name = 'Summer'
  AND NOT EXISTS (
      SELECT 1 FROM gene_seasonal_function gsf
      WHERE gsf.gene_id = g.id AND gsf.season_id = s.id
        AND gsf.tissue_type = 'Pars tuberalis' AND gsf.study_reference = 'PMID 34414222'
  );

-- [B] CHGA — HIGH under SD — pars tuberalis — sheep — Xia et al. 2021
INSERT INTO gene_seasonal_function
    (gene_id, season_id, expression_level, functional_role, pathway,
     tissue_type, study_reference, photoperiod_condition, evidence_level)
SELECT g.id, s.id, 'HIGH',
       'Short-photoperiod (SP)-induced candidate gene in Sunite ewe pars tuberalis RNA-seq; its high expression is characteristic of the short-photoperiod state (Xia et al. 2021).',
       'Thyroid-Hormone Seasonal Switch', 'Pars tuberalis', 'PMID 34414222', 'SD',
       'Direct experimental (this study)'
FROM genes g, seasons s
WHERE g.gene_symbol = 'CHGA' AND s.name = 'Winter'
  AND NOT EXISTS (
      SELECT 1 FROM gene_seasonal_function gsf
      WHERE gsf.gene_id = g.id AND gsf.season_id = s.id
        AND gsf.tissue_type = 'Pars tuberalis' AND gsf.study_reference = 'PMID 34414222'
  );

-- [B] FOS — HIGH under SD — pars tuberalis — sheep — Xia et al. 2021
INSERT INTO gene_seasonal_function
    (gene_id, season_id, expression_level, functional_role, pathway,
     tissue_type, study_reference, photoperiod_condition, evidence_level)
SELECT g.id, s.id, 'HIGH',
       'SP-induced candidate gene identified by RNA-seq in Sunite ewe pars tuberalis (Xia et al. 2021).',
       'Thyroid-Hormone Seasonal Switch', 'Pars tuberalis', 'PMID 34414222', 'SD',
       'Direct experimental (this study)'
FROM genes g, seasons s
WHERE g.gene_symbol = 'FOS' AND s.name = 'Winter'
  AND NOT EXISTS (
      SELECT 1 FROM gene_seasonal_function gsf
      WHERE gsf.gene_id = g.id AND gsf.season_id = s.id
        AND gsf.tissue_type = 'Pars tuberalis' AND gsf.study_reference = 'PMID 34414222'
  );

-- [B] SOCS3 — HIGH under SD — pars tuberalis — sheep — Xia et al. 2021
INSERT INTO gene_seasonal_function
    (gene_id, season_id, expression_level, functional_role, pathway,
     tissue_type, study_reference, photoperiod_condition, evidence_level)
SELECT g.id, s.id, 'HIGH',
       'SP-induced candidate gene identified by RNA-seq in Sunite ewe pars tuberalis (Xia et al. 2021).',
       'Thyroid-Hormone Seasonal Switch', 'Pars tuberalis', 'PMID 34414222', 'SD',
       'Direct experimental (this study)'
FROM genes g, seasons s
WHERE g.gene_symbol = 'SOCS3' AND s.name = 'Winter'
  AND NOT EXISTS (
      SELECT 1 FROM gene_seasonal_function gsf
      WHERE gsf.gene_id = g.id AND gsf.season_id = s.id
        AND gsf.tissue_type = 'Pars tuberalis' AND gsf.study_reference = 'PMID 34414222'
  );

-- [B] TH — HIGH under SD — pars tuberalis — sheep — Xia et al. 2021
INSERT INTO gene_seasonal_function
    (gene_id, season_id, expression_level, functional_role, pathway,
     tissue_type, study_reference, photoperiod_condition, evidence_level)
SELECT g.id, s.id, 'HIGH',
       'SP-induced candidate gene identified by RNA-seq in Sunite ewe pars tuberalis (Xia et al. 2021).',
       'Thyroid-Hormone Seasonal Switch', 'Pars tuberalis', 'PMID 34414222', 'SD',
       'Direct experimental (this study)'
FROM genes g, seasons s
WHERE g.gene_symbol = 'TH' AND s.name = 'Winter'
  AND NOT EXISTS (
      SELECT 1 FROM gene_seasonal_function gsf
      WHERE gsf.gene_id = g.id AND gsf.season_id = s.id
        AND gsf.tissue_type = 'Pars tuberalis' AND gsf.study_reference = 'PMID 34414222'
  );

-- ════════════════════════════════════════════════════════════════
-- Done. Verify with:
--   SELECT g.gene_symbol, gsf.* FROM gene_seasonal_function gsf
--   JOIN genes g ON gsf.gene_id = g.id
--   WHERE gsf.study_reference IN ('PMID 18354476', 'PMID 34414222');
-- ════════════════════════════════════════════════════════════════
