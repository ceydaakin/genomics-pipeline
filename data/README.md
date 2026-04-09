# Data Directory

This directory contains the data files required for genomics analysis.

## Directory Structure

```
data/
└── fe_cs_genomics/          # Sample genomics project data
    ├── GCA_*.fna            # GenBank assemblies
    ├── OPSG_*.fna           # Local strains
    └── README.md            # Data usage guide
```

## Supported File Formats

Supported genome file formats:
- `.fna` - FASTA Nucleic Acid
- `.fasta` - Standard FASTA format
- `.fa` - FASTA short extension
- `.fna.gz` - Compressed FASTA

## Adding New Data

To add new genome files to this directory:

1. Place files in appropriate subdirectory
2. Ensure filenames contain accession numbers or strain information
3. The pipeline will automatically extract strain names

## Example Usage

```bash
# Create new dataset
mkdir data/my_project/

# Add genomes
cp *.fna data/my_project/

# Run analysis
./scripts/run_genomics_analysis.sh data/my_project/
```

## Notes

- Genome files are excluded from git repository due to size (.gitignore)
- Add your own genome files to use the pipeline
- Directory structure will be preserved even without genome files