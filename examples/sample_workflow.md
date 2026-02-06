# Ornek Calisma Akisi: Uctan Uca DW Mapping

Bu dokuman, bir modul icin mapping surecinin nasil isledigini gosterir.

## 1. Girdi Hazirligi

### Connection String Dosya Formati

**Satir bazli format (conn_key.txt):**
```
type=postgresql
host=10.0.1.50
port=5432
db=keyuygulama
user=etl_user
pass=***
```

**JDBC format (conn_ray.txt):**
```
jdbc:sqlserver://10.0.1.60:1433;databaseName=ray_db
user=etl_user
pass=***
```

### Veri Sozlugu Yapisi

Veri sozlugu dosyasi (txt/md/docx) su bolumlerden olusur:
- **Veri grubu adi** — Mantiksal tablo adi (Ornek: "Kaza Master", "Tehlike Envanter")
- **Icerik aciklamasi** — Hangi verileri icerir
- **Iliskili senaryolar** — Bu verinin kullanildigi senaryo kodlari
- **Ornek alanlar** — Beklenen sutunlar

## 2. Metadata Cekme

```bash
# KEY sistemi (PostgreSQL)
python extract_metadata.py --connection-file conn_key.txt --output key_db_metadata.xlsx

# RAY sistemi (MSSQL)
python extract_metadata.py --connection-file conn_ray.txt --output ray_db_metadata.xlsx
```

Cikti Excel dosyasi 17 sutun icerir (bkz. SKILL.md Adim 2).

## 3. Analiz Sonucu Ornegi

Veri sozlugu analizinden sonra olusturulan siniflandirma:

| Mantiksal Grup | Fiziksel Tablo(lar) | Tip | Hedef Tablo |
|----------------|---------------------|-----|-------------|
| Kaza Master | kazaincelemeraporu | fact | fact_kaza |
| Kaza Kok Neden | kazakokneden | bridge | bridge_kaza_kokneden |
| Birimler | birimler | dim | dim_birim |
| Kaza Turu | kazaturu | dim | dim_kaza_tur |
| Risk Matrisi | riskmatris | fact | fact_risk |
| Tehlike Envanter | tehlikeenvanter | dim | dim_tehlike |

## 4. Mapping Cikti Ornegi

Uretilen Attribute_Level_Mapping.xlsx ozeti:

```
Source System | Source System.1 | Source Db    | Source Schema | Source Table        | M/D    | Target Schema | Source Attribute | Target Physical | Target Logical | Target Attribute    | Schema Code | Modul
PostgreSQL    | KEY             | keyuygulama  | public        | kazaincelemeraporu  | Master | DW            | id               | fact_kaza       | Kaza Master    | kaza_id             | KEY_KS001   | KEY
PostgreSQL    | KEY             | keyuygulama  | public        | kazaincelemeraporu  |        |               | kazatarihi       | fact_kaza       |                | kaza_tarihi         | KEY_KS001   | KEY
PostgreSQL    | KEY             | keyuygulama  | public        | kazaincelemeraporu  |        |               | fk_kazaturid     | fact_kaza       |                | fk_dim_kaza_tur_id  | KEY_KS001   | KEY
PostgreSQL    | KEY             | keyuygulama  | public        | birimler            | Master | DW            | id               | dim_birim       | Birim          | birim_id            | KEY_KS001   | KEY
PostgreSQL    | KEY             | keyuygulama  | public        | birimler            |        |               | birimadi         | dim_birim       |                | birim_adi           | KEY_KS001   | KEY
MSSQL         | RAY             | ray_db       | dbo           | riskmatris          | Master | DW            | IND              | fact_risk       | Risk Matrisi   | risk_id             | KEY_KS001   | KEY
```

## 5. Dogrulama Raporu Ornegi

```markdown
# KEY Modulu Mapping Dogrulama Raporu

## Veri Varligi Ozeti
| Tablo | Kayit Sayisi |
|-------|-------------|
| kazaincelemeraporu | 3,245 |
| kazakokneden | 8,712 |
| birimler | 156 |
| riskmatris | 1,089 |

## Senaryo Dogrulama Sonuclari
| Senaryo | Adim | Sonuc |
|---------|------|-------|
| KS_001 | Kaza-Risk Korelasyon | BASARILI |
| KS_001 | Kok Neden Analizi | BASARILI |
| KS_002 | Risk Onceliklendirme | BASARILI |

## Veri Kalitesi
- kazaincelemeraporu.kazatarihi: %0.2 NULL (7 kayit)
- birimler.sil: 12 kayit silinmis olarak isaretli

## Mapping Istatistikleri
- Fact tablo: 20, Dim tablo: 22, Bridge tablo: 7
- Toplam attribute: 597
- Kaynak sistem: KEY (PostgreSQL) 412 attr, RAY (MSSQL) 185 attr
```

## KEY Modulu Referans Degerleri

KEY modulu icin gerceklesen mapping sonuclari (referans):
- **49** kaynak tablo
- **597** toplam attribute
- **20** fact tablo
- **22** dim tablo
- **7** bridge tablo
- **8** kullanim senaryosu (KS_001 - KS_008)
- **2** kaynak sistem: KEY (PostgreSQL), RAY (MSSQL)
