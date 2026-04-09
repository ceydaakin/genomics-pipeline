# 🧬 Automated Genomics Analysis Pipeline

Kapsamlı otomatik genomik analiz sistemi - BUSCO, ANI, Snippy, Roary, Prokka ve Eggnog mapper analizlerini tek seferde çalıştırır ve suş isimlerini otomatik olarak çıkarır.

## 🚀 Hızlı Başlangıç

### 1. Araçları Kur
```bash
# Tüm gerekli araçları tek seferde kur
./scripts/install_comprehensive_genomics_tools.sh
```

### 2. Analizi Çalıştır
```bash
# Varsayılan genomlar klasöründeki tüm genomları analiz et
./scripts/run_genomics_analysis.sh

# Özel klasördeki genomları analiz et  
./scripts/run_genomics_analysis.sh /path/to/your/genomes
```

### 3. Sonuçları İncele
```bash
# Sonuçlar otomatik olarak organize edilir
cd automated_genomics_results/

# Özet raporu görüntüle
cat 09_Final_Reports/comprehensive_genomics_report.md
```

## 📊 Analiz Aşamaları

Pipeline otomatik olarak şu analizleri yapar:

1. **🔍 BUSCO** - Genom kalite değerlendirmesi
2. **📝 Prokka** - Genom açıklaması (annotation)
3. **🧮 FastANI** - Ortalama nükleotid benzerliği
4. **🔍 Snippy** - SNP analizi ve filogenetik ağaç
5. **🌐 Roary** - Pan-genom analizi
6. **🥚 EggNOG** - Fonksiyonel açıklama

### 🔬 İleri Düzey Analizler (Otomatik)
7. **📊 PCoA** - Principal Coordinates Analysis
8. **🧬 Core/Accessory** - Core vs accessory genom karşılaştırması  
9. **📏 Jaccard** - Jaccard uzaklık analizi
10. **🌳 Enhanced Phylogeny** - Gelişmiş filogenetik ağaçlar

## 📁 Sonuç Klasör Yapısı

```
automated_genomics_results/
├── 01_BUSCO_Quality_Assessment/
│   ├── by_strain/           # Her suş için ayrı BUSCO sonuçları
│   │   ├── DSM_21775_senmaizukei/
│   │   ├── OPSG_3_2_4_senmaizukei/
│   │   └── ...
│   └── summary/            # Toplu BUSCO özeti
├── 02_Prokka_Annotation/
│   ├── by_strain/          # Her suş için Prokka sonuçları
│   └── combined_annotations/ # Birleştirilmiş annotation dosyaları
├── 03_ANI_Analysis/
│   └── fastani_results.txt # ANI matrisi
├── 04_Snippy_SNP_Analysis/
│   └── snippy_core/        # SNP temelli filogenetik analiz
├── 05_Roary_Pangenome/
│   └── roary_output/       # Pan-genom analiz sonuçları
├── 06_EggNOG_Functional/
│   ├── by_strain/          # Her suş için fonksiyonel analiz
│   └── ...
├── 07_Comparative_Analysis/
│   ├── ani_results/        # Karşılaştırmalı ANI analizi
│   ├── snippy_results/     # Karşılaştırmalı SNP analizi
│   └── roary_results/      # Karşılaştırmalı pan-genom
├── 08_Plots_and_Figures/
│   ├── busco_plots/        # BUSCO grafikleri
│   ├── ani_plots/          # ANI ısı haritaları
│   ├── snippy_plots/       # SNP analizleri
│   └── summary_plots/      # Özet grafikler
├── 09_Final_Reports/
│   ├── comprehensive_genomics_report.md
│   ├── strain_summary.csv
│   └── analysis_summary.json
└── 10_Advanced_Analysis/   # İleri düzey analizler
    ├── pcoa_analysis/      # PCoA koordinatları ve grafikleri
    ├── core_accessory_genome/ # Core vs accessory genom analizi
    ├── jaccard_analysis/   # Jaccard uzaklık matrisi ve heatmap
    └── enhanced_phylogeny/ # Gelişmiş filogenetik ağaçlar
```

## 🔧 Gelişmiş Kullanım

### Python Script'i Doğrudan Kullanma
```bash
# Temel kullanım
python src/automated_genomics_pipeline.py --input data/

# Özelleştirilmiş parametreler
python src/automated_genomics_pipeline.py \
    --input /path/to/genomes \
    --output custom_results/ \
    --threads 8 \
    --busco-db lactobacillales_odb10

# Dry run - sadece ne yapılacağını göster
python src/automated_genomics_pipeline.py --input genomes/ --dry-run
```

### Konfigürasyon Dosyası
```bash
# Konfigürasyon kaydet
python src/automated_genomics_pipeline.py --input genomes/ --config configs/my_config.json

# Kaydedilmiş konfigürasyonu kullan
python src/automated_genomics_pipeline.py --config configs/my_config.json
```

## 🧪 Suş İsmi Çıkarma

Sistem otomatik olarak FASTA başlıklarından bakteriyel suş isimlerini çıkarır:

- **GCA_001592085.1_ASM159208v1** → **DSM_21775_senmaizukei**
- **OPSG_3_2_4_genomic.fna** → **OPSG_3_2_4_senmaizukei**
- **Levilactobacillus parabrevis** → **L_parabrevis_strain**

Grafikler ve raporlarda accession numaraları yerine anlaşılır suş isimleri kullanılır.

## 📋 Gereksinimler

### Conda Ortamı
```bash
# Gerekli ortam
conda activate genomics-analysis-complete

# Gerekli araçlar
- busco (genom kalitesi)
- fastANI (ANI analizi)
- snippy (SNP çağırma)
- roary (pan-genom)
- prokka (annotation)
- emapper.py (fonksiyonel annotation)
```

### Python Paketleri
```bash
- biopython
- pandas
- matplotlib
- seaborn
- numpy
- scipy
- scikit-learn
```

## 📝 Desteklenen Genom Formatları

- `.fna` - FASTA Nucleic Acid
- `.fasta` - FASTA format
- `.fa` - FASTA short extension
- `.fna.gz` - Sıkıştırılmış FASTA

## ⚡ Performans İpuçları

### Hızlı Analiz İçin
```bash
# Daha fazla thread kullan
--threads 8

# Hızlı BUSCO veritabanı seç
--busco-db bacteria_odb10

# SSD disk kullan (mümkünse)
```

### Bellek Optimizasyonu
```bash
# Büyük genom setleri için
export OMP_NUM_THREADS=4
ulimit -v 8000000  # 8GB bellek limiti
```

## 🔍 Sorun Giderme

### Log Dosyaları
```bash
# Ana log dosyası
tail -f automated_genomics_pipeline.log

# Belirli analiz logları
ls automated_genomics_results/*/logs/
```

### Yaygın Sorunlar

1. **Conda ortamı aktif değil**
   ```bash
   conda activate genomics-analysis-complete
   ```

2. **Araçlar bulunamıyor**
   ```bash
   ./scripts/install_comprehensive_genomics_tools.sh
   ```

3. **Bellek yetersizliği**
   ```bash
   # Thread sayısını azalt
   --threads 2
   ```

4. **Disk alanı yetersiz**
   ```bash
   # Sonuç klasörünü büyük diske taşı
   --output /path/to/large/disk/results
   ```

## 📚 Örnek Kullanımlar

### FE_CS Genomics Projesi
```bash
# Proje için optimize edilmiş analiz
./scripts/run_genomics_analysis.sh data/

# L. senmaizukei'ye özel BUSCO veritabanı
python src/automated_genomics_pipeline.py \
    --input data/ \
    --busco-db lactobacillales_odb10
```

### Özel Genom Seti
```bash
# Kendi genomlarınızı analiz edin
mkdir data/my_genomes/
cp *.fna data/my_genomes/
./scripts/run_genomics_analysis.sh data/my_genomes/
```

## 📂 Proje Yapısı

```
genomics-pipeline/
├── src/                    # Python modülleri
│   ├── automated_genomics_pipeline.py
│   ├── genomics_config.py
│   ├── strain_extractor.py
│   ├── output_organizer.py
│   └── advanced_genomics_analysis.py
├── scripts/               # Shell scriptleri
│   ├── install_comprehensive_genomics_tools.sh
│   └── run_genomics_analysis.sh
├── data/                  # Genom verileri
│   └── README.md          # Veri klasörü rehberi
├── docs/                  # Dokümantasyon
├── tests/                 # Test dosyaları
├── examples/             # Örnek kullanımlar
├── configs/              # Konfigürasyon dosyaları
└── README.md             # Ana dokümantasyon (bu dosya)
```

## 🎯 Çıktı Örnekleri

### Strain Summary Tablosu
| Strain Name | Display Name | Species | Type | File Size (MB) |
|-------------|--------------|---------|------|----------------|
| DSM_21775_senmaizukei | L. senmaizukei DSM 21775 | Levilactobacillus senmaizukei | reference | 2.1 |
| OPSG_3_2_4_senmaizukei | L. senmaizukei OPSG_3_2_4 | Levilactobacillus senmaizukei | local_isolate | 2.2 |

### Analiz Durumu
- **BUSCO**: ✅ Completed
- **Prokka**: ✅ Completed  
- **ANI**: ✅ Completed
- **Snippy**: ✅ Completed
- **Roary**: ✅ Completed
- **EggNOG**: ✅ Completed
- **PCoA**: ✅ Completed
- **Core/Accessory**: ✅ Completed
- **Jaccard**: ✅ Completed
- **Enhanced Phylogeny**: ✅ Completed

## 🤝 Destek

Sorun yaşarsanız:

1. Log dosyalarını kontrol edin
2. GitHub issues açın  
3. Detaylı hata mesajları paylaşın

## 📖 İlgili Dokümantasyon

- [Kurulum Rehberi](docs/installation.md)
- [Kullanım Örnekleri](examples/)
- [API Dokümantasyonu](docs/api.md)
- [Sorun Giderme](docs/troubleshooting.md)

---

**🧬 Ceyda Akın - ITU Food Engineering Department**  
**Automated Genomics Analysis Pipeline v1.0**