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

## Workflow

Bu skill 6 adimdan olusur. Her adimi sirasiyla takip et.

---

### Adim 1 — Girdi Toplama

Kullanicidan asagidaki bilgileri iste:

1. **Modul/Proje adi** — Ornek: KEY, RAY, SAP, HR
2. **Connection string dosyasi veya baglanti bilgileri** — Bir veya birden fazla DB olabilir. Desteklenen formatlar:
   - JDBC format: `jdbc:postgresql://host:port/db`
   - Ayri satirlar: host, port, db, user, pass
   - Dogrudan CLI parametreleri
3. **Kullanim senaryolari / veri sozlugu dosyasi** — txt, docx, md formatinda. Mapping icin hangi tablolarin gerektigini belirler.
4. **Mapping sablon Excel dosyasi** (opsiyonel) — Varsa mevcut sablonu kullan, yoksa standart 13 sutunluk format uygula.
5. **Calisma dizini** — Cikti dosyalarinin yazilacagi yer.

Eksik bilgi varsa kullaniciya sor, devam etme.

---

### Adim 2 — Metadata Cekme

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

Metadata cikti sutunlari:
- table_schema, table_name, column_name, kolon_sirasi, data_type, max_uzunluk
- numeric_precision, numeric_scale, is_nullable, column_default
- is_primary_key, pk_constraint, is_foreign_key, fk_constraint
- referenced_schema, referenced_table, referenced_column

---

### Adim 3 — Veri Sozlugu / Kullanim Senaryosu Analizi

Kullanim senaryosu dosyasini oku ve analiz et:

1. **Mantiksal tablo adlarini cikar** — Veri sozlugundeki her veri grubunu belirle
2. **Fact/Dim/Bridge siniflandirmasi yap** — Bu dosyanin "Mapping Kurallari" bolumune bak:
   - Transactional/event verisi → **fact_**
   - Referans/lookup verisi → **dim_**
   - M:N iliski tablolari → **bridge_**
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
- Bu dosyanin "Sablon Format" bolumundeki 13 sutunluk formata uyulur

Ek detay icin: `{SKILL_DIR}/references/mapping_guidelines.md` ve `{SKILL_DIR}/references/template_format.md`

Mapping satirlari hazirlandiktan sonra:
```bash
python {SKILL_DIR}/scripts/generate_mapping.py \
  --input mapping_data.json --output ./Attribute_Level_Mapping.xlsx
```

Script, olusturulan mapping verisini 13 sutunluk standart formatta Excel'e yazar:
- Star schema naming convention (fact_, dim_, bridge_)
- Renk kodlama: fact=mavi (#DBEEF4), dim=yesil (#E2EFDA), bridge=sari (#FFF2CC)
- Header stili, freeze pane, auto-filter

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

### Star Schema Siniflandirma

| Tip | On Ek | Icerik | Ornekler |
|-----|-------|--------|----------|
| Fact | `fact_` | Transactional/event verisi, olculebilir metrikler | kazalar, riskler, denetimler |
| Dimension | `dim_` | Referans/lookup verisi, yavas degisen boyutlar | personel, birimler, hat/istasyon |
| Bridge | `bridge_` | M:N iliskileri cozen kesisim tablolari | kaza-kok_neden, tehlike-tedbir |

### Naming Conventions

- **Hedef tablo**: `fact_{isim}`, `dim_{isim}`, `bridge_{isim1}_{isim2}`
- **Hedef attribute**: snake_case, Turkce karakter yok (s→s, c→c, g→g, i→i, o→o, u→u)
- **FK sutun**: `fk_{hedef_tablo}_id` — Ornek: `fk_dim_birim_id`

### Audit Sutunlari

**PostgreSQL:** created_by→olusturan_kullanici, created_date→olusturma_tarihi, modified_by→guncelleyen_kullanici, modified_date→guncelleme_tarihi
**MSSQL:** ek→olusturan_kullanici, ektar→olusturma_tarihi, gun→guncelleyen_kullanici, guntar→guncelleme_tarihi
**Ek:** etl_yuklenme_tarihi, etl_kaynak_sistem (tum tablolara)

### Soft Delete

Kaynak: sil (flag), siltar (datetime), fk_durum. Hedef: mapping'e dahil, ETL'de WHERE sil=0 filtresi.

---

## Sablon Format (13 Sutun)

| # | Sutun | Doldurma |
|---|-------|----------|
| 1 | Source System | Her satirda: PostgreSQL, MSSQL |
| 2 | Source System.1 | Her satirda: KEY, RAY |
| 3 | Source Db | Her satirda |
| 4 | Source Schema | Her satirda: public, dbo |
| 5 | Source Table | Her satirda |
| 6 | Master/Detail | Ilk satir: Master, sonrakiler: bos |
| 7 | Target Schema | Ilk satir: DW, sonrakiler: bos |
| 8 | Source Attribute | Her satirda, metadata'dan dogrulanmis |
| 9 | Target Physical Name | Her satirda: fact_xxx, dim_xxx |
| 10 | Target Logical Name | Ilk satirda, sonrakiler: bos |
| 11 | Target Attribute | Her satirda, snake_case |
| 12 | Schema Code | Her satirda: MOD_KS001 |
| 13 | Modul | Her satirda |

Renk: fact=mavi(#DBEEF4), dim=yesil(#E2EFDA), bridge=sari(#FFF2CC)

---

## Onemli Notlar

- Metadata'da olmayan sutun mapping'e **EKLENMEZ**
- Her mapping satiri icin kaynak sutunun metadata'da var oldugu dogrulanir
- Kullanici onay vermeden bir sonraki adima gecilmez
- Hata durumunda kullaniciya bilgi verilir ve alternatif cozum onerilir
- Birden fazla DB varsa her biri icin ayri metadata cekilir
- Ornek calisma akisi icin: `{SKILL_DIR}/examples/sample_workflow.md`
