#!/usr/bin/env python3
"""
Genomics Pipeline Configuration
Defines settings, paths, and parameters for automated genomics analysis
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json

@dataclass
class GenomicsConfig:
    """Main configuration class for genomics pipeline"""

    # Base directories
    base_dir: Path = Path("/Users/ceydaakin/genomics-pipeline")
    data_dir: Path = field(init=False)
    results_dir: Path = field(init=False)

    # Analysis output directories
    busco_dir: Path = field(init=False)
    ani_dir: Path = field(init=False)
    snippy_dir: Path = field(init=False)
    roary_dir: Path = field(init=False)
    prokka_dir: Path = field(init=False)
    eggnog_dir: Path = field(init=False)
    plots_dir: Path = field(init=False)
    reports_dir: Path = field(init=False)

    # Tool parameters
    busco_database: str = "bacteria_odb10"
    busco_alt_database: str = "lactobacillales_odb10"
    ani_threshold: float = 95.0  # ANI threshold for same species
    threads: int = 4

    # File patterns
    genome_extensions: List[str] = field(default_factory=lambda: ['.fna', '.fasta', '.fa', '.fna.gz'])

    # Output naming
    use_strain_names: bool = True  # Use extracted strain names instead of accessions
    strain_names_in_plots: bool = True  # Replace accession numbers with strain names in plots

    def __post_init__(self):
        """Set up derived paths after initialization"""
        self.data_dir = self.base_dir / "data" / "fe_cs_genomics"
        self.results_dir = self.base_dir / "automated_genomics_results"

        # Analysis subdirectories
        self.busco_dir = self.results_dir / "busco_analysis"
        self.ani_dir = self.results_dir / "ani_analysis"
        self.snippy_dir = self.results_dir / "snippy_analysis"
        self.roary_dir = self.results_dir / "roary_analysis"
        self.prokka_dir = self.results_dir / "prokka_analysis"
        self.eggnog_dir = self.results_dir / "eggnog_analysis"
        self.plots_dir = self.results_dir / "plots"
        self.reports_dir = self.results_dir / "reports"

        # Create all directories
        self.create_directories()

    def create_directories(self):
        """Create all required directories"""
        dirs_to_create = [
            self.results_dir, self.busco_dir, self.ani_dir,
            self.snippy_dir, self.roary_dir, self.prokka_dir,
            self.eggnog_dir, self.plots_dir, self.reports_dir
        ]

        for directory in dirs_to_create:
            directory.mkdir(parents=True, exist_ok=True)

    def save_config(self, filepath: Optional[Path] = None):
        """Save configuration to JSON file"""
        if filepath is None:
            filepath = self.results_dir / "pipeline_config.json"

        config_dict = {
            'base_dir': str(self.base_dir),
            'data_dir': str(self.data_dir),
            'results_dir': str(self.results_dir),
            'busco_database': self.busco_database,
            'busco_alt_database': self.busco_alt_database,
            'ani_threshold': self.ani_threshold,
            'threads': self.threads,
            'genome_extensions': self.genome_extensions,
            'use_strain_names': self.use_strain_names,
            'strain_names_in_plots': self.strain_names_in_plots
        }

        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)

    @classmethod
    def load_config(cls, filepath: Path):
        """Load configuration from JSON file"""
        with open(filepath, 'r') as f:
            config_dict = json.load(f)

        config = cls(base_dir=Path(config_dict['base_dir']))

        # Update with loaded values
        for key, value in config_dict.items():
            if hasattr(config, key) and key != 'base_dir':
                setattr(config, key, value)

        return config

# Tool command templates
TOOL_COMMANDS = {
    'busco': {
        'basic': "busco -i {input} -l {database} -o {output} -m genome --cpu {threads}",
        'force': "busco -i {input} -l {database} -o {output} -m genome --cpu {threads} --force"
    },
    'fastani': {
        'pairwise': "fastANI -q {query} -r {reference} -o {output}",
        'matrix': "fastANI --ql {query_list} --rl {ref_list} -o {output} --matrix"
    },
    'snippy': {
        'basic': "snippy --outdir {outdir} --ref {reference} --ctgs {contigs} --cpus {threads}",
        'cleanup': "snippy-clean_full_aln {core_aln} > {clean_aln}"
    },
    'prokka': {
        'basic': "prokka --outdir {outdir} --prefix {prefix} --cpus {threads} {input}",
        'genus': "prokka --outdir {outdir} --prefix {prefix} --genus {genus} --cpus {threads} {input}"
    },
    'roary': {
        'basic': "roary -p {threads} -e -n -v {gff_files}",
        'fast': "roary -p {threads} -e -n -v -i 90 {gff_files}"
    },
    'eggnog': {
        'basic': "emapper.py -i {input} -o {output_prefix} --output_dir {outdir} --cpu {threads}",
        'diamond': "emapper.py -i {input} -o {output_prefix} --output_dir {outdir} --cpu {threads} --data_dir {data_dir}"
    }
}

# Database information
DATABASES = {
    'busco': {
        'bacteria': 'bacteria_odb10',
        'lactobacillales': 'lactobacillales_odb10',
        'bacilli': 'bacilli_odb10'
    },
    'eggnog': {
        'data_dir': '~/eggnog_data',
        'database': 'eggnog.db'
    }
}

# File naming patterns
NAMING_PATTERNS = {
    'strain_extraction': [
        r'>\w+\.\d+\s+([A-Z][a-z]+ [a-z]+)',  # Standard: >GCA_123.1 Genus species
        r'>[A-Z0-9_\.]+\s+([A-Z][a-z]+\s+[a-z]+)',  # Alternative format
        r'(Levilactobacillus\s+\w+|Lactobacillus\s+\w+)',  # Specific genera
        r'([A-Z][a-z]+\s+[a-z]+)',  # Generic genus species
    ],
    'accession': [
        r'(GCA_\d+\.\d+)',  # GenBank assembly accession
        r'(OPSG_\d+_\d+_\d+)',  # Custom local isolate ID
        r'([A-Z]+_\d+)',  # Simple accession pattern
    ]
}