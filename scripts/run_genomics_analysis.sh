#!/bin/bash

# Simple wrapper script for automated genomics pipeline
# Usage: ./run_genomics_analysis.sh [genome_directory]

echo "🧬 Automated Genomics Analysis Pipeline"
echo "======================================"

# Default genome directory
GENOME_DIR="data/fe_cs_genomics"

# Use provided directory if given
if [ $# -eq 1 ]; then
    GENOME_DIR="$1"
fi

echo "Genome directory: $GENOME_DIR"

# Check if directory exists
if [ ! -d "$GENOME_DIR" ]; then
    echo "❌ Error: Genome directory '$GENOME_DIR' does not exist"
    echo ""
    echo "Usage: $0 [genome_directory]"
    echo "Example: $0 data/fe_cs_genomics"
    exit 1
fi

# Check if conda environment is activated
if [[ "$CONDA_DEFAULT_ENV" != "genomics-analysis-complete" ]]; then
    echo "🔧 Activating conda environment: genomics-analysis-complete"
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate genomics-analysis-complete

    if [ $? -ne 0 ]; then
        echo "❌ Error: Could not activate conda environment 'genomics-analysis-complete'"
        echo "Please run: conda activate genomics-analysis-complete"
        exit 1
    fi
fi

# Check if required tools are available
echo "🔍 Checking required tools..."

REQUIRED_TOOLS="busco fastANI snippy roary prokka emapper.py"
MISSING_TOOLS=""

for tool in $REQUIRED_TOOLS; do
    if ! command -v $tool &> /dev/null; then
        MISSING_TOOLS="$MISSING_TOOLS $tool"
    else
        echo "  ✓ $tool found"
    fi
done

if [ ! -z "$MISSING_TOOLS" ]; then
    echo "❌ Missing required tools:$MISSING_TOOLS"
    echo "Please run: ./install_comprehensive_genomics_tools.sh"
    exit 1
fi

echo "✅ All required tools available"
echo ""

# Count genome files
GENOME_COUNT=$(find "$GENOME_DIR" -name "*.fna" -o -name "*.fasta" -o -name "*.fa" | wc -l)
echo "📊 Found $GENOME_COUNT genome files in $GENOME_DIR"

if [ $GENOME_COUNT -eq 0 ]; then
    echo "❌ No genome files found! Please check the directory contains .fna, .fasta, or .fa files"
    exit 1
fi

echo ""
echo "🚀 Starting automated genomics analysis..."
echo "This will run: BUSCO, Prokka, ANI, Snippy, Roary, EggNOG-mapper"
echo ""

# Ask for confirmation
read -p "Continue with analysis? [y/N]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Analysis cancelled"
    exit 0
fi

# Run the pipeline
echo "🔬 Running automated genomics pipeline..."
echo "======================================="

python src/automated_genomics_pipeline.py \
    --input "$GENOME_DIR" \
    --threads 4 \
    --busco-db bacteria_odb10

PIPELINE_EXIT_CODE=$?

echo ""
if [ $PIPELINE_EXIT_CODE -eq 0 ]; then
    echo "🎉 Analysis completed successfully!"
    echo "📁 Results are available in: automated_genomics_results/"
    echo ""
    echo "📊 Summary files:"
    echo "  - automated_genomics_results/09_Final_Reports/comprehensive_genomics_report.md"
    echo "  - automated_genomics_results/09_Final_Reports/strain_summary.csv"
    echo "  - automated_genomics_results/08_Plots_and_Figures/"
    echo ""
    echo "🔬 Analysis directories:"
    echo "  - 01_BUSCO_Quality_Assessment/"
    echo "  - 02_Prokka_Annotation/"
    echo "  - 03_ANI_Analysis/"
    echo "  - 04_Snippy_SNP_Analysis/"
    echo "  - 05_Roary_Pangenome/"
    echo "  - 06_EggNOG_Functional/"
    echo "  - 07_Comparative_Analysis/"
else
    echo "❌ Analysis failed with exit code $PIPELINE_EXIT_CODE"
    echo "Check the log file: automated_genomics_pipeline.log"
    exit $PIPELINE_EXIT_CODE
fi