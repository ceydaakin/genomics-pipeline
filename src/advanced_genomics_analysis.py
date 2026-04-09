#!/usr/bin/env python3
"""
Advanced Genomics Analysis Module
Implements missing components from the workflow diagram:
- PCoA (Principal Coordinates Analysis)
- Core vs Accessory genome analysis
- Jaccard distance analysis
- Enhanced phylogenetic tree building
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.decomposition import PCA
from sklearn.manifold import MDS
from sklearn.metrics import jaccard_score
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import pdist, squareform
import subprocess
import logging
from typing import Dict, List, Tuple, Optional
from Bio import Phylo
from io import StringIO

# Setup logging
logger = logging.getLogger(__name__)

class AdvancedGenomicsAnalysis:
    """Advanced genomics analysis for completing the workflow diagram requirements"""

    def __init__(self, results_dir: Path, strain_mapping: Dict):
        self.results_dir = Path(results_dir)
        self.strain_mapping = strain_mapping
        self.advanced_dir = self.results_dir / "10_Advanced_Analysis"
        self.advanced_dir.mkdir(exist_ok=True, parents=True)

        # Create subdirectories
        self.pcoa_dir = self.advanced_dir / "pcoa_analysis"
        self.core_accessory_dir = self.advanced_dir / "core_accessory_genome"
        self.jaccard_dir = self.advanced_dir / "jaccard_analysis"
        self.phylo_dir = self.advanced_dir / "enhanced_phylogeny"

        for directory in [self.pcoa_dir, self.core_accessory_dir, self.jaccard_dir, self.phylo_dir]:
            directory.mkdir(exist_ok=True)

    def run_pcoa_analysis(self, roary_results: Optional[Path] = None,
                         ani_results: Optional[Path] = None) -> Dict:
        """
        Principal Coordinates Analysis (PCoA)
        Creates ordination based on gene presence/absence and ANI distances
        """
        logger.info("🔍 Running PCoA analysis...")

        pcoa_results = {}

        # PCoA based on gene presence/absence (from Roary)
        if roary_results and roary_results.exists():
            pcoa_results['gene_based'] = self._pcoa_from_roary(roary_results)

        # PCoA based on ANI distances
        if ani_results and ani_results.exists():
            pcoa_results['ani_based'] = self._pcoa_from_ani(ani_results)

        return pcoa_results

    def _pcoa_from_roary(self, roary_results: Path) -> Dict:
        """PCoA analysis from Roary gene presence/absence matrix"""

        # Look for gene presence/absence file
        gene_presence_file = roary_results / "gene_presence_absence.csv"

        if not gene_presence_file.exists():
            logger.warning("Gene presence/absence file not found in Roary results")
            return {}

        try:
            # Read gene presence/absence matrix
            df = pd.read_csv(gene_presence_file, low_memory=False)

            # Extract strain columns (skip annotation columns)
            strain_columns = [col for col in df.columns if col not in
                            ['Gene', 'Non-unique Gene name', 'Annotation', 'No. isolates', 'No. sequences']]

            # Create binary matrix (1 = gene present, 0 = gene absent)
            gene_matrix = df[strain_columns].copy()
            gene_matrix = gene_matrix.fillna(0)  # NaN = absent
            gene_matrix = (gene_matrix != 0).astype(int)  # Convert to binary

            # Transpose so rows = strains, columns = genes
            gene_matrix = gene_matrix.T

            # Calculate Jaccard distances
            jaccard_distances = []
            strain_names = gene_matrix.index.tolist()

            for i in range(len(strain_names)):
                row_distances = []
                for j in range(len(strain_names)):
                    if i == j:
                        distance = 0.0
                    else:
                        # Jaccard distance = 1 - Jaccard similarity
                        intersection = np.sum(gene_matrix.iloc[i] & gene_matrix.iloc[j])
                        union = np.sum(gene_matrix.iloc[i] | gene_matrix.iloc[j])
                        jaccard_sim = intersection / union if union > 0 else 0
                        distance = 1 - jaccard_sim
                    row_distances.append(distance)
                jaccard_distances.append(row_distances)

            jaccard_matrix = np.array(jaccard_distances)

            # Perform classical MDS (equivalent to PCoA)
            mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
            pcoa_coords = mds.fit_transform(jaccard_matrix)

            # Create results dataframe
            pcoa_df = pd.DataFrame(pcoa_coords, columns=['PCoA1', 'PCoA2'])
            pcoa_df.index = strain_names

            # Map to display names
            display_names = []
            for strain in strain_names:
                # Find corresponding strain in mapping
                display_name = strain  # fallback
                for accession, info in self.strain_mapping.items():
                    if strain in info['strain_name'] or strain in accession:
                        display_name = info['display_name']
                        break
                display_names.append(display_name)

            pcoa_df['Display_Name'] = display_names

            # Save results
            pcoa_df.to_csv(self.pcoa_dir / "pcoa_gene_based_coordinates.csv")

            # Create PCoA plot
            self._plot_pcoa(pcoa_df, "Gene Presence/Absence Based PCoA",
                          self.pcoa_dir / "pcoa_gene_based.png")

            # Save Jaccard distance matrix
            jaccard_df = pd.DataFrame(jaccard_matrix, index=strain_names, columns=strain_names)
            jaccard_df.to_csv(self.jaccard_dir / "jaccard_distance_matrix.csv")

            # Create Jaccard heatmap
            self._plot_jaccard_heatmap(jaccard_df, display_names)

            logger.info("✓ Gene-based PCoA analysis completed")

            return {
                'coordinates': pcoa_df,
                'jaccard_matrix': jaccard_df,
                'explained_variance': mds.stress_
            }

        except Exception as e:
            logger.error(f"Error in gene-based PCoA: {e}")
            return {}

    def _pcoa_from_ani(self, ani_results: Path) -> Dict:
        """PCoA analysis from ANI distance matrix"""

        try:
            # Read ANI results
            ani_df = pd.read_csv(ani_results, sep='\t', header=None,
                               names=['query', 'reference', 'ani', 'fragments', 'total_fragments'])

            # Get unique genome names
            genomes = list(set(ani_df['query'].tolist() + ani_df['reference'].tolist()))

            # Create symmetric ANI matrix
            ani_matrix = np.eye(len(genomes)) * 100  # Diagonal = 100% identity

            for _, row in ani_df.iterrows():
                query_idx = genomes.index(row['query'])
                ref_idx = genomes.index(row['reference'])
                ani_matrix[query_idx, ref_idx] = row['ani']
                ani_matrix[ref_idx, query_idx] = row['ani']  # Make symmetric

            # Convert ANI to distance (100 - ANI)
            distance_matrix = 100 - ani_matrix

            # Perform classical MDS (PCoA)
            mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
            pcoa_coords = mds.fit_transform(distance_matrix)

            # Create results dataframe
            pcoa_df = pd.DataFrame(pcoa_coords, columns=['PCoA1', 'PCoA2'])
            pcoa_df.index = genomes

            # Map to display names
            display_names = []
            for genome in genomes:
                display_name = genome  # fallback
                genome_basename = Path(genome).name
                for accession, info in self.strain_mapping.items():
                    if (accession in genome_basename or
                        info['strain_name'] in genome_basename or
                        any(part in genome_basename for part in accession.split('_'))):
                        display_name = info['display_name']
                        break
                display_names.append(display_name)

            pcoa_df['Display_Name'] = display_names

            # Save results
            pcoa_df.to_csv(self.pcoa_dir / "pcoa_ani_based_coordinates.csv")

            # Create PCoA plot
            self._plot_pcoa(pcoa_df, "ANI Distance Based PCoA",
                          self.pcoa_dir / "pcoa_ani_based.png")

            logger.info("✓ ANI-based PCoA analysis completed")

            return {
                'coordinates': pcoa_df,
                'ani_matrix': pd.DataFrame(ani_matrix, index=genomes, columns=genomes),
                'explained_variance': mds.stress_
            }

        except Exception as e:
            logger.error(f"Error in ANI-based PCoA: {e}")
            return {}

    def _plot_pcoa(self, pcoa_df: pd.DataFrame, title: str, output_path: Path):
        """Create PCoA visualization"""

        plt.figure(figsize=(12, 8))

        # Create scatter plot
        scatter = plt.scatter(pcoa_df['PCoA1'], pcoa_df['PCoA2'],
                            s=100, alpha=0.7, c=range(len(pcoa_df)),
                            cmap='Set3', edgecolors='black', linewidth=0.5)

        # Add labels
        for i, (idx, row) in enumerate(pcoa_df.iterrows()):
            plt.annotate(row['Display_Name'],
                        (row['PCoA1'], row['PCoA2']),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=9, ha='left', va='bottom',
                        bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7))

        plt.xlabel('PCoA Axis 1')
        plt.ylabel('PCoA Axis 2')
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)

        # Add strain type legend if available
        strain_types = set()
        for accession, info in self.strain_mapping.items():
            strain_type = info['metadata'].get('strain_type', 'unknown')
            strain_types.add(strain_type)

        if len(strain_types) > 1:
            # Color by strain type
            colors = {}
            color_map = plt.cm.Set3(np.linspace(0, 1, len(strain_types)))
            for i, st in enumerate(strain_types):
                colors[st] = color_map[i]

            # Re-plot with strain type colors
            plt.clf()
            plt.figure(figsize=(12, 8))

            for i, (idx, row) in enumerate(pcoa_df.iterrows()):
                # Find strain type
                strain_type = 'unknown'
                for accession, info in self.strain_mapping.items():
                    if info['display_name'] == row['Display_Name']:
                        strain_type = info['metadata'].get('strain_type', 'unknown')
                        break

                plt.scatter(row['PCoA1'], row['PCoA2'],
                          s=100, alpha=0.7, color=colors.get(strain_type, 'gray'),
                          edgecolors='black', linewidth=0.5, label=strain_type)

                plt.annotate(row['Display_Name'],
                           (row['PCoA1'], row['PCoA2']),
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=9, ha='left', va='bottom',
                           bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7))

            # Remove duplicate legend entries
            handles, labels = plt.gca().get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            plt.legend(by_label.values(), by_label.keys(), title='Strain Type')

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_jaccard_heatmap(self, jaccard_matrix: pd.DataFrame, display_names: List[str]):
        """Create Jaccard distance heatmap"""

        # Update matrix with display names
        jaccard_display = jaccard_matrix.copy()
        jaccard_display.index = display_names
        jaccard_display.columns = display_names

        plt.figure(figsize=(12, 10))

        # Create heatmap
        mask = np.triu(np.ones_like(jaccard_display, dtype=bool))  # Mask upper triangle
        sns.heatmap(jaccard_display, mask=mask, annot=True, fmt='.3f',
                   cmap='viridis', square=True, linewidths=0.5,
                   cbar_kws={'label': 'Jaccard Distance'})

        plt.title('Jaccard Distance Heatmap (Gene Presence/Absence)',
                 fontsize=14, fontweight='bold')
        plt.xlabel('Strains')
        plt.ylabel('Strains')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)

        plt.tight_layout()
        plt.savefig(self.jaccard_dir / "jaccard_distance_heatmap.png",
                   dpi=300, bbox_inches='tight')
        plt.close()

    def analyze_core_accessory_genome(self, roary_results: Optional[Path] = None) -> Dict:
        """
        Detailed core vs accessory genome analysis
        """
        logger.info("🌐 Analyzing core vs accessory genome...")

        if not roary_results or not roary_results.exists():
            logger.warning("Roary results not found for core/accessory analysis")
            return {}

        try:
            # Read gene presence/absence file
            gene_presence_file = roary_results / "gene_presence_absence.csv"
            df = pd.read_csv(gene_presence_file, low_memory=False)

            # Get strain columns
            strain_columns = [col for col in df.columns if col not in
                            ['Gene', 'Non-unique Gene name', 'Annotation', 'No. isolates', 'No. sequences']]

            total_strains = len(strain_columns)

            # Calculate gene frequencies
            gene_counts = df[strain_columns].notna().sum(axis=1)
            df['Gene_Frequency'] = gene_counts / total_strains

            # Classify genes
            core_threshold = 0.95  # 95% of strains
            accessory_threshold = 0.15  # 15% of strains

            df['Gene_Class'] = df['Gene_Frequency'].apply(lambda x:
                'Core' if x >= core_threshold else
                'Soft Core' if x >= 0.85 else
                'Shell' if x >= accessory_threshold else
                'Cloud')

            # Calculate statistics
            stats = {
                'total_genes': len(df),
                'core_genes': len(df[df['Gene_Class'] == 'Core']),
                'soft_core_genes': len(df[df['Gene_Class'] == 'Soft Core']),
                'shell_genes': len(df[df['Gene_Class'] == 'Shell']),
                'cloud_genes': len(df[df['Gene_Class'] == 'Cloud']),
                'total_strains': total_strains,
                'core_threshold': core_threshold,
                'accessory_threshold': accessory_threshold
            }

            # Save detailed gene classification
            gene_classification = df[['Gene', 'Annotation', 'No. isolates',
                                    'Gene_Frequency', 'Gene_Class']].copy()
            gene_classification.to_csv(
                self.core_accessory_dir / "gene_classification_detailed.csv",
                index=False)

            # Create visualizations
            self._plot_core_accessory_summary(stats)
            self._plot_gene_frequency_histogram(df)
            self._plot_pangenome_accumulation(df, strain_columns)

            # Save summary statistics
            stats_df = pd.DataFrame([stats])
            stats_df.to_csv(self.core_accessory_dir / "core_accessory_summary.csv",
                           index=False)

            logger.info("✓ Core vs accessory genome analysis completed")
            return stats

        except Exception as e:
            logger.error(f"Error in core/accessory analysis: {e}")
            return {}

    def _plot_core_accessory_summary(self, stats: Dict):
        """Create core vs accessory genome summary plot"""

        categories = ['Core', 'Soft Core', 'Shell', 'Cloud']
        values = [stats[f'{cat.lower().replace(" ", "_")}_genes'] for cat in categories]
        colors = ['#2E8B57', '#32CD32', '#FFD700', '#FF6347']  # Green to red gradient

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Pie chart
        wedges, texts, autotexts = ax1.pie(values, labels=categories, colors=colors,
                                          autopct='%1.1f%%', startangle=90)
        ax1.set_title('Gene Classification Distribution', fontsize=14, fontweight='bold')

        # Bar chart
        bars = ax2.bar(categories, values, color=colors, alpha=0.8,
                      edgecolor='black', linewidth=0.5)
        ax2.set_ylabel('Number of Genes')
        ax2.set_title('Gene Counts by Category', fontsize=14, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for bar, value in zip(bars, values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01*max(values),
                    str(value), ha='center', va='bottom', fontweight='bold')

        plt.suptitle(f'Pan-genome Analysis Summary (n={stats["total_strains"]} strains)',
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.core_accessory_dir / "core_accessory_summary.png",
                   dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_gene_frequency_histogram(self, df: pd.DataFrame):
        """Plot gene frequency distribution"""

        plt.figure(figsize=(12, 6))

        plt.hist(df['Gene_Frequency'], bins=50, alpha=0.7, color='skyblue',
                edgecolor='black', linewidth=0.5)

        # Add vertical lines for thresholds
        plt.axvline(x=0.95, color='red', linestyle='--', linewidth=2,
                   label='Core threshold (95%)')
        plt.axvline(x=0.15, color='orange', linestyle='--', linewidth=2,
                   label='Accessory threshold (15%)')

        plt.xlabel('Gene Frequency (Proportion of Strains)')
        plt.ylabel('Number of Genes')
        plt.title('Distribution of Gene Frequencies Across Strains',
                 fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.core_accessory_dir / "gene_frequency_histogram.png",
                   dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_pangenome_accumulation(self, df: pd.DataFrame, strain_columns: List[str]):
        """Plot pan-genome accumulation curve"""

        # Simulate pan-genome growth by randomly sampling strains
        max_strains = len(strain_columns)
        strain_counts = range(1, max_strains + 1)

        # Multiple iterations for smooth curve
        iterations = 100 if max_strains > 5 else 50
        pangenome_sizes = []
        core_sizes = []

        for n_strains in strain_counts:
            iteration_pangenome = []
            iteration_core = []

            for _ in range(iterations):
                # Random sample of strains
                sampled_strains = np.random.choice(strain_columns, size=n_strains, replace=False)

                # Pan-genome: any gene present in at least one strain
                pangenome_mask = df[sampled_strains].notna().any(axis=1)
                pangenome_size = pangenome_mask.sum()
                iteration_pangenome.append(pangenome_size)

                # Core genome: genes present in all strains
                core_mask = df[sampled_strains].notna().all(axis=1)
                core_size = core_mask.sum()
                iteration_core.append(core_size)

            pangenome_sizes.append(np.mean(iteration_pangenome))
            core_sizes.append(np.mean(iteration_core))

        plt.figure(figsize=(12, 8))

        plt.plot(strain_counts, pangenome_sizes, 'o-', color='blue', linewidth=2,
                markersize=6, label='Pan-genome')
        plt.plot(strain_counts, core_sizes, 'o-', color='red', linewidth=2,
                markersize=6, label='Core genome')

        plt.xlabel('Number of Strains')
        plt.ylabel('Number of Genes')
        plt.title('Pan-genome and Core Genome Accumulation Curves',
                 fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Add final values as text
        plt.text(max_strains * 0.7, max(pangenome_sizes) * 0.9,
                f'Final pan-genome: {int(pangenome_sizes[-1]):,} genes',
                fontsize=10, bbox=dict(boxstyle='round', facecolor='lightblue'))
        plt.text(max_strains * 0.7, max(pangenome_sizes) * 0.8,
                f'Final core genome: {int(core_sizes[-1]):,} genes',
                fontsize=10, bbox=dict(boxstyle='round', facecolor='lightcoral'))

        plt.tight_layout()
        plt.savefig(self.core_accessory_dir / "pangenome_accumulation_curve.png",
                   dpi=300, bbox_inches='tight')
        plt.close()

    def build_enhanced_phylogenetic_trees(self, snippy_results: Optional[Path] = None,
                                        ani_results: Optional[Path] = None) -> Dict:
        """
        Build enhanced phylogenetic trees with better visualization
        """
        logger.info("🌳 Building enhanced phylogenetic trees...")

        tree_results = {}

        # SNP-based tree
        if snippy_results and snippy_results.exists():
            tree_results['snp_tree'] = self._build_snp_tree(snippy_results)

        # ANI-based tree
        if ani_results and ani_results.exists():
            tree_results['ani_tree'] = self._build_ani_tree(ani_results)

        return tree_results

    def _build_snp_tree(self, snippy_results: Path) -> Dict:
        """Build phylogenetic tree from SNP data"""

        try:
            # Look for core alignment file
            core_aln_file = None
            for file in snippy_results.rglob("core.full.aln"):
                core_aln_file = file
                break

            if not core_aln_file:
                logger.warning("Core alignment file not found in Snippy results")
                return {}

            # Build tree using IQ-TREE
            tree_output = self.phylo_dir / "snp_tree"
            tree_output.mkdir(exist_ok=True)

            cmd = f"iqtree -s {core_aln_file} -m GTR+G -bb 1000 -pre {tree_output}/snp_tree"

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                tree_file = tree_output / "snp_tree.treefile"
                if tree_file.exists():
                    # Visualize tree
                    self._visualize_phylogenetic_tree(tree_file, "SNP-based Phylogenetic Tree",
                                                    self.phylo_dir / "snp_tree_visualization.png")

                    logger.info("✓ SNP-based phylogenetic tree built successfully")
                    return {'tree_file': tree_file, 'method': 'IQ-TREE', 'data_type': 'SNP'}
                else:
                    logger.error("Tree file not generated")
            else:
                logger.error(f"IQ-TREE failed: {result.stderr}")

        except Exception as e:
            logger.error(f"Error building SNP tree: {e}")

        return {}

    def _build_ani_tree(self, ani_results: Path) -> Dict:
        """Build phylogenetic tree from ANI distance matrix"""

        try:
            # Read ANI results and create distance matrix
            ani_df = pd.read_csv(ani_results, sep='\t', header=None,
                               names=['query', 'reference', 'ani', 'fragments', 'total_fragments'])

            # Get unique genome names
            genomes = list(set(ani_df['query'].tolist() + ani_df['reference'].tolist()))

            # Create symmetric ANI matrix
            ani_matrix = np.eye(len(genomes)) * 100

            for _, row in ani_df.iterrows():
                query_idx = genomes.index(row['query'])
                ref_idx = genomes.index(row['reference'])
                ani_matrix[query_idx, ref_idx] = row['ani']
                ani_matrix[ref_idx, query_idx] = row['ani']

            # Convert to distance matrix (100 - ANI)
            distance_matrix = 100 - ani_matrix

            # Hierarchical clustering
            condensed_distances = pdist(distance_matrix, metric='euclidean')
            linkage_matrix = linkage(condensed_distances, method='average')

            # Create tree visualization
            plt.figure(figsize=(12, 8))
            dendrogram(linkage_matrix, labels=genomes, leaf_rotation=45,
                      leaf_font_size=10)
            plt.title('ANI-based Phylogenetic Tree (UPGMA)', fontsize=14, fontweight='bold')
            plt.ylabel('Distance (100 - ANI)')
            plt.tight_layout()
            plt.savefig(self.phylo_dir / "ani_tree_visualization.png",
                       dpi=300, bbox_inches='tight')
            plt.close()

            # Save distance matrix
            distance_df = pd.DataFrame(distance_matrix, index=genomes, columns=genomes)
            distance_df.to_csv(self.phylo_dir / "ani_distance_matrix.csv")

            logger.info("✓ ANI-based phylogenetic tree built successfully")

            return {
                'distance_matrix': distance_df,
                'linkage_matrix': linkage_matrix,
                'method': 'UPGMA',
                'data_type': 'ANI'
            }

        except Exception as e:
            logger.error(f"Error building ANI tree: {e}")
            return {}

    def _visualize_phylogenetic_tree(self, tree_file: Path, title: str, output_path: Path):
        """Visualize phylogenetic tree with strain names"""

        try:
            # Read tree
            tree = Phylo.read(tree_file, 'newick')

            # Replace terminal names with display names
            for terminal in tree.get_terminals():
                original_name = terminal.name
                # Find corresponding display name
                for accession, info in self.strain_mapping.items():
                    if (accession in original_name or
                        info['strain_name'] in original_name or
                        any(part in original_name for part in accession.split('_'))):
                        terminal.name = info['display_name']
                        break

            # Create visualization
            fig, ax = plt.subplots(figsize=(12, 8))
            Phylo.draw(tree, axes=ax, do_show=False)
            ax.set_title(title, fontsize=14, fontweight='bold')

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

        except Exception as e:
            logger.error(f"Error visualizing tree: {e}")

def integrate_advanced_analysis(automated_pipeline_results: Dict,
                              results_dir: Path,
                              strain_mapping: Dict) -> Dict:
    """
    Integrate advanced analysis into the automated pipeline
    """

    logger.info("🔬 Running advanced genomics analysis integration...")

    advanced_analysis = AdvancedGenomicsAnalysis(results_dir, strain_mapping)

    advanced_results = {}

    # PCoA analysis
    pcoa_results = advanced_analysis.run_pcoa_analysis(
        roary_results=automated_pipeline_results.get('roary'),
        ani_results=automated_pipeline_results.get('ani')
    )
    advanced_results['pcoa'] = pcoa_results

    # Core/Accessory genome analysis
    core_accessory_results = advanced_analysis.analyze_core_accessory_genome(
        roary_results=automated_pipeline_results.get('roary')
    )
    advanced_results['core_accessory'] = core_accessory_results

    # Enhanced phylogenetic trees
    phylo_results = advanced_analysis.build_enhanced_phylogenetic_trees(
        snippy_results=automated_pipeline_results.get('snippy'),
        ani_results=automated_pipeline_results.get('ani')
    )
    advanced_results['enhanced_phylogeny'] = phylo_results

    logger.info("✓ Advanced genomics analysis completed")

    return advanced_results