# Attribute_Level_Mapping Sablon Format Tanimi

Bu dosya, Attribute_Level_Mapping.xlsx sablonunun 13 sutununu tanimlar.

## Sutun Tanimlari

| # | Sutun Adi | Aciklama | Ornek Deger | Doldurma Kurali |
|---|-----------|----------|-------------|-----------------|
| 1 | Source System | Kaynak veritabani tipi | PostgreSQL, MSSQL | Her satirda dolu |
| 2 | Source System.1 | Kaynak sistem kisa adi | KEY, RAY, SAP | Her satirda dolu |
| 3 | Source Db | Veritabani adi | keyuygulama, ray_db | Her satirda dolu |
| 4 | Source Schema | Sema adi | public, dbo | Her satirda dolu |
| 5 | Source Table | Kaynak tablo adi | kazaincelemeraporu | Her satirda dolu |
| 6 | Master/Detail | Hedef tablo gruplama | Master / (bos) | Ilk satir Master, sonrakiler bos |
| 7 | Target Schema | Hedef sema | DW | Ilk satir DW, sonrakiler bos |
| 8 | Source Attribute | Kaynak sutun adi | kazatarihi | Her satirda dolu, metadata'dan dogrulanmis |
| 9 | Target Physical Name | Hedef fiziksel tablo adi | fact_kaza | Her satirda dolu |
| 10 | Target Logical Name | Hedef mantiksal ad (Turkce) | Kaza Master | Ilk satirda dolu, sonrakiler bos |
| 11 | Target Attribute | Hedef sutun adi (snake_case) | kaza_tarihi | Her satirda dolu |
| 12 | Schema Code | Senaryo kodu | KEY_KS001 | Her satirda dolu |
| 13 | Modul | Modul adi | KEY | Her satirda dolu |

## Master/Detail Mantigi

Bir hedef tablo (Target Physical Name) icin birden fazla attribute satiri olur:

```
Source Table | Master/Detail | Target Physical Name | Source Attribute | Target Attribute
------------ | ------------- | -------------------- | --------------- | ----------------
kazaraporu   | Master        | fact_kaza            | id              | kaza_id
kazaraporu   |               | fact_kaza            | kazatarihi      | kaza_tarihi
kazaraporu   |               | fact_kaza            | kazaturid       | fk_dim_kaza_tur_id
birimler     | Master        | dim_birim            | id              | birim_id
birimler     |               | dim_birim            | birimadi        | birim_adi
```

- `Master` yalnizca hedef tablonun **ilk satirinda** yazilir
- Ayni hedef tablonun sonraki satirlari **Master/Detail bos** birakilir
- Yeni bir hedef tablo basladiginda tekrar `Master` yazilir

## Target Schema Mantigi

- `DW` yalnizca hedef tablonun **ilk satirinda** yazilir (Master ile ayni satirda)
- Sonraki satirlar bos birakilir

## Target Logical Name Mantigi

- Turkce aciklayici isim: "Kaza Master", "Birim Dimension", "Tehlike-KokNeden Bridge"
- Yalnizca hedef tablonun **ilk satirinda** yazilir
- Sonraki satirlar bos birakilir

## Renk Kodlama

Excel'de satirlar hedef tablo tipine gore renklendirilir:
- **Mavi (#DBEEF4)**: fact_ tablolari
- **Yesil (#E2EFDA)**: dim_ tablolari
- **Sari (#FFF2CC)**: bridge_ tablolari

## Excel Formatlama

- Header: Koyu mavi arka plan (#4472C4), beyaz bold yazi
- Font: Calibri 10pt
- Freeze Pane: A2 (header sabit)
- Auto-Filter: Tum sutunlarda aktif
- Header satir yuksekligi: 30px
