# Attribute_Level_Mapping Sablon Format Tanimi

Bu dosya, Attribute_Level_Mapping.xlsx sablonunun 15 sutununu ve Entity_Level_Mapping.xlsx formatini tanimlar.

## Sutun Tanimlari

| # | Sutun Adi | Aciklama | Ornek Deger | Doldurma Kurali |
|---|-----------|----------|-------------|-----------------|
| 1 | Source System | Kaynak veritabani tipi | PostgreSQL, MSSQL | Her satirda dolu |
| 2 | Source System.1 | Kaynak sistem kisa adi | KEY, RAY, SAP | Her satirda dolu |
| 3 | Source Db | Veritabani adi | keyuygulama, ray_db | Her satirda dolu |
| 4 | Source Schema | Sema adi | public, dbo | Her satirda dolu |
| 5 | Source Table | Kaynak tablo adi | kazaincelemeraporu | Her satirda dolu |
| 6 | Master/Detail | Hedef tablo gruplama | Master / (bos) | Ilk satir Master, sonrakiler bos |
| 7 | Target Schema | Hedef sema | DWH | Ilk satir DWH, sonrakiler bos |
| 8 | Source Attribute | Kaynak sutun adi | kazatarihi | Her satirda dolu, metadata'dan dogrulanmis |
| 9 | Target Physical Name | Hedef fiziksel tablo adi | f_kaza | Her satirda dolu |
| 10 | Target Logical Name | Hedef mantiksal ad (Turkce) | Kaza Master | Ilk satirda dolu, sonrakiler bos |
| 11 | Target Attribute | Hedef sutun adi (snake_case, lowercase) | kaza_tarihi | Her satirda dolu |
| 12 | Schema Code | Senaryo kodu | KEY_KS001 | Her satirda dolu |
| 13 | Modul | Modul adi | KEY | Her satirda dolu |
| 14 | Kullanim Senaryosu | Tablonun hangi senaryoya ait oldugu | KS_001, KS_002 | Her satirda dolu |
| 15 | Senaryo Adimi | Senaryonun hangi adiminda kullanildigi | Kaza-Risk Korelasyon | Her satirda dolu |

## Master/Detail Mantigi

Bir hedef tablo (Target Physical Name) icin birden fazla attribute satiri olur:

```
Source Table | Master/Detail | Target Physical Name | Source Attribute | Target Attribute
------------ | ------------- | -------------------- | --------------- | ----------------
kazaraporu   | Master        | f_kaza               | id              | kaza_id
kazaraporu   |               | f_kaza               | kazatarihi      | kaza_tarihi
kazaraporu   |               | f_kaza               | kazaturid       | kaza_turu_id
birimler     | Master        | d_birim              | id              | birim_id
birimler     |               | d_birim              | birimadi        | birim_adi
```

- `Master` yalnizca hedef tablonun **ilk satirinda** yazilir
- Ayni hedef tablonun sonraki satirlari **Master/Detail bos** birakilir
- Yeni bir hedef tablo basladiginda tekrar `Master` yazilir

## Target Schema Mantigi

- `DWH` yalnizca hedef tablonun **ilk satirinda** yazilir (Master ile ayni satirda)
- Sonraki satirlar bos birakilir

## Target Logical Name Mantigi

- Turkce aciklayici isim: "Kaza Master", "Birim Dimension", "Tehlike-KokNeden Bridge"
- Yalnizca hedef tablonun **ilk satirinda** yazilir
- Sonraki satirlar bos birakilir

## Renk Kodlama

Excel'de satirlar hedef tablo tipine gore renklendirilir:
- **Mavi (#DBEEF4)**: f_ tablolari (fact)
- **Yesil (#E2EFDA)**: d_ tablolari (dimension)
- **Sari (#FFF2CC)**: b_ tablolari (bridge)

## Excel Formatlama

- Header: Koyu mavi arka plan (#4472C4), beyaz bold yazi
- Font: Calibri 10pt
- Freeze Pane: A2 (header sabit)
- Auto-Filter: Tum sutunlarda aktif
- Header satir yuksekligi: 30px

---

## Entity_Level_Mapping Sablon Formati

Entity seviyesinde mapping: her hedef tablo icin tek satir.

### Sutun Tanimlari

| # | Sutun Adi | Aciklama | Ornek Deger | Doldurma Kurali |
|---|-----------|----------|-------------|-----------------|
| 1 | Target Schema | Hedef sema | dwh | Sabit "dwh" (lowercase) |
| 2 | Target Physical Name | Hedef fiziksel tablo adi | f_kaza | Her satirda dolu |
| 3 | Target Logical Name | Hedef mantiksal ad (Turkce) | Kaza Master | Her satirda dolu |
| 4 | Source System | Kaynak veritabani tipi | PostgreSQL | Ilk kaynak satirdan |
| 5 | Source Db | Veritabani adi | keyuygulama | Ilk kaynak satirdan |
| 6 | Source Schema | Sema adi | public | Ilk kaynak satirdan |
| 7 | Source Table | Kaynak tablo adi | kazaincelemeraporu | Ilk kaynak satirdan |
| 8 | Modul | Modul adi | KEY | Ilk satirdan |

### Excel Formatlama

- Sheet adi: "Source-DWH"
- Header: Gri arka plan (#A5A5A5), bold yazi
- Font: Calibri 10pt
- Freeze Pane: A2 (header sabit)
- Auto-Filter: Tum sutunlarda aktif
- Renk kodlama yok (duz beyaz satirlar)
