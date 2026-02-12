---
name: dw-mapping
description: Veri ambari attribute-level mapping olusturma araci. Veritabanina baglanip metadata cekar, kullanim senaryolarini analiz eder, star schema mapping uretir, canli dogrulama yapar. Tetikleyiciler - "mapping olustur", "veri ambari mapping", "attribute level mapping", "DW mapping", "modul mapping", "metadata cek", "mapping dogrula".
---

# dw-mapping

Genel amacli veri ambari attribute-level mapping skill'i. Herhangi bir modul/proje/veritabani icin tekrarlanabilir DW mapping sureci.

## Triggers

- "mapping olustur"
- "veri ambari mapping"
- "attribute level mapping"
- "DW mapping"
- "modul mapping"
- "metadata cek"
- "mapping dogrula"

## Ortam Ayarlari

Bu skill'in script ve referans dosyalari bir dizinde bulunur. Calisma basinda `SKILL_DIR` degerini belirle:

**Yol bulma sirasi** (ilk bulunan kullanilir):
1. Bu dosyanin bulundugu dizin (bu dosya `SKILL.md` ise, ayni klasor `SKILL_DIR` olur)
2. `~/.claude/skills/dw-mapping/` (Claude Code varsayilan)
3. `~/.config/dw-mapping/` (genel XDG uyumlu konum)
4. Calisma dizininde `dw-mapping/` alt klasoru
5. Hicbiri yoksa: `dw-mapping.skill.md` dosyasindaki "Embedded Scripts" bolumunden script'leri calisma dizinine cikar ve orayi kullan

**Yol bulma komutu:**
```bash
for d in "$(dirname "$0")" "$HOME/.claude/skills/dw-mapping" "$HOME/.config/dw-mapping" "./dw-mapping"; do
  [ -f "$d/scripts/extract_metadata.py" ] && echo "SKILL_DIR=$d" && break
done
```

Asagidaki adimlarda `{SKILL_DIR}` gecen her yerde bu dizini kullan.

---

## Katman Mimarisi

Veri ambari 4 katmandan olusur, her katmanin ayri bir veritabani semasi vardir:

| Katman | Sema | Aciklama |
|--------|------|----------|
| Mirror | **ODS** | Kaynak sistemlerden birebir kopyalanan ham veri |
| Foundation | **DWH** | Star schema modeline donusturulmus analitik veri |
| Staging | **STG** | Ara donusum tablolari |
| Logging | **ETL** | ETL surec loglari |

Mapping sureci **ODS → DWH** donusumunu tanimlar.

---

## Workflow

Bu skill 6 adimdan olusur. Her adimi sirasiyla takip et.

---

### Adim 1 — Girdi Toplama

Kullanicidan asagidaki bilgileri iste:

1. **Modul/Proje adi** — Ornek: KEY, RAY, SAP, HR
2. **Connection string dosyasi veya baglanti bilgileri** — Calisma dizininde gecerli metadata Excel dosyasi varsa bu bilgi **gerekmez** (Adim 2'de otomatik tespit edilir). Yoksa bir veya birden fazla DB olabilir. Desteklenen formatlar:
   - JDBC format: `jdbc:postgresql://host:port/db`
   - Ayri satirlar: host, port, db, user, pass
   - Dogrudan CLI parametreleri
3. **Kullanim senaryolari / veri sozlugu dosyasi** — txt, docx, md formatinda. Mapping icin hangi tablolarin gerektigini belirler.
4. **Mapping sablon Excel dosyasi** (opsiyonel) — Varsa mevcut sablonu kullan, yoksa standart 15 sutunluk format uygula.
5. **Calisma dizini** — Cikti dosyalarinin yazilacagi yer.

Eksik bilgi varsa kullaniciya sor, devam etme.

---

### Adim 2 — Metadata Cekme

**Once mevcut metadata dosyalarini kontrol et:**

Calisma dizininde `*_db_metadata.xlsx` veya `*_metadata.xlsx` desenine uyan dosyalar ara. Bulunan her dosya icin:
1. Dosyayi ac ve sutun basliklarini oku
2. Beklenen 17 sutunun (table_schema, table_name, column_name, ..., referenced_column) mevcut oldugundan emin ol
3. Veri satirlarinin dolu oldugunu dogrula (bos dosya degilse gecerli say)

**Gecerli metadata dosyasi bulunduysa:**
- Kullaniciya bilgi ver: "Mevcut metadata dosyasi bulundu: {dosya_adi} ({satir_sayisi} satir). Bu dosya kullanilacak."
- DB baglantisi adimini **atla**, dogrudan Adim 3'e gec
- Birden fazla gecerli dosya varsa hepsini listele ve kullan

**Gecerli metadata dosyasi bulunamadiysa:**
`{SKILL_DIR}/scripts/extract_metadata.py` scriptini calistir.

Her connection string icin:
- DB tipini belirle (PostgreSQL / MSSQL / Oracle / MySQL)
- Ilgili metadata SQL'ini calistir
- Cikti: `{calisma_dizini}/{kaynak_sistem}_db_metadata.xlsx`

Ornek komut:
```bash
python {SKILL_DIR}/scripts/extract_metadata.py \
  --type postgresql --host localhost --port 5432 \
  --db keyuygulama --user postgres --pass xxx \
  --output ./key_db_metadata.xlsx
```

Connection file ile:
```bash
python {SKILL_DIR}/scripts/extract_metadata.py \
  --connection-file conn.txt --output ./metadata.xlsx
```

Metadata cikti sutunlari (17 sutun):
- table_schema, table_name, column_name, kolon_sirasi, data_type, max_uzunluk
- numeric_precision, numeric_scale, is_nullable, column_default
- is_primary_key, pk_constraint, is_foreign_key, fk_constraint
- referenced_schema, referenced_table, referenced_column

---

### Adim 3 — Veri Sozlugu / Kullanim Senaryosu Analizi

Kullanim senaryosu dosyasini oku ve analiz et:

1. **Mantiksal tablo adlarini cikar** — Veri sozlugundeki her veri grubunu belirle
2. **Fact/Dim/Bridge siniflandirmasi yap** — Bu dosyanin "Mapping Kurallari" bolumune bak:
   - Transactional/event verisi → **f_**
   - Referans/lookup verisi → **d_**
   - M:N iliski tablolari → **b_**
3. **Senaryo adimlarini hedef tablolarla eslestir** — Her senaryo adiminin hangi tablolara ihtiyac duydugunu belirle
4. **Metadata ile karsilastir** — Mantiksal tablolarin fiziksel karsiliklari metadata'da var mi kontrol et

Ek detay icin: `{SKILL_DIR}/references/mapping_guidelines.md`

Analiz sonucunu kullaniciya ozetle ve onay al.

---

### Adim 4 — Mapping Uretimi

Metadata + senaryo analizi sonucuna gore mapping satirlarini olustur.

**KRITIK KURALLAR:**
- Metadata'da olmayan sutun **UYDURULMAZ**
- Her kaynak sutun metadata'dan dogrulanir
- Bu dosyanin "Mapping Kurallari" bolumundeki convention'lara uyulur
- Bu dosyanin "Sablon Format" bolumundeki 15 sutunluk formata uyulur

Ek detay icin: `{SKILL_DIR}/references/mapping_guidelines.md` ve `{SKILL_DIR}/references/template_format.md`

Mapping satirlari hazirlandiktan sonra:
```bash
python {SKILL_DIR}/scripts/generate_mapping.py \
  --input mapping_data.json --output ./Attribute_Level_Mapping.xlsx
```

Script, olusturulan mapping verisini 15 sutunluk standart formatta Excel'e yazar:
- Star schema naming convention (f_, d_, b_)
- Renk kodlama: fact=mavi (#DBEEF4), dim=yesil (#E2EFDA), bridge=sari (#FFF2CC)
- Header stili, freeze pane, auto-filter

Ayni JSON verisinden entity-level mapping de uret:
```bash
python {SKILL_DIR}/scripts/generate_entity_mapping.py \
  --input mapping_data.json --output ./Entity_Level_Mapping.xlsx
```

Entity mapping, attribute-level verisinden her benzersiz hedef tablo icin tek satir olusturur (8 sutun).

---

### Adim 5 — Dogrulama SQL'leri ve Canli Test

Her kullanim senaryosu adimi icin:

1. **SELECT sorgusu uret** — Hangi senaryo adimi icin oldugunu yorumla belirt
2. **Canli DB'de calistir** — Sorguyu baglantida calistir
3. **Veri kalitesi kontrolleri:**
   - NULL doluluk oranlari
   - FK butunluk (referans tablosunda karsiligi var mi)
   - DISTINCT deger sayilari
   - Tarih alanlari format kontrolu
4. **Hata durumunda** — Sorguyu duzelt ve tekrar calistir. Kullaniciya bilgi ver.

Her sorgu sonucunu kaydet, Adim 6'da rapora ekle.

---

### Adim 6 — Rapor Uretimi

Calisma dizinine Markdown rapor olustur: `{modul}_mapping_raporu.md`

Rapor icerigi:
1. **Veri Varligi Ozeti** — Tablo basina kayit sayisi
2. **Senaryo Adimi Dogrulama Sonuclari** — Her adim icin BASARILI / HATA
3. **Veri Kalitesi Sorunlari** — NULL oranlar, FK kiriklar, veri anomalileri
4. **Mapping Istatistikleri:**
   - Toplam fact / dim / bridge tablo sayisi
   - Toplam attribute sayisi
   - Kaynak sistem bazinda dagılim

---

## Mapping Kurallari

### Katman Sema Kurallari

| Katman | Sema | Tablo Prefix Ornegi |
|--------|------|---------------------|
| ODS (Mirror) | `ODS` | Kaynak sistem ismi prefix: `kky_zkky_iybs_0288`, `ytp_musteri` |
| DWH (Foundation) | `DWH` | Star schema prefix: `f_tasima`, `d_musteri` |
| STG (Staging) | `STG` | Ara tablolar |
| ETL (Logging) | `ETL` | Log tablolari |

### Star Schema Siniflandirma

| Tip | On Ek | Icerik | Ornekler |
|-----|-------|--------|----------|
| Fact (Olgu) | `f_` | Transactional/event verisi, olculebilir metrikler | f_tasima, f_kaza, f_denetim |
| Dimension (Boyut) | `d_` | Referans/lookup verisi, yavas degisen boyutlar | d_musteri, d_birim, d_istasyon |
| Bridge (Kopru) | `b_` | M:N iliskileri cozen kesisim tablolari | b_kaza_kokneden, b_tehlike_tedbir |

### Naming Conventions

**Genel kurallar:**
- Tum tablo ve kolon isimlerinde **Turkce karakter kullanilmaz** (s→s, c→c, g→g, i→i, o→o, u→u)
- Tum tablo ve kolon isimlerinde **kucuk harf (lowercase)** kullanilir (Iceberg ve Trino gerekliligi)
- Kaynak sutun adini mumkun oldugunca koru, sadece convention'a uygun hale getir

**Hedef tablo isimlendirme:**
- `f_{isim}` — Ornek: f_tasima, f_kaza, f_risk
- `d_{isim}` — Ornek: d_musteri, d_birim, d_hat
- `b_{isim1}_{isim2}` — Ornek: b_kaza_kokneden

**ODS katmani tablo isimlendirme:**
- Kaynak sistem ismi prefix olarak kullanilir
- Ornek: `kky_zkky_iybs_0288`, `ytp_musteri`

**Kolon postfix kurallari:**

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

### Anahtar Kurallari

- Tum PK ve FK alanlari `_id` ile biter
- FK olarak kullanilan, `_id` ile biten her kolon icin bir boyut (d_) tablosu olmak **zorundadir**
- Fiziksel olarak PK ve FK tanimlari olusturulmaz (Iceberg kisitlamasi), ancak mantiksal modelde iliskiler korunur

### Metadata Kolonlari (Audit)

**ODS Katmani (Mirror):**

| Kolon | Aciklama |
|-------|----------|
| yukleme_tarihi | Kaydin eklendigi tarih |

**DWH Katmani (Foundation):**

| Kolon | Aciklama |
|-------|----------|
| yukleme_tarihi | Kaydin eklendigi tarih |
| yukleyen | Kaydi kimin ekledigi |
| guncelleme_tarihi | Kaydin guncellendigi tarih |
| guncelleyen | Kaydi kimin guncelledigi |
| kaynak_tablo | Kaynak tablo bilgisi |

Bu metadata kolonlari **tum hedef tablolara** otomatik eklenir.

### Soft Delete Pattern

Kaynak: `sil` (flag), `siltar` (datetime), `fk_durum` (aktif/pasif)
Hedef: mapping'e dahil edilir, ETL'de `WHERE sil = 0` filtreleme kurali olarak kullanilir.

---

## Sablon Format (15 Sutun)

| # | Sutun | Doldurma |
|---|-------|----------|
| 1 | Source System | Her satirda: PostgreSQL, MSSQL |
| 2 | Source System.1 | Her satirda: KEY, RAY |
| 3 | Source Db | Her satirda |
| 4 | Source Schema | Her satirda: public, dbo |
| 5 | Source Table | Her satirda |
| 6 | Master/Detail | Ilk satir: Master, sonrakiler: bos |
| 7 | Target Schema | Ilk satir: DWH, sonrakiler: bos |
| 8 | Source Attribute | Her satirda, metadata'dan dogrulanmis |
| 9 | Target Physical Name | Her satirda: f_xxx, d_xxx |
| 10 | Target Logical Name | Ilk satirda, sonrakiler: bos |
| 11 | Target Attribute | Her satirda, snake_case, lowercase |
| 12 | Schema Code | Her satirda: MOD_KS001 |
| 13 | Modul | Her satirda |
| 14 | Kullanim Senaryosu | Her satirda: KS_001, KS_002 |
| 15 | Senaryo Adimi | Her satirda: adim aciklamasi |

Renk: fact=mavi(#DBEEF4), dim=yesil(#E2EFDA), bridge=sari(#FFF2CC)

---

## Onemli Notlar

- Metadata'da olmayan sutun mapping'e **EKLENMEZ**
- Her mapping satiri icin kaynak sutunun metadata'da var oldugu dogrulanir
- Kullanici onay vermeden bir sonraki adima gecilmez
- Hata durumunda kullaniciya bilgi verilir ve alternatif cozum onerilir
- Birden fazla DB varsa her biri icin ayri metadata cekilir
- Ornek calisma akisi icin: `{SKILL_DIR}/examples/sample_workflow.md`
