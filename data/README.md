# Data Directory

Bu klasör genomics analizi için gerekli veri dosyalarını içerir.

## Klasör Yapısı

```
data/
└── fe_cs_genomics/          # FE_CS projesi genom verileri
    ├── GCA_*.fna            # GenBank assemblies
    ├── OPSG_*.fna           # Yerel suşlar
    └── busco_downloads/     # BUSCO veritabanları
```

## Veri Formatları

Desteklenen genom dosya formatları:
- `.fna` - FASTA Nucleic Acid
- `.fasta` - FASTA format
- `.fa` - FASTA short extension
- `.fna.gz` - Sıkıştırılmış FASTA

## Yeni Veri Ekleme

Yeni genom dosyalarını bu klasöre eklemek için:

1. Dosyaları uygun alt klasöre koyun
2. Dosya isimlerinin accession numarası veya suş bilgisi içerdiğinden emin olun
3. Pipeline otomatik olarak suş isimlerini çıkaracaktır

## Örnek Kullanım

```bash
# Yeni veri seti oluştur
mkdir data/my_project/

# Genomları ekle
cp *.fna data/my_project/

# Analizi çalıştır
./scripts/run_genomics_analysis.sh data/my_project/
```