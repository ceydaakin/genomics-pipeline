# Sample Genomics Data Directory

Place your genome files in this directory for analysis.

## Supported Formats
- `.fna` - FASTA Nucleic Acid
- `.fasta` - Standard FASTA format
- `.fa` - FASTA short extension
- `.fna.gz` - Compressed FASTA

## Example File Structure
```
fe_cs_genomics/
├── GCA_001592085.1_ASM159208v1_genomic.fna
├── OPSG_3_2_4_genomic.fna
├── GCA_000383435.1_ASM38343v1_genomic.fna
└── [other genome files...]
```

## Usage
```bash
# Copy genome files to this directory
cp *.fna data/fe_cs_genomics/

# Run the analysis
./scripts/run_genomics_analysis.sh
```

**Note:** Genome files are excluded from the repository due to file size (.gitignore). 
You need to add your own genome files to this directory to use the pipeline.