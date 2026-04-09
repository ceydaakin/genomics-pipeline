# 🧬 Automated Genomics Analysis Pipeline

A comprehensive automated bacterial genome analysis pipeline that performs quality assessment, phylogenetic analysis, functional annotation, and comparative genomics with publication-ready results.

## ✨ Features

### Core Analyses
- **BUSCO** - Genome quality assessment
- **Prokka** - Genome annotation 
- **FastANI** - Average nucleotide identity analysis
- **Snippy** - SNP calling and phylogenetic analysis
- **Roary** - Pan-genome analysis
- **EggNOG-mapper** - Functional annotation

### Advanced Analyses
- **PCoA** - Principal Coordinates Analysis
- **Core/Accessory Genome** - Comparative genome analysis
- **Jaccard Distance** - Gene presence/absence analysis
- **Enhanced Phylogeny** - ML phylogenetic trees with bootstrap support

### Automation Features
- **Automatic strain name extraction** from FASTA headers
- **Organized output structure** by analysis type and strain
- **Publication-ready plots** with proper strain naming
- **Comprehensive reporting** in multiple formats

## 🚀 Quick Start

### Prerequisites
- macOS or Linux
- Conda/Miniconda
- 8+ GB RAM
- 10+ GB disk space

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ceydaakin/genomics-pipeline.git
cd genomics-pipeline
```

2. **Install bioinformatics tools**
```bash
./scripts/install_comprehensive_genomics_tools.sh
```

3. **Add your genome data**
```bash
# Copy your .fna/.fasta files to the data directory
cp your_genomes/*.fna data/fe_cs_genomics/
```

4. **Run the analysis**
```bash
./scripts/run_genomics_analysis.sh
```

## 📁 Output Structure

Results are automatically organized into a clear directory structure:

```
automated_genomics_results/
├── 01_BUSCO_Quality_Assessment/    # Genome quality metrics
├── 02_Prokka_Annotation/          # Gene annotations by strain
├── 03_ANI_Analysis/               # Phylogenetic relationships  
├── 04_Snippy_SNP_Analysis/        # SNP-based phylogeny
├── 05_Roary_Pangenome/           # Pan-genome analysis
├── 06_EggNOG_Functional/         # Functional annotations
├── 07_Comparative_Analysis/       # Cross-analysis comparisons
├── 08_Plots_and_Figures/         # Publication-ready figures
├── 09_Final_Reports/             # Summary reports and tables
└── 10_Advanced_Analysis/         # PCoA, Jaccard, etc.
```

## 🔧 Advanced Usage

### Command Line Interface

```bash
# Basic usage
python src/automated_genomics_pipeline.py --input data/fe_cs_genomics/

# Custom parameters
python src/automated_genomics_pipeline.py \
    --input /path/to/genomes \
    --output custom_results/ \
    --threads 8 \
    --busco-db lactobacillales_odb10

# Dry run (preview only)
python src/automated_genomics_pipeline.py --input data/ --dry-run
```

### Configuration Files

```bash
# Save settings
python src/automated_genomics_pipeline.py \
    --input data/ \
    --config configs/my_settings.json

# Reuse settings  
python src/automated_genomics_pipeline.py --config configs/my_settings.json
```

## 📄 Supported File Formats

- `.fna` - FASTA Nucleic Acid
- `.fasta` - Standard FASTA format
- `.fa` - FASTA short extension  
- `.fna.gz` - Compressed FASTA

## 📊 Example Results

### Strain Summary Table
| Strain Name | Species | Type | Quality Score |
|-------------|---------|------|---------------|
| L. senmaizukei DSM 21775 | Levilactobacillus senmaizukei | Reference | 95.2% |
| L. senmaizukei OPSG_3_2_4 | Levilactobacillus senmaizukei | Local isolate | 94.8% |

### Analysis Status
- ✅ BUSCO: Completed (15 genomes)
- ✅ Prokka: Completed (15 genomes)  
- ✅ ANI: Completed (105 comparisons)
- ✅ Snippy: Completed (SNP phylogeny)
- ✅ Roary: Completed (pan-genome)
- ✅ EggNOG: Completed (functional annotation)

## 🛠️ Troubleshooting

### Common Issues

**Conda environment not activated**
```bash
conda activate genomics-analysis-complete
```

**Tools not found**
```bash
# Reinstall tools
./scripts/install_comprehensive_genomics_tools.sh
```

**Memory errors**
```bash
# Reduce thread count
--threads 2
```

**Large dataset issues**
```bash
# Use custom output location
--output /path/to/large/disk/results/
```

## 🧪 Testing

```bash
# Run comprehensive tests
python tests/test_complete_pipeline.py

# Test with example data
./scripts/run_genomics_analysis.sh data/fe_cs_genomics/
```

## 📖 Documentation

- [Installation Guide](docs/installation.md) - Detailed setup instructions
- [Examples](examples/) - Usage examples and tutorials
- [Contributing](CONTRIBUTING.md) - How to contribute to the project

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:

- Reporting bugs
- Suggesting enhancements  
- Submitting pull requests
- Development setup

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎓 Citation

If you use this pipeline in your research, please cite:

```
Genomics Analysis Pipeline
https://github.com/ceydaakin/genomics-pipeline
```

## 🆘 Support

- 📫 Open an [Issue](https://github.com/ceydaakin/genomics-pipeline/issues) for bug reports
- 💡 Start a [Discussion](https://github.com/ceydaakin/genomics-pipeline/discussions) for questions
- 📖 Check the [Documentation](docs/) for detailed guides

---

**Built for researchers, by researchers. Making genomics analysis accessible to everyone.** 🧬✨