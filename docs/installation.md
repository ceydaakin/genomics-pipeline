# Installation Guide

Bu rehber Automated Genomics Pipeline'ın kurulumunu detaylı olarak açıklar.

## Sistem Gereksinimleri

### Operating System
- macOS (Intel/Apple Silicon)
- Linux (Ubuntu 18.04+, CentOS 7+)
- Windows (WSL2 önerilir)

### Disk Space
- En az 10 GB boş disk alanı
- Analiz sonuçları için ek alan (veri boyutuna bağlı)

### Memory
- En az 8 GB RAM
- 16 GB+ önerilir

## Adım 1: Proje İndirme

```bash
# Projeyi klonla veya indir
cd /Users/yourusername/
git clone <repository-url> genomics-pipeline
# veya
# ZIP dosyasını indir ve çıkart

cd genomics-pipeline/
```

## Adım 2: Conda/Miniconda Kurulumu

Eğer Conda yüklü değilse:

### macOS (Apple Silicon)
```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
bash Miniconda3-latest-MacOSX-arm64.sh
```

### macOS (Intel)
```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
bash Miniconda3-latest-MacOSX-x86_64.sh
```

### Linux
```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

Terminal'i kapatıp tekrar açın.

## Adım 3: Bioinformatics Tools Kurulumu

```bash
# Tüm gerekli araçları otomatik kur
./scripts/install_comprehensive_genomics_tools.sh
```

Bu script şunları yükler:
- BUSCO (genom kalite değerlendirmesi)
- FastANI (ANI analizi)
- Snippy (SNP analizi)
- Roary (pan-genom)
- Prokka (annotation)
- EggNOG-mapper (fonksiyonel annotation)
- IQ-TREE, RAxML (filogenetik ağaçlar)
- Gerekli Python paketleri

## Adım 4: Environment Aktivasyonu

```bash
conda activate genomics-analysis-complete
```

## Adım 5: Kurulum Doğrulama

```bash
# Test scripti ile doğrula
python tests/test_complete_pipeline.py
```

Başarılı kurulum sonrası göreceğiniz output:
```
🧬 AUTOMATED GENOMICS PIPELINE - COMPLETE TEST SUITE
======================================================================
✅ Testing strain extraction...
✅ Pipeline dry run results...
✅ Advanced Analysis Components Test...
✅ All tests completed!
```

## Adım 6: İlk Analiz

```bash
# Örnek veri ile test
./scripts/run_genomics_analysis.sh data/fe_cs_genomics/
```

## Troubleshooting

### Conda environment bulunamıyor
```bash
# Environment'i manuel oluştur
conda create -n genomics-analysis-complete python=3.9 -y
conda activate genomics-analysis-complete

# Gerekli paketleri yükle
conda install -c bioconda -c conda-forge busco fastani snippy roary prokka eggnog-mapper -y
```

### Araçlar PATH'te bulunamıyor
```bash
# Environment'ın aktif olduğunu kontrol et
echo $CONDA_DEFAULT_ENV

# Manuel aktivasyon
source $(conda info --base)/etc/profile.d/conda.sh
conda activate genomics-analysis-complete
```

### Permission Denied Hataları
```bash
# Script'leri executable yap
chmod +x scripts/*.sh
chmod +x tests/*.py
```

### Disk Alanı Yetersizliği
```bash
# Sonuçları başka diske taşı
python src/automated_genomics_pipeline.py \
    --input data/ \
    --output /path/to/large/disk/results/
```

### Memory Hataları
```bash
# Thread sayısını azalt
python src/automated_genomics_pipeline.py \
    --input data/ \
    --threads 2

# Memory limitlerini ayarla
export OMP_NUM_THREADS=2
ulimit -v 4000000  # 4GB limit
```

## Avançed Configuration

### Custom BUSCO Database
```bash
# Lactobacillales için özel database
python src/automated_genomics_pipeline.py \
    --input data/ \
    --busco-db lactobacillales_odb10
```

### Configuration File
```bash
# Ayarları kaydet
python src/automated_genomics_pipeline.py \
    --input data/ \
    --threads 8 \
    --output custom_results/ \
    --config configs/my_config.json

# Tekrar kullan
python src/automated_genomics_pipeline.py \
    --config configs/my_config.json
```

## Uninstallation

```bash
# Conda environment'ı sil
conda env remove -n genomics-analysis-complete

# Proje klasörünü sil
rm -rf genomics-pipeline/
```

## Getting Help

1. Log dosyalarını kontrol edin: `automated_genomics_pipeline.log`
2. Issues açın: GitHub repository issues
3. Dokumentasyonu okuyun: `docs/` klasöründe