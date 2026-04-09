#!/usr/bin/env python3
"""
Automated Genomics Analysis Pipeline
Comprehensive pipeline for bacterial genome analysis including:
- BUSCO (quality assessment)
- ANI (phylogenetic relationships)
- Snippy (SNP analysis)
- Roary (pan-genome analysis)
- Prokka (genome annotation)
- EggNOG-mapper (functional annotation)

Usage:
    python automated_genomics_pipeline.py --input /path/to/genomes [options]
"""

import argparse
import logging
import subprocess
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import traceback
import tempfile

# Import our custom modules
from genomics_config import GenomicsConfig, TOOL_COMMANDS
from strain_extractor import get_strain_extractor
from output_organizer import create_output_organizer
from advanced_genomics_analysis import integrate_advanced_analysis

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('automated_genomics_pipeline.log')
    ]
)
logger = logging.getLogger(__name__)

class AutomatedGenomicsPipeline:
    """Main automated genomics pipeline class"""

    def __init__(self, config: GenomicsConfig):
        self.config = config
        self.strain_extractor = get_strain_extractor()
        self.genome_files = []
        self.strain_mapping = {}
        self.results = {}
        self.organizer = None

        # Set up plotting style
        self._setup_plotting()

    def _setup_plotting(self):
        """Configure plotting parameters"""
        plt.style.use('default')
        sns.set_palette("Set2")
        plt.rcParams.update({
            'figure.figsize': (12, 8),
            'font.size': 11,
            'axes.labelsize': 12,
            'axes.titlesize': 14,
            'legend.fontsize': 10,
            'figure.titlesize': 16
        })

    def discover_genomes(self, input_path: Path) -> List[Path]:
        """Discover genome files in input directory or file"""

        genome_files = []

        if input_path.is_file():
            # Single file provided
            if any(input_path.suffix == ext for ext in self.config.genome_extensions):
                genome_files = [input_path]
        else:
            # Directory provided - search for genome files
            for extension in self.config.genome_extensions:
                genome_files.extend(input_path.rglob(f"*{extension}"))

        logger.info(f"Discovered {len(genome_files)} genome files")
        for gf in genome_files:
            logger.info(f"  - {gf.name}")

        return genome_files

    def extract_strain_information(self, genome_files: List[Path]) -> Dict:
        """Extract strain information for all genome files"""

        logger.info("Extracting strain information...")
        self.strain_mapping = self.strain_extractor.create_strain_mapping(genome_files)

        # Save strain mapping
        mapping_file = self.config.results_dir / 'strain_mapping.json'
        self.strain_extractor.save_strain_mapping(self.strain_mapping, mapping_file)

        return self.strain_mapping

    def setup_output_organization(self):
        """Set up organized output structure"""
        self.organizer = create_output_organizer(self.config.results_dir, self.strain_mapping)
        self.organizer.print_directory_structure()

    def run_busco_analysis(self) -> Dict:
        """Run BUSCO quality assessment on all genomes"""

        logger.info("🔍 Running BUSCO quality assessment...")
        busco_results = {}

        for accession, strain_info in self.strain_mapping.items():
            genome_path = Path(strain_info['filepath'])
            strain_name = strain_info['strain_name']

            logger.info(f"Running BUSCO for {strain_name}")

            # Set up BUSCO output directory
            busco_output = self.config.busco_dir / f"busco_{strain_name}"
            busco_output.mkdir(exist_ok=True)

            try:
                # Run BUSCO command
                cmd = TOOL_COMMANDS['busco']['basic'].format(
                    input=genome_path,
                    database=self.config.busco_database,
                    output=strain_name,
                    threads=self.config.threads
                )

                result = subprocess.run(
                    cmd.split(),
                    cwd=busco_output.parent,
                    capture_output=True,
                    text=True,
                    timeout=1800  # 30 minutes timeout
                )

                if result.returncode == 0:
                    busco_results[accession] = busco_output.parent / strain_name
                    logger.info(f"✓ BUSCO completed for {strain_name}")
                else:
                    logger.error(f"✗ BUSCO failed for {strain_name}: {result.stderr}")

            except subprocess.TimeoutExpired:
                logger.error(f"BUSCO timed out for {strain_name}")
            except Exception as e:
                logger.error(f"BUSCO error for {strain_name}: {e}")

        return busco_results

    def run_prokka_annotation(self) -> Dict:
        """Run Prokka genome annotation"""

        logger.info("📝 Running Prokka genome annotation...")
        prokka_results = {}

        for accession, strain_info in self.strain_mapping.items():
            genome_path = Path(strain_info['filepath'])
            strain_name = strain_info['strain_name']

            logger.info(f"Running Prokka for {strain_name}")

            # Set up Prokka output directory
            prokka_output = self.config.prokka_dir / f"prokka_{strain_name}"
            prokka_output.mkdir(exist_ok=True)

            try:
                # Determine genus for better annotation
                genus = "Levilactobacillus"  # Default for this project
                if 'genus' in strain_info['metadata']:
                    genus = strain_info['metadata']['genus']

                # Run Prokka command
                cmd = TOOL_COMMANDS['prokka']['genus'].format(
                    outdir=prokka_output,
                    prefix=strain_name,
                    genus=genus,
                    threads=self.config.threads,
                    input=genome_path
                )

                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=1800  # 30 minutes timeout
                )

                if result.returncode == 0:
                    prokka_results[accession] = prokka_output
                    logger.info(f"✓ Prokka completed for {strain_name}")
                else:
                    logger.error(f"✗ Prokka failed for {strain_name}: {result.stderr}")

            except subprocess.TimeoutExpired:
                logger.error(f"Prokka timed out for {strain_name}")
            except Exception as e:
                logger.error(f"Prokka error for {strain_name}: {e}")

        return prokka_results

    def run_ani_analysis(self) -> Optional[Path]:
        """Run Average Nucleotide Identity analysis"""

        logger.info("🧮 Running ANI analysis...")

        # Create file lists for FastANI
        query_list = self.config.ani_dir / "query_list.txt"
        ref_list = self.config.ani_dir / "ref_list.txt"

        genome_paths = [Path(info['filepath']) for info in self.strain_mapping.values()]

        # Write genome file lists
        with open(query_list, 'w') as f:
            for path in genome_paths:
                f.write(f"{path}\n")

        with open(ref_list, 'w') as f:
            for path in genome_paths:
                f.write(f"{path}\n")

        # Run FastANI
        ani_output = self.config.ani_dir / "fastani_results.txt"

        try:
            cmd = TOOL_COMMANDS['fastani']['matrix'].format(
                query_list=query_list,
                ref_list=ref_list,
                output=ani_output
            )

            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )

            if result.returncode == 0:
                logger.info("✓ ANI analysis completed")
                return ani_output
            else:
                logger.error(f"✗ ANI analysis failed: {result.stderr}")
                return None

        except Exception as e:
            logger.error(f"ANI analysis error: {e}")
            return None

    def run_snippy_analysis(self, reference_genome: Optional[Path] = None) -> Optional[Path]:
        """Run Snippy SNP analysis"""

        logger.info("🔍 Running Snippy SNP analysis...")

        # Choose reference genome (highest BUSCO score or first genome)
        if reference_genome is None:
            reference_genome = Path(list(self.strain_mapping.values())[0]['filepath'])

        snippy_core_dir = self.config.snippy_dir / "snippy_core"
        snippy_core_dir.mkdir(exist_ok=True)

        # Run Snippy for each genome against reference
        snippy_dirs = []

        for accession, strain_info in self.strain_mapping.items():
            genome_path = Path(strain_info['filepath'])
            strain_name = strain_info['strain_name']

            if genome_path == reference_genome:
                continue  # Skip reference genome

            logger.info(f"Running Snippy for {strain_name}")

            snippy_output = self.config.snippy_dir / f"snippy_{strain_name}"

            try:
                cmd = TOOL_COMMANDS['snippy']['basic'].format(
                    outdir=snippy_output,
                    reference=reference_genome,
                    contigs=genome_path,
                    threads=self.config.threads
                )

                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=1800  # 30 minutes timeout
                )

                if result.returncode == 0:
                    snippy_dirs.append(str(snippy_output))
                    logger.info(f"✓ Snippy completed for {strain_name}")
                else:
                    logger.error(f"✗ Snippy failed for {strain_name}: {result.stderr}")

            except subprocess.TimeoutExpired:
                logger.error(f"Snippy timed out for {strain_name}")
            except Exception as e:
                logger.error(f"Snippy error for {strain_name}: {e}")

        # Run snippy-core to combine results
        if snippy_dirs:
            try:
                cmd = f"snippy-core --ref {reference_genome} {' '.join(snippy_dirs)}"
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=snippy_core_dir,
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    logger.info("✓ Snippy core analysis completed")
                    return snippy_core_dir
                else:
                    logger.error(f"✗ Snippy core failed: {result.stderr}")

            except Exception as e:
                logger.error(f"Snippy core error: {e}")

        return None

    def run_roary_analysis(self, prokka_results: Dict) -> Optional[Path]:
        """Run Roary pan-genome analysis"""

        logger.info("🌐 Running Roary pan-genome analysis...")

        if not prokka_results:
            logger.error("No Prokka results available for Roary analysis")
            return None

        # Collect GFF files from Prokka results
        gff_files = []
        for accession, prokka_dir in prokka_results.items():
            strain_name = self.strain_mapping[accession]['strain_name']
            gff_file = prokka_dir / f"{strain_name}.gff"

            if gff_file.exists():
                gff_files.append(str(gff_file))
            else:
                # Look for any GFF file in the directory
                gff_candidates = list(prokka_dir.glob("*.gff"))
                if gff_candidates:
                    gff_files.append(str(gff_candidates[0]))

        if len(gff_files) < 2:
            logger.error("Need at least 2 GFF files for Roary analysis")
            return None

        roary_output = self.config.roary_dir / "roary_output"

        try:
            cmd = TOOL_COMMANDS['roary']['basic'].format(
                threads=self.config.threads,
                gff_files=' '.join(gff_files)
            )

            # Add output directory to command
            cmd = f"{cmd} -f {roary_output}"

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )

            if result.returncode == 0:
                logger.info("✓ Roary pan-genome analysis completed")
                return roary_output
            else:
                logger.error(f"✗ Roary analysis failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error("Roary analysis timed out")
        except Exception as e:
            logger.error(f"Roary analysis error: {e}")

        return None

    def run_eggnog_analysis(self, prokka_results: Dict) -> Dict:
        """Run EggNOG-mapper functional annotation"""

        logger.info("🥚 Running EggNOG-mapper functional annotation...")
        eggnog_results = {}

        for accession, prokka_dir in prokka_results.items():
            strain_name = self.strain_mapping[accession]['strain_name']

            logger.info(f"Running EggNOG-mapper for {strain_name}")

            # Find protein FASTA file from Prokka
            faa_file = prokka_dir / f"{strain_name}.faa"
            if not faa_file.exists():
                # Look for any FAA file in the directory
                faa_candidates = list(prokka_dir.glob("*.faa"))
                if faa_candidates:
                    faa_file = faa_candidates[0]
                else:
                    logger.warning(f"No protein FASTA file found for {strain_name}")
                    continue

            eggnog_output = self.config.eggnog_dir / f"eggnog_{strain_name}"
            eggnog_output.mkdir(exist_ok=True)

            try:
                cmd = TOOL_COMMANDS['eggnog']['basic'].format(
                    input=faa_file,
                    output_prefix=strain_name,
                    outdir=eggnog_output,
                    threads=self.config.threads
                )

                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=3600  # 1 hour timeout
                )

                if result.returncode == 0:
                    eggnog_results[accession] = eggnog_output
                    logger.info(f"✓ EggNOG-mapper completed for {strain_name}")
                else:
                    logger.error(f"✗ EggNOG-mapper failed for {strain_name}: {result.stderr}")

            except subprocess.TimeoutExpired:
                logger.error(f"EggNOG-mapper timed out for {strain_name}")
            except Exception as e:
                logger.error(f"EggNOG-mapper error for {strain_name}: {e}")

        return eggnog_results

    def generate_comprehensive_plots(self):
        """Generate comprehensive plots with strain names"""

        logger.info("📊 Generating comprehensive plots...")

        plots_dir = self.config.plots_dir
        plots_dir.mkdir(exist_ok=True)

        # Generate strain summary plot
        self._plot_strain_summary()

        # Generate BUSCO summary if available
        if 'busco' in self.results:
            self._plot_busco_summary()

        # Generate ANI heatmap if available
        if 'ani' in self.results:
            self._plot_ani_heatmap()

    def _plot_strain_summary(self):
        """Create strain summary visualization"""

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Genomics Analysis Summary - Strain Overview', fontsize=16)

        # Plot 1: Strain types
        strain_types = [info['metadata'].get('strain_type', 'unknown')
                       for info in self.strain_mapping.values()]
        type_counts = pd.Series(strain_types).value_counts()

        axes[0, 0].pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%')
        axes[0, 0].set_title('Distribution of Strain Types')

        # Plot 2: Species distribution
        species = [info['metadata'].get('species', 'Unknown')
                  for info in self.strain_mapping.values()]
        species_counts = pd.Series(species).value_counts()

        if len(species_counts) > 1:
            axes[0, 1].bar(range(len(species_counts)), species_counts.values)
            axes[0, 1].set_xticks(range(len(species_counts)))
            axes[0, 1].set_xticklabels(species_counts.index, rotation=45)
            axes[0, 1].set_title('Species Distribution')
        else:
            axes[0, 1].text(0.5, 0.5, f'Single species:\n{species_counts.index[0]}',
                          ha='center', va='center', transform=axes[0, 1].transAxes)
            axes[0, 1].set_title('Species Distribution')

        # Plot 3: File sizes
        file_sizes = [info['metadata'].get('file_size', 0) / (1024*1024)
                     for info in self.strain_mapping.values()]
        display_names = [info['display_name'] for info in self.strain_mapping.values()]

        axes[1, 0].bar(range(len(file_sizes)), file_sizes)
        axes[1, 0].set_xticks(range(len(display_names)))
        axes[1, 0].set_xticklabels(display_names, rotation=45, ha='right')
        axes[1, 0].set_ylabel('File Size (MB)')
        axes[1, 0].set_title('Genome File Sizes')

        # Plot 4: Analysis completion status
        completed_analyses = []
        analysis_names = ['BUSCO', 'Prokka', 'ANI', 'Snippy', 'Roary', 'EggNOG']
        for analysis in analysis_names:
            completed_analyses.append(analysis.lower() in self.results)

        colors = ['green' if completed else 'red' for completed in completed_analyses]
        axes[1, 1].bar(analysis_names, [1 if c else 0 for c in completed_analyses], color=colors)
        axes[1, 1].set_ylim(0, 1.2)
        axes[1, 1].set_ylabel('Completed')
        axes[1, 1].set_title('Analysis Completion Status')
        axes[1, 1].set_xticklabels(analysis_names, rotation=45)

        plt.tight_layout()
        plt.savefig(self.config.plots_dir / 'strain_summary.png', dpi=300, bbox_inches='tight')
        plt.close()

        logger.info("✓ Strain summary plot generated")

    def _plot_busco_summary(self):
        """Generate BUSCO summary plots"""
        # This would parse BUSCO results and create quality assessment plots
        logger.info("BUSCO summary plot generation - placeholder")

    def _plot_ani_heatmap(self):
        """Generate ANI heatmap with strain names"""
        # This would parse ANI results and create a heatmap with strain names
        logger.info("ANI heatmap generation - placeholder")

    def generate_final_report(self):
        """Generate final comprehensive report"""

        logger.info("📝 Generating final comprehensive report...")

        report_file = self.config.reports_dir / 'comprehensive_genomics_report.md'

        with open(report_file, 'w') as f:
            f.write("# Comprehensive Genomics Analysis Report\n\n")
            f.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Total Genomes Analyzed:** {len(self.strain_mapping)}\n\n")

            # Strain information
            f.write("## Strain Information\n\n")
            f.write("| Strain Name | Display Name | Species | Type | File Size (MB) |\n")
            f.write("|-------------|--------------|---------|------|-----------------|\n")

            for accession, strain_info in self.strain_mapping.items():
                metadata = strain_info['metadata']
                f.write(f"| {strain_info['strain_name']} | {strain_info['display_name']} | "
                       f"{metadata.get('species', 'Unknown')} | {metadata.get('strain_type', 'Unknown')} | "
                       f"{metadata.get('file_size', 0) / (1024*1024):.1f} |\n")

            # Analysis summary
            f.write("\n## Analysis Summary\n\n")

            # Core analyses
            core_analyses = ['busco', 'prokka', 'ani', 'snippy', 'roary', 'eggnog']
            f.write("### Core Analyses\n")
            for analysis in core_analyses:
                if analysis in self.results:
                    status = "✅ Completed" if self.results[analysis] else "❌ Failed"
                    f.write(f"- **{analysis.upper()}**: {status}\n")

            # Advanced analyses
            if 'advanced' in self.results:
                f.write("\n### Advanced Analyses\n")
                advanced = self.results['advanced']
                pcoa_status = "✅ Completed" if 'pcoa' in advanced and advanced['pcoa'] else "❌ Failed"
                core_acc_status = "✅ Completed" if 'core_accessory' in advanced and advanced['core_accessory'] else "❌ Failed"
                phylo_status = "✅ Completed" if 'enhanced_phylogeny' in advanced and advanced['enhanced_phylogeny'] else "❌ Failed"

                f.write(f"- **PCoA ANALYSIS**: {pcoa_status}\n")
                f.write(f"- **CORE/ACCESSORY GENOME**: {core_acc_status}\n")
                f.write(f"- **ENHANCED PHYLOGENY**: {phylo_status}\n")

            f.write("\n## Results Location\n\n")
            f.write(f"All results are organized in: `{self.config.results_dir}`\n\n")

            # Directory structure
            f.write("### Directory Structure\n\n")
            if self.organizer:
                for analysis_name, analysis_dir in self.organizer.get_organized_paths().items():
                    f.write(f"- **{analysis_name.title()}**: `{analysis_dir.name}/`\n")

            # Advanced analysis directory
            if 'advanced' in self.results:
                f.write(f"- **Advanced Analysis**: `10_Advanced_Analysis/`\n")
                f.write(f"  - PCoA Analysis: `pcoa_analysis/`\n")
                f.write(f"  - Core/Accessory Genome: `core_accessory_genome/`\n")
                f.write(f"  - Jaccard Analysis: `jaccard_analysis/`\n")
                f.write(f"  - Enhanced Phylogeny: `enhanced_phylogeny/`\n")

        logger.info(f"✓ Comprehensive report generated: {report_file}")

    def run_pipeline(self, input_path: Path):
        """Run the complete automated genomics pipeline"""

        logger.info("🧬 Starting Automated Genomics Pipeline")
        logger.info("=" * 50)

        try:
            # Step 1: Discover genome files
            self.genome_files = self.discover_genomes(input_path)
            if not self.genome_files:
                logger.error("No genome files found!")
                return False

            # Step 2: Extract strain information
            self.extract_strain_information(self.genome_files)

            # Step 3: Set up organized output structure
            self.setup_output_organization()

            # Step 4: Save configuration
            self.config.save_config()

            # Step 5: Run analyses
            logger.info("Starting genomics analyses...")

            # BUSCO analysis
            busco_results = self.run_busco_analysis()
            self.results['busco'] = busco_results
            if self.organizer:
                self.organizer.organize_busco_results(busco_results)

            # Prokka annotation
            prokka_results = self.run_prokka_annotation()
            self.results['prokka'] = prokka_results
            if self.organizer:
                self.organizer.organize_prokka_results(prokka_results)

            # ANI analysis
            ani_result = self.run_ani_analysis()
            self.results['ani'] = ani_result

            # Snippy analysis
            snippy_result = self.run_snippy_analysis()
            self.results['snippy'] = snippy_result

            # Roary analysis (requires Prokka results)
            roary_result = self.run_roary_analysis(prokka_results)
            self.results['roary'] = roary_result

            # EggNOG analysis (requires Prokka results)
            eggnog_results = self.run_eggnog_analysis(prokka_results)
            self.results['eggnog'] = eggnog_results

            # Step 6: Organize comparative results
            if self.organizer:
                self.organizer.organize_comparative_results(
                    ani_results=ani_result,
                    snippy_results=snippy_result,
                    roary_results=roary_result
                )

            # Step 7: Generate plots and reports
            self.generate_comprehensive_plots()

            # Step 8: Run advanced analysis (PCoA, Core/Accessory, Enhanced phylogeny)
            logger.info("Running advanced genomics analysis...")
            advanced_results = integrate_advanced_analysis(
                automated_pipeline_results=self.results,
                results_dir=self.config.results_dir,
                strain_mapping=self.strain_mapping
            )
            self.results['advanced'] = advanced_results

            # Step 9: Generate final report
            self.generate_final_report()

            # Step 10: Create final summaries
            if self.organizer:
                self.organizer.create_analysis_summary()
                self.organizer.create_strain_summary_table()

            logger.info("🎉 Automated Genomics Pipeline completed successfully!")
            logger.info("📊 Advanced Analysis Summary:")
            logger.info(f"  - PCoA Analysis: {'✅' if 'pcoa' in advanced_results else '❌'}")
            logger.info(f"  - Core/Accessory Genome: {'✅' if 'core_accessory' in advanced_results else '❌'}")
            logger.info(f"  - Enhanced Phylogeny: {'✅' if 'enhanced_phylogeny' in advanced_results else '❌'}")
            logger.info(f"📁 Results available in: {self.config.results_dir}")

            return True

        except Exception as e:
            logger.error(f"Pipeline failed with error: {e}")
            logger.error(traceback.format_exc())
            return False

def main():
    """Main function for command-line interface"""

    parser = argparse.ArgumentParser(
        description="Automated Genomics Analysis Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze all genomes in a directory
  python automated_genomics_pipeline.py --input /path/to/genomes/

  # Analyze specific genome file
  python automated_genomics_pipeline.py --input genome.fna

  # Use custom output directory and threads
  python automated_genomics_pipeline.py --input genomes/ --output results/ --threads 8
        """
    )

    parser.add_argument(
        '--input', '-i',
        type=Path,
        required=True,
        help='Input directory containing genome files or single genome file'
    )

    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output directory for results (default: automated_genomics_results/)'
    )

    parser.add_argument(
        '--threads', '-t',
        type=int,
        default=4,
        help='Number of threads to use (default: 4)'
    )

    parser.add_argument(
        '--busco-db',
        default='bacteria_odb10',
        help='BUSCO database to use (default: bacteria_odb10)'
    )

    parser.add_argument(
        '--config',
        type=Path,
        help='Load configuration from JSON file'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without running analyses'
    )

    args = parser.parse_args()

    # Check input path
    if not args.input.exists():
        logger.error(f"Input path does not exist: {args.input}")
        sys.exit(1)

    # Load or create configuration
    if args.config and args.config.exists():
        config = GenomicsConfig.load_config(args.config)
        logger.info(f"Loaded configuration from {args.config}")
    else:
        config = GenomicsConfig()

    # Update configuration with command line arguments
    if args.output:
        config.results_dir = args.output
        config.create_directories()

    config.threads = args.threads
    config.busco_database = args.busco_db

    # Create and run pipeline
    pipeline = AutomatedGenomicsPipeline(config)

    if args.dry_run:
        logger.info("DRY RUN MODE - Discovering genomes only...")
        genome_files = pipeline.discover_genomes(args.input)
        strain_mapping = pipeline.extract_strain_information(genome_files)
        pipeline.setup_output_organization()

        logger.info("Pipeline would run the following analyses:")
        analyses = ['BUSCO', 'Prokka', 'ANI', 'Snippy', 'Roary', 'EggNOG']
        for analysis in analyses:
            logger.info(f"  - {analysis}")

        sys.exit(0)

    # Run the full pipeline
    success = pipeline.run_pipeline(args.input)

    if success:
        logger.info("🎉 Pipeline completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Pipeline failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()