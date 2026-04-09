# Project Structure

```
genomics-pipeline/
├── README.md                           # Ana proje dokümantasyonu
├── PROJECT_STRUCTURE.md               # Bu dosya - proje yapısı
│
├── src/                               # Python modülleri
│   ├── automated_genomics_pipeline.py # Ana pipeline scripti
│   ├── genomics_config.py             # Konfigürasyon sistemi
│   ├── strain_extractor.py            # Suş ismi çıkarma modülü
│   ├── output_organizer.py            # Çıktı organizasyon sistemi
│   └── advanced_genomics_analysis.py  # İleri seviye analizler
│
├── scripts/                           # Shell scriptleri
│   ├── install_comprehensive_genomics_tools.sh  # Tool kurulum scripti
│   └── run_genomics_analysis.sh       # Ana çalıştırma scripti
│
├── data/                              # Veri klasörü
│   ├── README.md                      # Veri kullanım rehberi
│   └── fe_cs_genomics/                # FE_CS projesi genom verileri
│       ├── GCA_*.fna                  # GenBank assembly dosyaları
│       ├── OPSG_*.fna                 # Yerel suş dosyaları
│       ├── Levilactobacillus*.fasta   # Diğer genom dosyaları
│       ├── busco_downloads/           # BUSCO veritabanları
│       └── busco_results/             # BUSCO sonuçları
│
├── tests/                             # Test dosyaları
│   └── test_complete_pipeline.py      # Kapsamlı test scripti
│
├── examples/                          # Kullanım örnekleri
│   └── basic_usage.sh                 # Temel kullanım örnekleri
│
├── docs/                              # Dokümantasyon
│   └── installation.md                # Detaylı kurulum rehberi
│
└── configs/                           # Konfigürasyon dosyaları
    └── example_config.json            # Örnek konfigürasyon
```

## Key Files Description

### Core Pipeline Files
- **`src/automated_genomics_pipeline.py`** - Ana pipeline, tüm analizleri koordine eder
- **`src/genomics_config.py`** - Pipeline konfigürasyon ve ayarları
- **`src/strain_extractor.py`** - FASTA başlıklarından suş ismi çıkarma
- **`src/output_organizer.py`** - Sonuçları suş isimlerine göre organize etme
- **`src/advanced_genomics_analysis.py`** - PCoA, Jaccard, Core/Accessory analizler

### User Interface
- **`scripts/run_genomics_analysis.sh`** - Ana kullanıcı interface scripti
- **`scripts/install_comprehensive_genomics_tools.sh`** - Tüm araçları kurar
- **`README.md`** - Ana kullanım rehberi

### Testing & Examples
- **`tests/test_complete_pipeline.py`** - Sistem testleri
- **`examples/basic_usage.sh`** - Kullanım örnekleri
- **`docs/installation.md`** - Kurulum rehberi

### Data Organization
- **`data/fe_cs_genomics/`** - Mevcut genom verileri (74MB)
- **`configs/example_config.json`** - Konfigürasyon şablonu

## Usage Quick Start

1. **Install tools:** `./scripts/install_comprehensive_genomics_tools.sh`
2. **Run analysis:** `./scripts/run_genomics_analysis.sh`
3. **Check results:** `automated_genomics_results/`

## File Counts
- Python modules: 5
- Shell scripts: 2  
- Documentation: 4
- Test files: 1
- Config files: 1
- Genome files: ~20 (in data/fe_cs_genomics/)

## Total Project Size
- Code + docs: ~200KB
- Data: ~74MB
- Total: ~74MB