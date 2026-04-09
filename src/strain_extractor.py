#!/usr/bin/env python3
"""
Strain Name Extraction Utilities
Advanced bacterial strain name extraction from FASTA headers and filenames
"""

import re
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from Bio import SeqIO
from genomics_config import NAMING_PATTERNS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StrainExtractor:
    """Enhanced bacterial strain name extractor"""

    def __init__(self):
        self.strain_patterns = NAMING_PATTERNS['strain_extraction']
        self.accession_patterns = NAMING_PATTERNS['accession']

        # Cache for extracted names to avoid re-processing
        self.name_cache = {}

    def extract_strain_name(self, fasta_file: Path) -> Tuple[str, str, Dict]:
        """
        Extract strain name from FASTA file

        Returns:
            Tuple of (strain_name, accession, metadata)
        """
        fasta_str = str(fasta_file)

        # Check cache first
        if fasta_str in self.name_cache:
            return self.name_cache[fasta_str]

        try:
            with open(fasta_file, 'r') as f:
                first_line = f.readline().strip()

            logger.info(f"Processing: {fasta_file.name}")
            logger.debug(f"Header: {first_line}")

            # Extract strain name and accession
            strain_name = self._extract_strain_from_header(first_line, fasta_file.name)
            accession = self._extract_accession(first_line, fasta_file.name)

            # Generate metadata
            metadata = self._generate_metadata(first_line, fasta_file, strain_name, accession)

            # Cache result
            result = (strain_name, accession, metadata)
            self.name_cache[fasta_str] = result

            logger.info(f"✓ Strain: {strain_name}, Accession: {accession}")
            return result

        except Exception as e:
            logger.error(f"Error processing {fasta_file}: {e}")
            fallback_name = f"Unknown_{fasta_file.stem}"
            fallback_accession = fasta_file.stem
            fallback_metadata = {'source': 'error', 'filename': fasta_file.name}

            result = (fallback_name, fallback_accession, fallback_metadata)
            self.name_cache[fasta_str] = result
            return result

    def _extract_strain_from_header(self, header: str, filename: str) -> str:
        """Extract strain name from FASTA header"""

        # Handle special cases first
        if "OPSG_3_2_4" in header or "OPSG_3_2_4" in filename:
            return "OPSG_3_2_4_senmaizukei"

        if "DSM" in header and "21775" in header:
            return "DSM_21775_senmaizukei"

        # Try standard patterns
        for i, pattern in enumerate(self.strain_patterns):
            match = re.search(pattern, header)
            if match:
                strain = match.group(1).strip()
                # Clean up the strain name
                strain = re.sub(r'\s+', '_', strain)  # Replace spaces with underscores
                strain = re.sub(r'[^\w\-_]', '', strain)  # Remove special characters
                logger.debug(f"Found strain with pattern {i+1}: {strain}")
                return strain

        # Try to extract from filename if header parsing fails
        strain_from_filename = self._extract_strain_from_filename(filename)
        if strain_from_filename:
            return strain_from_filename

        # Fallback: try to get any bacterial-looking names
        fallback_matches = re.findall(r'([A-Z][a-z]+(?:bacterium|bacillus|coccus|lactobacillus))', header)
        if fallback_matches:
            return f"{fallback_matches[0]}_strain"

        return "Unknown_strain"

    def _extract_strain_from_filename(self, filename: str) -> Optional[str]:
        """Extract strain information from filename"""

        # Remove common extensions
        name = filename.replace('.fna', '').replace('.fasta', '').replace('.fa', '').replace('.gz', '')

        # Look for strain patterns in filename
        patterns = [
            r'GCA_(\d+)\.(\d+)_([^_]+)',  # GCA_123.1_StrainName
            r'(OPSG_\d+_\d+_\d+)',        # OPSG patterns
            r'([A-Z][a-z]+_[a-z]+)_(.+)', # Genus_species_strain
            r'DSM[_\-]?(\d+)',            # DSM strain numbers
        ]

        for pattern in patterns:
            match = re.search(pattern, name)
            if match:
                if 'OPSG' in pattern:
                    return f"{match.group(1)}_local_isolate"
                elif 'DSM' in pattern:
                    return f"DSM_{match.group(1)}"
                else:
                    groups = match.groups()
                    return '_'.join(groups).replace(' ', '_')

        return None

    def _extract_accession(self, header: str, filename: str) -> str:
        """Extract accession number from header or filename"""

        # Try header first
        for pattern in self.accession_patterns:
            match = re.search(pattern, header)
            if match:
                return match.group(1)

        # Try filename
        for pattern in self.accession_patterns:
            match = re.search(pattern, filename)
            if match:
                return match.group(1)

        # Fallback to filename stem
        return Path(filename).stem

    def _generate_metadata(self, header: str, fasta_file: Path, strain_name: str, accession: str) -> Dict:
        """Generate metadata for the strain"""

        metadata = {
            'filename': fasta_file.name,
            'filepath': str(fasta_file),
            'header': header,
            'strain_name': strain_name,
            'accession': accession,
            'file_size': fasta_file.stat().st_size if fasta_file.exists() else 0,
        }

        # Try to extract additional information
        if 'senmaizukei' in header.lower():
            metadata['species'] = 'Levilactobacillus senmaizukei'
        elif 'parabrevis' in header.lower():
            metadata['species'] = 'Levilactobacillus parabrevis'
        elif 'lactobacillus' in header.lower():
            metadata['genus'] = 'Lactobacillus'
        elif 'levilactobacillus' in header.lower():
            metadata['genus'] = 'Levilactobacillus'

        # Check for strain/isolate type indicators
        if 'DSM' in header:
            metadata['strain_type'] = 'reference'
            metadata['culture_collection'] = 'DSM'
        elif 'OPSG' in header or 'local' in strain_name.lower():
            metadata['strain_type'] = 'local_isolate'
        else:
            metadata['strain_type'] = 'unknown'

        return metadata

    def create_strain_mapping(self, genome_files: List[Path]) -> Dict[str, Dict]:
        """
        Create a comprehensive mapping of strain information for all genome files

        Returns:
            Dict with structure: {accession: {strain_name, metadata, filepath}}
        """
        strain_mapping = {}

        logger.info(f"Creating strain mapping for {len(genome_files)} genomes")

        for genome_file in genome_files:
            strain_name, accession, metadata = self.extract_strain_name(genome_file)

            strain_mapping[accession] = {
                'strain_name': strain_name,
                'accession': accession,
                'metadata': metadata,
                'filepath': str(genome_file),
                'display_name': self._create_display_name(strain_name, accession, metadata)
            }

        return strain_mapping

    def _create_display_name(self, strain_name: str, accession: str, metadata: Dict) -> str:
        """Create a display-friendly name for plots and reports"""

        # If we have species info, create a nice display name
        if 'species' in metadata:
            species = metadata['species']
            if 'senmaizukei' in species:
                if 'OPSG' in strain_name:
                    return "L. senmaizukei OPSG_3_2_4"
                elif 'DSM' in strain_name:
                    return "L. senmaizukei DSM 21775"
                else:
                    return f"L. senmaizukei {strain_name}"
            elif 'parabrevis' in species:
                if 'DSM' in strain_name:
                    return f"L. parabrevis {strain_name}"
                else:
                    return f"L. parabrevis {accession}"

        # Fallback to cleaned strain name
        clean_name = strain_name.replace('_', ' ').title()
        return clean_name if clean_name != "Unknown Strain" else accession

    def save_strain_mapping(self, strain_mapping: Dict, output_file: Path):
        """Save strain mapping to JSON file for reference"""
        import json

        with open(output_file, 'w') as f:
            json.dump(strain_mapping, f, indent=2)

        logger.info(f"Strain mapping saved to {output_file}")

def get_strain_extractor() -> StrainExtractor:
    """Factory function to get a configured strain extractor"""
    return StrainExtractor()

def test_strain_extraction():
    """Test strain extraction on available genome files"""

    data_dir = Path("/Users/ceydaakin/genomics-pipeline/data/fe_cs_genomics")
    extractor = get_strain_extractor()

    # Find all genome files
    genome_files = []
    for ext in ['.fna', '.fasta', '.fa']:
        genome_files.extend(data_dir.rglob(f"*{ext}"))

    print(f"Testing strain extraction on {len(genome_files)} files")
    print("=" * 60)

    for genome_file in genome_files[:5]:  # Test first 5 files
        strain_name, accession, metadata = extractor.extract_strain_name(genome_file)
        print(f"File: {genome_file.name}")
        print(f"Strain: {strain_name}")
        print(f"Accession: {accession}")
        print(f"Display: {extractor._create_display_name(strain_name, accession, metadata)}")
        print()

if __name__ == "__main__":
    test_strain_extraction()