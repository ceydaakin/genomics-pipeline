# FE_CS Genomics Data Directory

Bu klasöre genom dosyalarınızı yerleştirin.

## Desteklenen Formatlar
- `.fna` - FASTA Nucleic Acid
- `.fasta` - FASTA format  
- `.fa` - FASTA short extension
- `.fna.gz` - Compressed FASTA

## Örnek Dosya Yapısı
```
fe_cs_genomics/
├── GCA_001592085.1_ASM159208v1_genomic.fna
├── OPSG_3_2_4_genomic.fna
├── GCA_000383435.1_ASM38343v1_genomic.fna
└── [diğer genom dosyaları...]
```

## Kullanım
```bash
# Genom dosyalarını bu klasöre kopyalayın
cp *.fna data/fe_cs_genomics/

# Analizi çalıştırın
./scripts/run_genomics_analysis.sh
```

**Not:** Genom dosyaları repository'de yer kapladığı için .gitignore ile hariç tutulmuştur. 
Kendi genom dosyalarınızı bu klasöre eklemeniz gerekir.