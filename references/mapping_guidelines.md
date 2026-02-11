# DW Mapping Kurallari ve Naming Conventions

Bu dosya, veri ambari attribute-level mapping sureci icin genel kurallari tanimlar.

## 1. Katman Mimarisi

| Katman | Sema | Aciklama |
|--------|------|----------|
| Mirror | ODS | Kaynak sistemlerden birebir kopyalanan ham veri |
| Foundation | DWH | Star schema modeline donusturulmus analitik veri |
| Staging | STG | Ara donusum tablolari |
| Logging | ETL | ETL surec loglari |

Mapping sureci ODS → DWH donusumunu tanimlar.

## 2. Star Schema Siniflandirma Kurallari

### Fact Tablolar (f_)
- Transactional / event verisi icerir
- Olculebilir degerler (metrik) icerir
- Zaman bazli kayitlar
- Ornekler: f_tasima, f_kaza, f_denetim, f_risk
- Her fact tablosunda surrogate key (xxx_id) ve ilgili dim FK'lari bulunur

### Dimension Tablolar (d_)
- Referans / lookup verisi icerir
- Yavaş degisen boyutlar (SCD)
- Ornekler: d_musteri, d_birim, d_istasyon, d_kaza_turu
- Her dim tablosunda surrogate key (xxx_id) ve dogal anahtar bulunur

### Bridge Tablolar (b_)
- M:N (coktan coka) iliskileri cozer
- Iki veya daha fazla tablonun kesisim kumesi
- Ornekler: b_kaza_kokneden, b_tehlike_tedbir, b_personel_sertifikasyon
- Her bridge tablosunda iliskili tablolarin FK'lari bulunur

## 3. Naming Conventions

### Genel Kurallar
- Tum tablo ve kolon isimlerinde **Turkce karakter kullanilmaz** (s→s, c→c, g→g, i→i, o→o, u→u)
- Tum tablo ve kolon isimlerinde **kucuk harf (lowercase)** kullanilir (Iceberg ve Trino gerekliligi)
- Kaynak sutun adini mumkun oldugunca koru, sadece convention'a uygun hale getir

### ODS Katmani Tablo Adlari
- Kaynak sistem ismi prefix olarak kullanilir
- Ornekler: `kky_zkky_iybs_0288`, `ytp_musteri`

### Hedef (DWH) Tablo Adlari
- `f_{isim}` — Ornek: f_tasima, f_kaza, f_risk
- `d_{isim}` — Ornek: d_musteri, d_birim, d_hat
- `b_{isim1}_{isim2}` — Ornek: b_kaza_kokneden

### Kolon Postfix Kurallari

| Alan Tipi | Postfix | Ornek |
|-----------|---------|-------|
| ID kolonlari (PK/FK) | `_id` | musteri_id, vagon_id |
| Kod alanlari | `_kodu` | vagon_kodu, istasyon_kodu |
| Ad alanlari | `_adi` | musteri_adi, istasyon_adi |
| Durum alanlari | `_durumu` | siparis_durumu, kayit_durumu |
| Tip alanlari | `_tipi` | vagon_tipi, kaza_tipi |
| Adet alanlari | `_adedi` | vagon_adedi, yolcu_adedi |
| Sure alanlari | `_suresi` | yolculuk_suresi, bekleme_suresi |
| Tarih alanlari | `_tarihi` | tasima_tarihi, yukleme_tarihi |
| Boolean alanlar | `_mi` / `_mu` | aktif_mi, haftasonu_mu |
| Parasal degerler | `_tutari` | bilet_tutari, navlun_tutari |

## 4. Anahtar Kurallari

- Tum PK ve FK alanlari `_id` ile biter
- FK olarak kullanilan, `_id` ile biten her kolon icin bir boyut (d_) tablosu olmak **zorundadir**
- Fiziksel olarak PK ve FK tanimlari olusturulmaz (Iceberg kisitlamasi)
- Mantiksal modelde (Powerdesigner) tablolar arasi iliskiler korunur

## 5. Metadata Kolonlari (Audit)

### ODS Katmani (Mirror)
| Kolon | Aciklama |
|-------|----------|
| yukleme_tarihi | Kaydin eklendigi tarih |

### DWH Katmani (Foundation)
| Kolon | Aciklama |
|-------|----------|
| yukleme_tarihi | Kaydin eklendigi tarih |
| yukleyen | Kaydi kimin ekledigi |
| guncelleme_tarihi | Kaydin guncellendigi tarih |
| guncelleyen | Kaydi kimin guncelledigi |
| kaynak_tablo | Kaynak tablo bilgisi |

Bu metadata kolonlari tum hedef tablolara otomatik eklenir.

## 6. Soft Delete Pattern

Kaynak sistemde soft delete sutunlari:
- `sil` (boolean/flag) — Silinmis mi?
- `siltar` (datetime) — Silinme tarihi
- `fk_durum` — Kayit durumu (aktif/pasif)

Hedef tarafta:
- Bu sutunlar mapping'e dahil edilir
- ETL surecinde filtreleme kurali olarak kullanilir: `WHERE sil = 0` veya `WHERE fk_durum = aktif`
- Mapping'de not olarak belirtilir

## 7. Sablon Alanlari Doldurma Kurallari

### Source System (1. sutun)
- DB tipi yazilir: `PostgreSQL`, `MSSQL`, `Oracle`, `MySQL`

### Source System.1 (2. sutun)
- Kaynak sistem kisa adi: `KEY`, `RAY`, `SAP`, `HR`

### Master/Detail (6. sutun)
- Bir hedef tablonun **ilk satiri**: `Master`
- Ayni tablonun sonraki satirlari: bos birakilir
- Yeni hedef tablo basladiginda tekrar `Master`

### Target Schema (7. sutun)
- Ilk satir: `DWH` (Foundation katmani semasi)
- Sonraki satirlar: bos birakilir

### Schema Code (12. sutun)
- Format: `{MODUL}_{SENARYO}` — Ornek: KEY_KS001, RAY_KS002
- Bir attribute birden fazla senaryoda kullaniliyorsa, ilk/ana senaryo yazilir

## 8. Veri Tipi Donusumleri

Genel kurallar:
- `varchar/text` → `VARCHAR(n)` (kaynak max_uzunluk korunur)
- `integer/int` → `INTEGER`
- `bigint` → `BIGINT`
- `numeric/decimal` → `NUMERIC(p,s)` (precision/scale korunur)
- `boolean/bit` → `BOOLEAN`
- `timestamp/datetime` → `TIMESTAMP`
- `date` → `DATE`

## 9. Onemli Kurallar

1. **Metadata'da olmayan sutun UYDURULMAZ** — Her kaynak sutun metadata'da var olmali
2. **Birden fazla kaynak tablodan ayni hedef tabloya mapping yapilabilir** — Farkli kaynak tablolar ayni f_/d_ tablosunu besleyebilir
3. **Surrogate key'ler hedef tarafta eklenir** — Kaynak sistemde karsiligi olmayabilir, mapping'de `[generated]` olarak isaretlenir
4. **NULL degerler korunur** — Kaynak NULL ise hedef de NULL olur, ozel donusum yoksa
5. **Tarih formatlari standartlastirilir** — Hedef tarafta ISO 8601 (YYYY-MM-DD HH:MM:SS)
