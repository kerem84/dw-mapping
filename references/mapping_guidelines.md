# DW Mapping Kurallari ve Naming Conventions

Bu dosya, veri ambari attribute-level mapping sureci icin genel kurallari tanimlar.

## 1. Star Schema Siniflandirma Kurallari

### Fact Tablolar (fact_)
- Transactional / event verisi icerir
- Olculebilir degerler (metrik) icerir
- Zaman bazli kayitlar
- Ornekler: kazalar, riskler, denetimler, olaylar, hareketler
- Her fact tablosunda surrogate key (fact_xxx_id) ve ilgili dim FK'lari bulunur

### Dimension Tablolar (dim_)
- Referans / lookup verisi icerir
- Yavaş degisen boyutlar (SCD)
- Ornekler: personel, birimler, hat/istasyon, kaza turleri, risk kategorileri
- Her dim tablosunda surrogate key (dim_xxx_id) ve dogal anahtar bulunur

### Bridge Tablolar (bridge_)
- M:N (coktan coka) iliskileri cozer
- Iki veya daha fazla tablonun kesisim kumesi
- Ornekler: kaza-kok_neden, tehlike-tedbir, personel-sertifikasyon
- Her bridge tablosunda iliskili tablolarin FK'lari bulunur

## 2. Naming Conventions

### Hedef Tablo Adlari
- `fact_{isim}` — Ornek: fact_kaza, fact_risk, fact_denetim
- `dim_{isim}` — Ornek: dim_personel, dim_birim, dim_hat
- `bridge_{isim1}_{isim2}` — Ornek: bridge_kaza_kokneden

### Hedef Attribute Adlari
- **snake_case** kullan: `kaza_tarihi`, `risk_skoru`
- **Turkce karakter kullanma**: ş→s, ç→c, ğ→g, ı→i, ö→o, ü→u, İ→i
- Kaynak sutun adini mumkun oldugunca koru, sadece convention'a uygun hale getir
- Kisaltmalar: `tar`→`tarihi`, `ack`→`aciklama` seklinde acilabilir ama zorunlu degil

### FK Sutun Convention
- `fk_{hedef_tablo}_id` — Ornek: fk_dim_birim_id, fk_dim_personel_id
- Kaynak sistemdeki FK sutunu hedef tarafta bu formata donusturulur

## 3. Audit Sutunlari Standart Mapping

### PostgreSQL Kaynak Pattern (KEY vb.)
| Kaynak | Hedef |
|--------|-------|
| created_by / olusturan | olusturan_kullanici |
| created_date / olusturma_tarihi | olusturma_tarihi |
| modified_by / guncelleyen | guncelleyen_kullanici |
| modified_date / guncelleme_tarihi | guncelleme_tarihi |

### MSSQL Kaynak Pattern (RAY vb.)
| Kaynak | Hedef |
|--------|-------|
| ek | olusturan_kullanici |
| ektar | olusturma_tarihi |
| gun | guncelleyen_kullanici |
| guntar | guncelleme_tarihi |

### Standart Audit Eki
Tum hedef tablolara eklenir:
- `etl_yuklenme_tarihi` (ETL load timestamp)
- `etl_kaynak_sistem` (kaynak sistem adi)

## 4. Soft Delete Pattern

Kaynak sistemde soft delete sutunlari:
- `sil` (boolean/flag) — Silinmis mi?
- `siltar` (datetime) — Silinme tarihi
- `fk_durum` — Kayit durumu (aktif/pasif)

Hedef tarafta:
- Bu sutunlar mapping'e dahil edilir
- ETL surecinde filtreleme kurali olarak kullanilir: `WHERE sil = 0` veya `WHERE fk_durum = aktif`
- Mapping'de not olarak belirtilir

## 5. Sablon Alanlari Doldurma Kurallari

### Source System (1. sutun)
- DB tipi yazilir: `PostgreSQL`, `MSSQL`, `Oracle`, `MySQL`

### Source System.1 (2. sutun)
- Kaynak sistem kisa adi: `KEY`, `RAY`, `SAP`, `HR`

### Master/Detail (6. sutun)
- Bir hedef tablonun **ilk satiri**: `Master`
- Ayni tablonun sonraki satirlari: bos birakilir
- Yeni hedef tablo basladiginda tekrar `Master`

### Target Schema (7. sutun)
- Ilk satir: `DW` (veya kullanicinin belirledigi sema adi)
- Sonraki satirlar: bos birakilir

### Schema Code (12. sutun)
- Format: `{MODUL}_{SENARYO}` — Ornek: KEY_KS001, RAY_KS002
- Bir attribute birden fazla senaryoda kullaniliyorsa, ilk/ana senaryo yazilir

## 6. Veri Tipi Donusumleri

Genel kurallar:
- `varchar/text` → `VARCHAR(n)` (kaynak max_uzunluk korunur)
- `integer/int` → `INTEGER`
- `bigint` → `BIGINT`
- `numeric/decimal` → `NUMERIC(p,s)` (precision/scale korunur)
- `boolean/bit` → `BOOLEAN`
- `timestamp/datetime` → `TIMESTAMP`
- `date` → `DATE`

## 7. Onemli Kurallar

1. **Metadata'da olmayan sutun UYDURULMAZ** — Her kaynak sutun metadata'da var olmali
2. **Birden fazla kaynak tablodan ayni hedef tabloya mapping yapilabilir** — Farkli kaynak tablolar ayni fact/dim'i besleyebilir
3. **Surrogate key'ler hedef tarafta eklenir** — Kaynak sistemde karsiligi olmayabilir, mapping'de `[generated]` olarak isaretlenir
4. **NULL degerler korunur** — Kaynak NULL ise hedef de NULL olur, ozel donusum yoksa
5. **Tarih formatlari standartlastirilir** — Hedef tarafta ISO 8601 (YYYY-MM-DD HH:MM:SS)
