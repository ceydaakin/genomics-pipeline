#!/usr/bin/env python3
"""
Output Organization Utilities
Manages organized output structure with strain names for genomics pipeline results
"""

import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import json
import pandas as pd
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)

class OutputOrganizer:
    """Organize pipeline outputs by strain names and analysis types"""

    def __init__(self, base_results_dir: Path, strain_mapping: Dict):
        self.base_results_dir = Path(base_results_dir)
        self.strain_mapping = strain_mapping
        self.base_results_dir.mkdir(parents=True, exist_ok=True)

        # Create organized structure
        self._create_organized_structure()

    def _create_organized_structure(self):
        """Create organized directory structure by strain and analysis type"""

        # Main analysis directories
        self.analysis_dirs = {
            'busco': self.base_results_dir / '01_BUSCO_Quality_Assessment',
            'prokka': self.base_results_dir / '02_Prokka_Annotation',
            'ani': self.base_results_dir / '03_ANI_Analysis',
            'snippy': self.base_results_dir / '04_Snippy_SNP_Analysis',
            'roary': self.base_results_dir / '05_Roary_Pangenome',
            'eggnog': self.base_results_dir / '06_EggNOG_Functional',
            'comparative': self.base_results_dir / '07_Comparative_Analysis',
            'plots': self.base_results_dir / '08_Plots_and_Figures',
            'reports': self.base_results_dir / '09_Final_Reports'
        }

        # Create main directories
        for analysis_type, directory in self.analysis_dirs.items():
            directory.mkdir(parents=True, exist_ok=True)

        # Create strain-specific subdirectories for individual analyses
        strain_specific_analyses = ['busco', 'prokka', 'eggnog']

        for analysis in strain_specific_analyses:
            strain_dir = self.analysis_dirs[analysis] / 'by_strain'
            strain_dir.mkdir(exist_ok=True)

            for accession, info in self.strain_mapping.items():
                strain_name = info['strain_name']
                strain_subdir = strain_dir / strain_name
                strain_subdir.mkdir(exist_ok=True)

        # Create plot subdirectories
        plot_subdirs = [
            'busco_plots', 'ani_plots', 'snippy_plots',
            'roary_plots', 'comparative_plots', 'summary_plots'
        ]

        for subdir in plot_subdirs:
            (self.analysis_dirs['plots'] / subdir).mkdir(exist_ok=True)

        logger.info("Organized directory structure created")

    def organize_busco_results(self, busco_results: Dict[str, Path]):
        """Organize BUSCO results by strain names"""

        busco_dir = self.analysis_dirs['busco']
        strain_dir = busco_dir / 'by_strain'
        summary_dir = busco_dir / 'summary'
        summary_dir.mkdir(exist_ok=True)

        organized_results = {}

        for accession, result_path in busco_results.items():
            if accession not in self.strain_mapping:
                logger.warning(f"Strain mapping not found for {accession}")
                continue

            strain_info = self.strain_mapping[accession]
            strain_name = strain_info['strain_name']
            display_name = strain_info['display_name']

            # Create strain-specific directory
            strain_result_dir = strain_dir / strain_name
            strain_result_dir.mkdir(exist_ok=True)

            # Copy/move BUSCO results
            if result_path.exists():
                target_dir = strain_result_dir / f"busco_{strain_name}"
                if result_path.is_dir():
                    shutil.copytree(result_path, target_dir, dirs_exist_ok=True)
                else:
                    shutil.copy2(result_path, strain_result_dir)

                organized_results[strain_name] = {
                    'path': target_dir,
                    'display_name': display_name,
                    'accession': accession
                }

        return organized_results

    def organize_prokka_results(self, prokka_results: Dict[str, Path]):
        """Organize Prokka annotation results by strain names"""

        prokka_dir = self.analysis_dirs['prokka']
        strain_dir = prokka_dir / 'by_strain'
        combined_dir = prokka_dir / 'combined_annotations'
        combined_dir.mkdir(exist_ok=True)

        organized_results = {}

        for accession, result_path in prokka_results.items():
            if accession not in self.strain_mapping:
                logger.warning(f"Strain mapping not found for {accession}")
                continue

            strain_info = self.strain_mapping[accession]
            strain_name = strain_info['strain_name']

            # Create strain-specific directory
            strain_result_dir = strain_dir / strain_name
            strain_result_dir.mkdir(exist_ok=True)

            # Copy Prokka results
            if result_path.exists():
                target_dir = strain_result_dir / f"prokka_{strain_name}"
                if result_path.is_dir():
                    shutil.copytree(result_path, target_dir, dirs_exist_ok=True)

                    # Also copy key files to combined directory for downstream analyses
                    key_files = ['*.gff', '*.gbk', '*.faa', '*.ffn']
                    for pattern in key_files:
                        for file in result_path.glob(pattern):
                            new_name = f"{strain_name}_{file.name}"
                            shutil.copy2(file, combined_dir / new_name)

                    organized_results[strain_name] = {
                        'path': target_dir,
                        'gff': target_dir / f"{strain_name}.gff",
                        'accession': accession
                    }

        return organized_results

    def organize_comparative_results(self, ani_results: Optional[Path] = None,
                                   snippy_results: Optional[Path] = None,
                                   roary_results: Optional[Path] = None):
        """Organize comparative analysis results"""

        comp_dir = self.analysis_dirs['comparative']

        # ANI results
        if ani_results and ani_results.exists():
            ani_comp_dir = comp_dir / 'ani_results'
            ani_comp_dir.mkdir(exist_ok=True)
            if ani_results.is_dir():
                shutil.copytree(ani_results, ani_comp_dir / 'original', dirs_exist_ok=True)
            else:
                shutil.copy2(ani_results, ani_comp_dir)

        # Snippy results
        if snippy_results and snippy_results.exists():
            snippy_comp_dir = comp_dir / 'snippy_results'
            snippy_comp_dir.mkdir(exist_ok=True)
            shutil.copytree(snippy_results, snippy_comp_dir / 'core_analysis', dirs_exist_ok=True)

        # Roary results
        if roary_results and roary_results.exists():
            roary_comp_dir = comp_dir / 'roary_results'
            roary_comp_dir.mkdir(exist_ok=True)
            shutil.copytree(roary_results, roary_comp_dir / 'pangenome', dirs_exist_ok=True)

    def organize_plots(self, plot_files: Dict[str, List[Path]]):
        """Organize plot files by analysis type with strain names"""

        plots_dir = self.analysis_dirs['plots']

        for analysis_type, files in plot_files.items():
            analysis_plot_dir = plots_dir / f"{analysis_type}_plots"
            analysis_plot_dir.mkdir(exist_ok=True)

            for plot_file in files:
                if plot_file.exists():
                    # Rename plot with strain names if possible
                    new_name = self._rename_plot_with_strain_names(plot_file.name)
                    target_path = analysis_plot_dir / new_name
                    shutil.copy2(plot_file, target_path)

    def _rename_plot_with_strain_names(self, original_name: str) -> str:
        """Rename plot files to use strain names instead of accession numbers"""

        new_name = original_name

        # Replace accession numbers with strain names in plot filenames
        for accession, strain_info in self.strain_mapping.items():
            if accession in new_name:
                display_name = strain_info['display_name'].replace(' ', '_').replace('.', '_')
                new_name = new_name.replace(accession, display_name)

        return new_name

    def create_analysis_summary(self):
        """Create a comprehensive analysis summary"""

        summary_file = self.analysis_dirs['reports'] / 'analysis_summary.json'

        summary = {
            'analysis_date': datetime.now().isoformat(),
            'total_genomes': len(self.strain_mapping),
            'strain_mapping': self.strain_mapping,
            'directory_structure': {
                analysis: str(path) for analysis, path in self.analysis_dirs.items()
            },
            'analysis_completed': []
        }

        # Check which analyses have been completed
        for analysis_name, analysis_dir in self.analysis_dirs.items():
            if analysis_name in ['plots', 'reports']:
                continue

            if any(analysis_dir.iterdir()):
                summary['analysis_completed'].append(analysis_name)

        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Analysis summary saved to {summary_file}")

    def create_strain_summary_table(self):
        """Create a summary table of all strains"""

        summary_data = []

        for accession, strain_info in self.strain_mapping.items():
            metadata = strain_info['metadata']
            summary_data.append({
                'Accession': accession,
                'Strain_Name': strain_info['strain_name'],
                'Display_Name': strain_info['display_name'],
                'Species': metadata.get('species', 'Unknown'),
                'Strain_Type': metadata.get('strain_type', 'Unknown'),
                'Filename': metadata.get('filename', ''),
                'File_Size_MB': round(metadata.get('file_size', 0) / (1024*1024), 2)
            })

        df = pd.DataFrame(summary_data)
        summary_file = self.analysis_dirs['reports'] / 'strain_summary.csv'
        df.to_csv(summary_file, index=False)

        logger.info(f"Strain summary table saved to {summary_file}")
        return df

    def get_organized_paths(self) -> Dict[str, Path]:
        """Return dictionary of organized analysis paths"""
        return self.analysis_dirs.copy()

    def print_directory_structure(self):
        """Print the organized directory structure"""

        print("\n📁 Organized Results Directory Structure")
        print("=" * 50)

        for analysis_name, analysis_dir in self.analysis_dirs.items():
            print(f"📂 {analysis_name.upper()}: {analysis_dir.name}")
            if analysis_dir.exists():
                # Show subdirectories
                subdirs = [d for d in analysis_dir.iterdir() if d.is_dir()]
                for subdir in subdirs[:3]:  # Show first 3 subdirectories
                    print(f"  └── 📁 {subdir.name}")
                if len(subdirs) > 3:
                    print(f"  └── ... and {len(subdirs) - 3} more directories")

        print(f"\n🗂️ Base results directory: {self.base_results_dir}")
        print(f"📊 Total strains: {len(self.strain_mapping)}")

def create_output_organizer(results_dir: Path, strain_mapping: Dict) -> OutputOrganizer:
    """Factory function to create an output organizer"""
    return OutputOrganizer(results_dir, strain_mapping)