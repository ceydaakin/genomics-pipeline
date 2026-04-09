#!/bin/bash

# Comprehensive Genomics Tools Installation Script
# Installs all tools required for automated genomics pipeline:
# BUSCO, FastANI, Snippy, Roary, Prokka, Eggnog mapper
# For FE_CS Genomics Project - Automated Analysis Pipeline

echo "🧬 Installing Comprehensive Genomics Analysis Tools"
echo "=================================================="
echo "Tools to install: BUSCO, FastANI, Snippy, Roary, Prokka, Eggnog mapper"
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Miniconda or Anaconda first."
    echo "Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Check if mamba is available (faster conda alternative)
if command -v mamba &> /dev/null; then
    CONDA_CMD="mamba"
    echo "🚀 Using mamba for faster installation"
else
    CONDA_CMD="conda"
    echo "📦 Using conda for installation"
fi

# Environment name
ENV_NAME="genomics-analysis-complete"

echo "Creating conda environment: $ENV_NAME"
$CONDA_CMD create -n $ENV_NAME python=3.9 -y

# Activate environment
echo "🔧 Activating environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate $ENV_NAME

# Add required channels
echo "📡 Adding bioconda and conda-forge channels..."
$CONDA_CMD config --add channels defaults
$CONDA_CMD config --add channels bioconda
$CONDA_CMD config --add channels conda-forge
$CONDA_CMD config --set channel_priority strict

echo ""
echo "🧬 Installing core bioinformatics tools..."
echo "=========================================="

# Install BUSCO (genome quality assessment)
echo "📊 Installing BUSCO..."
$CONDA_CMD install busco -y

# Install FastANI (Average Nucleotide Identity)
echo "🧮 Installing FastANI..."
$CONDA_CMD install fastani -y

# Install Snippy (SNP calling and phylogeny)
echo "🔍 Installing Snippy..."
$CONDA_CMD install snippy -y

# Install Roary (pan-genome analysis)
echo "🌐 Installing Roary..."
$CONDA_CMD install roary -y

# Install Prokka (genome annotation)
echo "📝 Installing Prokka..."
$CONDA_CMD install prokka -y

# Install eggNOG-mapper (functional annotation)
echo "🥚 Installing eggNOG-mapper..."
$CONDA_CMD install eggnog-mapper -y

# Install phylogenetic analysis tools
echo "🌳 Installing phylogenetic tools..."
$CONDA_CMD install iqtree raxml fasttree -y

# Install additional sequence analysis tools
echo "🔧 Installing additional tools..."
$CONDA_CMD install blast samtools bedtools bcftools seqtk mafft -y

echo ""
echo "🐍 Installing Python packages..."
echo "================================"

# Install scientific Python packages
$CONDA_CMD install pandas matplotlib seaborn numpy scipy scikit-learn jupyter -y
pip install biopython ete3 plotly

echo ""
echo "🔍 Verifying installations..."
echo "============================"

# Function to check tool installation
check_tool() {
    local tool=$1
    local cmd=$2

    if command -v $tool &> /dev/null; then
        version=$($cmd 2>&1 | head -1)
        echo "✅ $tool: $version"
        return 0
    else
        echo "❌ $tool: NOT FOUND"
        return 1
    fi
}

# Verify all tools
echo "Core analysis tools:"
check_tool "busco" "busco --version"
check_tool "fastANI" "fastANI --version"
check_tool "snippy" "snippy --version"
check_tool "roary" "roary --version"
check_tool "prokka" "prokka --version"
check_tool "emapper.py" "emapper.py --version"

echo ""
echo "Phylogenetic tools:"
check_tool "iqtree" "iqtree --version"
check_tool "raxmlHPC" "raxmlHPC -version"
check_tool "fasttree" "fasttree -help"

echo ""
echo "Sequence analysis tools:"
check_tool "blastn" "blastn -version"
check_tool "samtools" "samtools --version"
check_tool "bedtools" "bedtools --version"

echo ""
echo "🎉 Installation completed!"
echo "========================="

# Download and setup databases
echo ""
echo "📥 Downloading essential databases..."
echo "====================================="

# Create databases directory
mkdir -p ~/genomics_databases

# Download BUSCO databases
echo "📊 Setting up BUSCO databases..."
busco --list-datasets | head -20
echo "Note: BUSCO databases will be downloaded automatically on first use"
echo "Common databases: bacteria_odb10, lactobacillales_odb10"

# Download eggNOG-mapper database
echo "🥚 Downloading eggNOG-mapper database (this may take some time)..."
download_eggnog_data.py

echo ""
echo "🚀 Setup completed successfully!"
echo "==============================="
echo ""
echo "To use the automated genomics pipeline:"
echo "1. Activate the environment: conda activate $ENV_NAME"
echo "2. Run the pipeline: python automated_genomics_pipeline.py --input /path/to/genomes/"
echo ""
echo "Environment name: $ENV_NAME"
echo "All tools are ready for automated genomics analysis!"
echo ""
echo "Next steps:"
echo "- Place your genome files in the data/ directory"
echo "- Run the automated pipeline script"
echo "- Check results in the organized output directories"