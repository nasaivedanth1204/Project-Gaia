# eDNA Datasets

This directory contains all datasets and reference databases used in the project **"AI-Based Taxonomy Identification and Biodiversity Assessment from eDNA Datasets."**

## Folder Structure

```
data/
│
├── accessions.txt          # SRA run accessions (manifest, tracked in git)
├── .gitignore              # keeps the large files below out of git
│
├── raw/
│   ├── SRR17137384.fastq
│   ├── SRR37879006.fastq
│   ├── SRR38080555.fastq
│   ├── SRR39683131.fastq
│   ├── SRR39742893.fastq
│   ├── SRR39848019.fastq
│   ├── SRR39993450.fastq
│   └── SRR39993451.fastq
│
├── references/
│   ├── BOLD_Public.fasta
│   ├── mitofishdb.fa
│   ├── SILVA.fasta
│   └── UNITE.fasta
│
├── taxonomy/
│   ├── names.dmp
│   ├── nodes.dmp
│   └── merged.dmp
│
└── metadata/
    └── SRA_RunInfo.xlsx
```

---

## Folder Description

### raw/

Contains raw environmental DNA (eDNA) sequencing datasets downloaded from the NCBI Sequence Read Archive (SRA).

**File Format**

- FASTQ
- FASTQ.GZ

These files are the primary input for taxonomy identification and biodiversity analysis.

---

### references/

Contains reference databases used for taxonomic classification.

| Database | Purpose |
|----------|---------|
| BOLD | Animal COI reference sequences |
| SILVA | 16S/18S rRNA reference database |
| MitoFish | Fish mitochondrial reference database |
| UNITE | Fungal ITS reference database |

---

### taxonomy/

Contains taxonomy files downloaded from the NCBI Taxonomy database.

| File | Description |
|------|-------------|
| names.dmp | Scientific names |
| nodes.dmp | Taxonomic hierarchy |
| merged.dmp | Merged taxonomy IDs |

These files are required for mapping sequence classifications to biological taxonomy.

---

### metadata/

Contains metadata associated with each sequencing run.

Example information includes:

- Run ID
- BioProject
- BioSample
- Organism
- Sequencing Platform
- Instrument
- Library Strategy
- Library Layout
- Number of Reads
- Number of Bases
- Publication Date

---

## Data Sources

- NCBI Sequence Read Archive (SRA)
- NCBI Taxonomy
- BOLD Systems
- SILVA Database
- MitoFish
- UNITE Database

---

## Workflow

```
Raw FASTQ Files
        │
        ▼
Quality Control
        │
        ▼
Sequence Filtering
        │
        ▼
Taxonomic Classification
        │
        ▼
Biodiversity Assessment
        │
        ▼
Machine Learning Analysis
        │
        ▼
Visualization Dashboard
```

---

## Note

Large datasets and reference databases may exceed GitHub's file size limits. For public repositories, it is recommended to exclude large files using `.gitignore` and provide download instructions in the main project README.

### Status of this directory

That recommendation is now enforced by `data/.gitignore`, which excludes
`raw/`, `references/`, `taxonomy/`, and common sequence formats. GitHub
hard-rejects any file over 100 MB, and git retains every version of a
file forever — so a large file committed once bloats the repository
permanently, even after deletion.

**Tracked here:** `accessions.txt`, `metadata/`, and this README.
**Not tracked:** everything under `raw/`, `references/`, and `taxonomy/` —
download those to your local disk before running the pipeline.
