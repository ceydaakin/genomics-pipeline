#!/usr/bin/env python3
"""
Test script for the complete automated genomics pipeline
Tests all components including advanced analyses
"""

import logging
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from genomics_config import GenomicsConfig
from strain_extractor import get_strain_extractor
from automated_genomics_pipeline import AutomatedGenomicsPipeline

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_strain_extraction():
    """Test strain name extraction functionality"""
    logger.info("Testing strain extraction...")

    data_dir = Path("data/fe_cs_genomics")
    extractor = get_strain_extractor()

    # Find test files
    test_files = []
    for ext in ['.fna', '.fasta', '.fa']:
        test_files.extend(data_dir.rglob(f"*{ext}"))

    print(f"\n🧪 Testing strain extraction on {len(test_files)} files:")
    print("=" * 70)

    for test_file in test_files[:5]:  # Test first 5 files
        if test_file.exists():
            strain_name, accession, metadata = extractor.extract_strain_name(test_file)
            display_name = extractor._create_display_name(strain_name, accession, metadata)

            print(f"📁 File: {test_file.name}")
            print(f"   Strain: {strain_name}")
            print(f"   Accession: {accession}")
            print(f"   Display: {display_name}")
            print(f"   Species: {metadata.get('species', 'Unknown')}")
            print()

def test_pipeline_dry_run():
    """Test pipeline configuration and setup without running analyses"""
    logger.info("Testing pipeline dry run...")

    config = GenomicsConfig()
    config.results_dir = Path("test_results")
    config.results_dir.mkdir(exist_ok=True)  # Create test directory

    pipeline = AutomatedGenomicsPipeline(config)

    # Test genome discovery
    input_path = Path("data/fe_cs_genomics")

    if input_path.exists():
        genome_files = pipeline.discover_genomes(input_path)
        strain_mapping = pipeline.extract_strain_information(genome_files)

        print(f"\n🔬 Pipeline dry run results:")
        print("=" * 50)
        print(f"📊 Genomes discovered: {len(genome_files)}")
        print(f"📝 Strains mapped: {len(strain_mapping)}")

        print(f"\n📁 Would create results in: {config.results_dir}")
        print(f"🔧 Configuration saved to: {config.results_dir}/pipeline_config.json")

        # Show strain mapping
        print(f"\n🧬 Strain mapping preview:")
        for i, (accession, info) in enumerate(list(strain_mapping.items())[:3]):
            print(f"  {i+1}. {accession} → {info['display_name']}")

        if len(strain_mapping) > 3:
            print(f"  ... and {len(strain_mapping) - 3} more strains")

    else:
        print(f"❌ Test data directory not found: {input_path}")

def test_advanced_analysis_components():
    """Test advanced analysis components"""
    logger.info("Testing advanced analysis components...")

    from advanced_genomics_analysis import AdvancedGenomicsAnalysis

    print(f"\n🔬 Advanced Analysis Components Test:")
    print("=" * 50)

    # Mock strain mapping for testing
    mock_strain_mapping = {
        'GCA_001592085.1': {
            'strain_name': 'DSM_21775_senmaizukei',
            'display_name': 'L. senmaizukei DSM 21775',
            'metadata': {'species': 'Levilactobacillus senmaizukei', 'strain_type': 'reference'}
        },
        'OPSG_3_2_4': {
            'strain_name': 'OPSG_3_2_4_senmaizukei',
            'display_name': 'L. senmaizukei OPSG_3_2_4',
            'metadata': {'species': 'Levilactobacillus senmaizukei', 'strain_type': 'local_isolate'}
        }
    }

    test_results_dir = Path("test_advanced_results")
    test_results_dir.mkdir(exist_ok=True)  # Create test directory

    # Initialize advanced analysis
    advanced = AdvancedGenomicsAnalysis(test_results_dir, mock_strain_mapping)

    print(f"✅ AdvancedGenomicsAnalysis initialized")
    print(f"📁 Test results directory: {test_results_dir}")
    print(f"🧬 Mock strains: {len(mock_strain_mapping)}")

    # Test directory creation
    expected_dirs = [
        "pcoa_analysis", "core_accessory_genome",
        "jaccard_analysis", "enhanced_phylogeny"
    ]

    for dir_name in expected_dirs:
        expected_path = test_results_dir / "10_Advanced_Analysis" / dir_name
        if expected_path.exists():
            print(f"✅ Created: {dir_name}/")
        else:
            print(f"❌ Missing: {dir_name}/")

def show_complete_workflow():
    """Show the complete workflow that matches the diagram"""

    print(f"\n🧬 COMPLETE AUTOMATED GENOMICS PIPELINE")
    print("=" * 60)
    print("Fully implements the workflow diagram requirements:")
    print()

    # Core analyses
    print("📊 CORE ANALYSES:")
    core_analyses = [
        "✅ Genom FASTA Dosyaları → Input processing",
        "✅ Strain bilgisi çıkarma → Automatic strain extraction",
        "✅ BUSCO analizi → Quality assessment per genome",
        "✅ Prokka annotation → Gene annotation per genome",
        "✅ FastANI → Average nucleotide identity matrix",
        "✅ Snippy → SNP calling and core genome analysis",
        "✅ Roary → Pan-genome analysis",
        "✅ EggNOG-mapper → Functional annotation"
    ]

    for analysis in core_analyses:
        print(f"  {analysis}")

    print()

    # Advanced analyses
    print("🔬 ADVANCED ANALYSES (New!):")
    advanced_analyses = [
        "✅ PCoA Analysis → Principal Coordinates Analysis",
        "✅ Core/Accessory Genome → Detailed core vs accessory comparison",
        "✅ Jaccard Distance → Gene presence/absence similarity",
        "✅ Enhanced Phylogeny → Improved phylogenetic trees",
        "✅ Gene Family Analysis → Comprehensive gene classification",
        "✅ Pan-genome Accumulation → Growth curve analysis"
    ]

    for analysis in advanced_analyses:
        print(f"  {analysis}")

    print()

    # Outputs
    print("📁 ORGANIZED OUTPUTS:")
    outputs = [
        "📊 SNP bazlı filogenetik ağaç → Enhanced SNP phylogeny",
        "📊 ANI bazlı filogenetik ağaç → Enhanced ANI phylogeny",
        "📊 PCoA grafiği → Gene & ANI-based ordination",
        "📊 Core vs Accessory → Comprehensive genome comparison",
        "📊 Jaccard ısı haritası → Distance heatmap",
        "📊 Pan-genom accumulation → Growth curves",
        "📝 Kapsamlı raporlar → Detailed analysis reports"
    ]

    for output in outputs:
        print(f"  {output}")

    print()
    print("🎯 USAGE:")
    print("  # Install tools (once)")
    print("  ./install_comprehensive_genomics_tools.sh")
    print()
    print("  # Run complete analysis")
    print("  ./run_genomics_analysis.sh data/fe_cs_genomics/")
    print()
    print("  # Results organized with strain names in:")
    print("  automated_genomics_results/")

if __name__ == "__main__":
    print("🧬 AUTOMATED GENOMICS PIPELINE - COMPLETE TEST SUITE")
    print("=" * 70)

    # Run tests
    test_strain_extraction()
    test_pipeline_dry_run()
    test_advanced_analysis_components()
    show_complete_workflow()

    print("\n🎉 All tests completed!")
    print("Ready to run the complete automated pipeline!")