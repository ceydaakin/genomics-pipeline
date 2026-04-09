# Installation Guide

Detailed installation instructions for the Automated Genomics Pipeline.

## System Requirements

### Operating System
- macOS (Intel/Apple Silicon)
- Linux (Ubuntu 18.04+, CentOS 7+)
- Windows (WSL2 recommended)

### Hardware Requirements
- **Disk Space**: 10+ GB free space
- **Memory**: 8+ GB RAM (16 GB+ recommended)
- **CPU**: 4+ cores recommended for parallel processing

## Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/ceydaakin/genomics-pipeline.git
cd genomics-pipeline
```

## Step 2: Install Conda/Miniconda

If Conda is not installed:

### macOS (Apple Silicon)
```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
bash Miniconda3-latest-MacOSX-arm64.sh
```

### macOS (Intel)
```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
bash Miniconda3-latest-MacOSX-x86_64.sh
```

### Linux
```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

Restart your terminal after installation.

## Step 3: Install Bioinformatics Tools

```bash
# Run the automated installation script
./scripts/install_comprehensive_genomics_tools.sh
```

This script installs:
- BUSCO (genome quality assessment)
- FastANI (ANI analysis)
- Snippy (SNP analysis)
- Roary (pan-genome analysis)
- Prokka (genome annotation)
- EggNOG-mapper (functional annotation)
- IQ-TREE, RAxML (phylogenetic analysis)
- Required Python packages

## Step 4: Activate Environment

```bash
conda activate genomics-analysis-complete
```

## Step 5: Verify Installation

```bash
# Run the test suite
python tests/test_complete_pipeline.py
```

Expected output for successful installation:
```
🧬 AUTOMATED GENOMICS PIPELINE - COMPLETE TEST SUITE
======================================================================
✅ Testing strain extraction...
✅ Pipeline dry run results...
✅ Advanced Analysis Components Test...
✅ All tests completed!
```

## Step 6: Add Your Data

```bash
# Add your genome files to the data directory
cp your_genomes/*.fna data/fe_cs_genomics/
```

## Step 7: Run First Analysis

```bash
# Test with your data
./scripts/run_genomics_analysis.sh
```

## Troubleshooting

### Conda Environment Issues

**Environment not found:**
```bash
# Manually create environment
conda create -n genomics-analysis-complete python=3.9 -y
conda activate genomics-analysis-complete

# Install packages
conda install -c bioconda -c conda-forge busco fastani snippy roary prokka eggnog-mapper -y
```

**Tools not in PATH:**
```bash
# Check environment is active
echo $CONDA_DEFAULT_ENV

# Manual activation
source $(conda info --base)/etc/profile.d/conda.sh
conda activate genomics-analysis-complete
```

### Permission Errors
```bash
# Make scripts executable
chmod +x scripts/*.sh
chmod +x tests/*.py
```

### Disk Space Issues
```bash
# Use custom output directory
python src/automated_genomics_pipeline.py \
    --input data/ \
    --output /path/to/large/disk/results/
```

### Memory Errors
```bash
# Reduce thread count
python src/automated_genomics_pipeline.py \
    --input data/ \
    --threads 2

# Set memory limits
export OMP_NUM_THREADS=2
ulimit -v 4000000  # 4GB limit
```

## Advanced Configuration

### Custom BUSCO Database
```bash
# Use Lactobacillales-specific database
python src/automated_genomics_pipeline.py \
    --input data/ \
    --busco-db lactobacillales_odb10
```

### Configuration Files
```bash
# Save settings
python src/automated_genomics_pipeline.py \
    --input data/ \
    --threads 8 \
    --output custom_results/ \
    --config configs/my_config.json

# Reuse settings
python src/automated_genomics_pipeline.py \
    --config configs/my_config.json
```

## Uninstallation

```bash
# Remove conda environment
conda env remove -n genomics-analysis-complete

# Remove project directory
rm -rf genomics-pipeline/
```

## Getting Help

1. Check log files: `automated_genomics_pipeline.log`
2. Open issues: [GitHub Repository Issues](https://github.com/ceydaakin/genomics-pipeline/issues)
3. Read documentation: Check `docs/` directory
4. Review examples: Check `examples/` directory

## Performance Tips

- Use SSD storage for better I/O performance
- Allocate adequate memory (16GB+ for large datasets)
- Use multiple threads on multi-core systems
- Monitor disk space during analysis