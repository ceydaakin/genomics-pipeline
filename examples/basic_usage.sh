#!/bin/bash

# Basic Usage Examples for Genomics Pipeline
# This script shows common usage patterns

echo "🧬 Genomics Pipeline - Basic Usage Examples"
echo "==========================================="

# Example 1: Quick analysis with default settings
echo ""
echo "📊 Example 1: Quick analysis with default data"
echo "----------------------------------------------"
echo "# Run analysis with FE_CS genomics data"
echo "./scripts/run_genomics_analysis.sh"
echo ""

# Example 2: Custom data directory
echo "📂 Example 2: Analysis with custom data directory"
echo "------------------------------------------------"
echo "# Analyze genomes in custom directory"
echo "./scripts/run_genomics_analysis.sh /path/to/your/genomes/"
echo ""

# Example 3: Python script direct usage
echo "🐍 Example 3: Direct Python script usage"
echo "----------------------------------------"
echo "# Basic usage"
echo "python src/automated_genomics_pipeline.py --input data/fe_cs_genomics/"
echo ""
echo "# With custom parameters"
echo "python src/automated_genomics_pipeline.py \\"
echo "    --input data/fe_cs_genomics/ \\"
echo "    --output custom_results/ \\"
echo "    --threads 8 \\"
echo "    --busco-db lactobacillales_odb10"
echo ""

# Example 4: Dry run
echo "🔍 Example 4: Dry run (preview only)"
echo "-----------------------------------"
echo "# See what would be done without running analysis"
echo "python src/automated_genomics_pipeline.py --input data/ --dry-run"
echo ""

# Example 5: Configuration file usage
echo "⚙️ Example 5: Using configuration files"
echo "--------------------------------------"
echo "# Save configuration"
echo "python src/automated_genomics_pipeline.py \\"
echo "    --input data/ \\"
echo "    --output results/ \\"
echo "    --threads 4 \\"
echo "    --config configs/my_settings.json"
echo ""
echo "# Reuse saved configuration"
echo "python src/automated_genomics_pipeline.py --config configs/my_settings.json"
echo ""

# Example 6: Testing
echo "🧪 Example 6: Testing the pipeline"
echo "---------------------------------"
echo "# Run comprehensive tests"
echo "python tests/test_complete_pipeline.py"
echo ""

echo "💡 Tips:"
echo "- Always activate conda environment first: conda activate genomics-analysis-complete"
echo "- Check logs in automated_genomics_pipeline.log for troubleshooting"
echo "- Results are organized by analysis type and strain name"
echo "- Use --help for full list of options"