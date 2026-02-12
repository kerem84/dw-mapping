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

Bu dosya self-contained (script'ler dahil). Herhangi bir AI CLI tool'da kullanilabilir.

**Script'lerin calisma dizinine cikarilmasi:**
Ilk kullanimda "Embedded Scripts" bolumundeki `extract_metadata.py`, `generate_mapping.py` ve `generate_entity_mapping.py` dosyalarini calisma dizinine yaz. Sonraki adimlarda bu dosyalari dogrudan `python extract_metadata.py ...`, `python generate_mapping.py ...` ve `python generate_entity_mapping.py ...` seklinde cagir.

**Python bagimliliklar:**
```bash
pip install psycopg2-binary pymssql openpyxl pandas
```

## Kurulum (Platforma Gore)

### Claude Code
```bash
mkdir -p ~/.claude/skills/dw-mapping/scripts
cp dw-mapping.skill.md ~/.claude/skills/dw-mapping/SKILL.md
# Embedded Scripts bolumundeki dosyalari scripts/ altina cikar
```

### OpenAI Codex CLI
```bash
mkdir -p ~/.codex/instructions/
cp dw-mapping.skill.md ~/.codex/instructions/dw-mapping.md
# veya proje kokune AGENTS.md / codex.md olarak kopyala
```

### Google Gemini CLI
```bash
cp dw-mapping.skill.md GEMINI.md
# veya .gemini/settings.json icinde system_instruction olarak referans ver
```

### OpenCode
```bash
cp dw-mapping.skill.md .opencode/instructions/dw-mapping.md
# veya proje kokune INSTRUCTIONS.md olarak kopyala
```

### Aider
```bash
cp dw-mapping.skill.md .aider/conventions/dw-mapping.md
# veya --read parametresi ile: aider --read dw-mapping.skill.md
```

### ChatGPT (Custom GPT / Projects)
1. Custom GPT Instructions veya Project Instructions alanina bu dosyanin tamamini yapistir
2. Code Interpreter aktif et
3. Embedded Scripts'teki Python dosyalarini Knowledge'a yukle

### Google Gemini (Gems)
1. Yeni Gem olustur, Talimatlar alanina bu dosyanin tamamini yapistir
2. Script calistirma sinirli: Gemini SQL ve script kodunu uretir, kullanici lokal olarak calistirir

## Katman Mimarisi

Veri ambari 4 katmandan olusur, her katmanin ayri bir veritabani semasi vardir:

| Katman | Sema | Aciklama |
|--------|------|----------|
| Mirror | **ODS** | Kaynak sistemlerden birebir kopyalanan ham veri |
| Foundation | **DWH** | Star schema modeline donusturulmus analitik veri |
| Staging | **STG** | Ara donusum tablolari |
| Logging | **ETL** | ETL surec loglari |

Mapping sureci **ODS → DWH** donusumunu tanimlar.

## Workflow

Bu skill 6 adimdan olusur. Her adimi sirasiyla takip et.

> **Script yollari:** Asagidaki adimlarda `python extract_metadata.py` ve `python generate_mapping.py` komutlari gecmektedir. Bu script'ler:
> - Eger calisma dizinine cikarilmissa: `python extract_metadata.py ...`
> - Eger bir skill dizininde ise: `python {SKILL_DIR}/scripts/extract_metadata.py ...`
> - Eger script dosyasi bulunamazsa: Bu dosyanin "Embedded Scripts" bolumundeki kodu calisma dizinine yaz ve oradan calistir.

---

### Adim 1 — Girdi Toplama

Kullanicidan asagidaki bilgileri iste:

1. **Modul/Proje adi** — Ornek: KEY, RAY, SAP, HR
2. **Connection string dosyasi veya baglanti bilgileri** — Bir veya birden fazla DB olabilir. Desteklenen formatlar:
   - JDBC format: `jdbc:postgresql://host:port/db`
   - Ayri satirlar: host, port, db, user, pass
   - Dogrudan CLI parametreleri
3. **Kullanim senaryolari / veri sozlugu dosyasi** — txt, docx, md formatinda. Mapping icin hangi tablolarin gerektigini belirler.
4. **Mapping sablon Excel dosyasi** (opsiyonel) — Varsa mevcut sablonu kullan, yoksa standart 15 sutunluk format uygula.
5. **Calisma dizini** — Cikti dosyalarinin yazilacagi yer.

Eksik bilgi varsa kullaniciya sor, devam etme.

---

### Adim 2 — Metadata Cekme

`scripts/extract_metadata.py` scriptini calistir.

Her connection string icin:
- DB tipini belirle (PostgreSQL / MSSQL / Oracle / MySQL)
- Ilgili metadata SQL'ini calistir
- Cikti: `{calisma_dizini}/{kaynak_sistem}_db_metadata.xlsx`

Ornek komut:
```bash
python scripts/extract_metadata.py \
  --type postgresql --host localhost --port 5432 \
  --db keyuygulama --user postgres --pass xxx \
  --output ./key_db_metadata.xlsx
```

Connection file ile:
```bash
python scripts/extract_metadata.py \
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
2. **Fact/Dim/Bridge siniflandirmasi yap** — Mapping Kurallari bolumune bak:
   - Transactional/event verisi → **f_**
   - Referans/lookup verisi → **d_**
   - M:N iliski tablolari → **b_**
3. **Senaryo adimlarini hedef tablolarla eslestir** — Her senaryo adiminin hangi tablolara ihtiyac duydugunu belirle
4. **Metadata ile karsilastir** — Mantiksal tablolarin fiziksel karsiliklari metadata'da var mi kontrol et

Analiz sonucunu kullaniciya ozetle ve onay al.

---

### Adim 4 — Mapping Uretimi

Metadata + senaryo analizi sonucuna gore mapping satirlarini olustur.

**KRITIK KURALLAR:**
- Metadata'da olmayan sutun **UYDURULMAZ**
- Her kaynak sutun metadata'dan dogrulanir
- Mapping Kurallari bolumundeki convention'lara uyulur
- Sablon Format bolumundeki 15 sutunluk formata uyulur

Mapping satirlari hazirlandiktan sonra:
```bash
python scripts/generate_mapping.py \
  --input mapping_data.json --output ./Attribute_Level_Mapping.xlsx
```

Script, olusturulan mapping verisini 15 sutunluk standart formatta Excel'e yazar:
- Star schema naming convention (f_, d_, b_)
- Renk kodlama: fact=mavi (#DBEEF4), dim=yesil (#E2EFDA), bridge=sari (#FFF2CC)
- Header stili, freeze pane, auto-filter

Ayni JSON verisinden entity-level mapping de uret:
```bash
python scripts/generate_entity_mapping.py \
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

### Veri Tipi Donusumleri

| Kaynak | Hedef |
|--------|-------|
| varchar/text | VARCHAR(n) |
| integer/int | INTEGER |
| bigint | BIGINT |
| numeric/decimal | NUMERIC(p,s) |
| boolean/bit | BOOLEAN |
| timestamp/datetime | TIMESTAMP |
| date | DATE |

### Onemli Kurallar

1. Metadata'da olmayan sutun **UYDURULMAZ**
2. Birden fazla kaynak tablodan ayni hedef tabloya mapping yapilabilir
3. Surrogate key'ler hedef tarafta eklenir, mapping'de `[generated]` olarak isaretlenir
4. NULL degerler korunur
5. Tarih formatlari hedef tarafta ISO 8601 (YYYY-MM-DD HH:MM:SS)

---

## Sablon Format (15 Sutun)

| # | Sutun | Aciklama | Doldurma Kurali |
|---|-------|----------|-----------------|
| 1 | Source System | DB tipi | Her satirda: PostgreSQL, MSSQL |
| 2 | Source System.1 | Sistem kisa adi | Her satirda: KEY, RAY, SAP |
| 3 | Source Db | Veritabani adi | Her satirda |
| 4 | Source Schema | Sema adi | Her satirda: public, dbo |
| 5 | Source Table | Kaynak tablo | Her satirda |
| 6 | Master/Detail | Gruplama | Ilk satir: Master, sonrakiler: bos |
| 7 | Target Schema | Hedef sema | Ilk satir: DWH, sonrakiler: bos |
| 8 | Source Attribute | Kaynak sutun | Her satirda, metadata'dan dogrulanmis |
| 9 | Target Physical Name | Hedef tablo | Her satirda: f_xxx, d_xxx |
| 10 | Target Logical Name | Turkce ad | Ilk satirda, sonrakiler: bos |
| 11 | Target Attribute | Hedef sutun | Her satirda, snake_case, lowercase |
| 12 | Schema Code | Senaryo kodu | Her satirda: MOD_KS001 |
| 13 | Modul | Modul adi | Her satirda |
| 14 | Kullanim Senaryosu | Senaryo kodu | Her satirda: KS_001, KS_002 |
| 15 | Senaryo Adimi | Adim aciklamasi | Her satirda: adim aciklamasi |

### Master/Detail Mantigi

```
Source Table | Master/Detail | Target Physical Name | Source Attribute | Target Attribute
------------ | ------------- | -------------------- | --------------- | ----------------
kazaraporu   | Master        | f_kaza               | id              | kaza_id
kazaraporu   |               | f_kaza               | kazatarihi      | kaza_tarihi
birimler     | Master        | d_birim              | id              | birim_id
birimler     |               | d_birim              | birimadi        | birim_adi
```

### Renk Kodlama (Excel)

- **Mavi (#DBEEF4)**: f_ tablolari (fact)
- **Yesil (#E2EFDA)**: d_ tablolari (dimension)
- **Sari (#FFF2CC)**: b_ tablolari (bridge)
- **Header**: Koyu mavi (#4472C4), beyaz bold, Calibri 10pt

---

## Ornek Calisma Akisi

### Connection String Dosya Formatlari

**Satir bazli (conn_key.txt):**
```
type=postgresql
host=10.0.1.50
port=5432
db=keyuygulama
user=etl_user
pass=***
```

**JDBC (conn_ray.txt):**
```
jdbc:sqlserver://10.0.1.60:1433;databaseName=ray_db
user=etl_user
pass=***
```

### Analiz Sonucu Ornegi

| Mantiksal Grup | Fiziksel Tablo | Tip | Hedef Tablo |
|----------------|----------------|-----|-------------|
| Kaza Master | kazaincelemeraporu | fact | f_kaza |
| Kaza Kok Neden | kazakokneden | bridge | b_kaza_kokneden |
| Birimler | birimler | dim | d_birim |
| Risk Matrisi | riskmatris | fact | f_risk |

### Mapping Cikti Ornegi

```
Source System | Source System.1 | Source Db   | Source Schema | Source Table       | M/D    | Target Schema | Source Attribute | Target Physical | Target Logical | Target Attribute   | Schema Code | Modul | Kullanim Senaryosu | Senaryo Adimi
PostgreSQL    | KEY             | keyuygulama | public        | kazaincelemeraporu | Master | DWH           | id               | f_kaza          | Kaza Master    | kaza_id            | KEY_KS001   | KEY   | KS_001             | Kaza-Risk Korelasyon
PostgreSQL    | KEY             | keyuygulama | public        | kazaincelemeraporu |        |               | kazatarihi       | f_kaza          |                | kaza_tarihi        | KEY_KS001   | KEY   | KS_001             | Kaza-Risk Korelasyon
MSSQL         | RAY             | ray_db      | dbo           | riskmatris         | Master | DWH           | IND              | f_risk          | Risk Matrisi   | risk_id            | KEY_KS001   | KEY   | KS_001             | Risk Onceliklendirme
```

### Referans Degerler (KEY Modulu)

- 49 kaynak tablo, 597 toplam attribute
- 20 fact, 22 dim, 7 bridge tablo
- 8 kullanim senaryosu (KS_001 - KS_008)
- 2 kaynak sistem: KEY (PostgreSQL), RAY (MSSQL)

---

## Embedded Scripts

### extract_metadata.py

```python
#!/usr/bin/env python3
"""
Genel amacli veritabani metadata cekici.
Desteklenen DB tipleri: PostgreSQL, MSSQL
Cikti: Excel dosyasi (openpyxl + pandas)

Kullanim:
  python extract_metadata.py --type postgresql --host X --port 5432 --db mydb --user U --pass P --output metadata.xlsx
  python extract_metadata.py --type mssql --host X --port 1433 --db mydb --user U --pass P --output metadata.xlsx
  python extract_metadata.py --connection-file conn.txt --output metadata.xlsx
"""

import argparse
import sys
import re
import pandas as pd

METADATA_COLUMNS = [
    "table_schema", "table_name", "column_name", "kolon_sirasi",
    "data_type", "max_uzunluk", "numeric_precision", "numeric_scale",
    "is_nullable", "column_default", "is_primary_key", "pk_constraint",
    "is_foreign_key", "fk_constraint", "referenced_schema",
    "referenced_table", "referenced_column"
]

POSTGRESQL_SQL = """
SELECT
    c.table_schema,
    c.table_name,
    c.column_name,
    c.ordinal_position AS kolon_sirasi,
    c.data_type,
    c.character_maximum_length AS max_uzunluk,
    c.numeric_precision,
    c.numeric_scale,
    c.is_nullable,
    c.column_default,
    CASE WHEN pk.column_name IS NOT NULL THEN 'YES' ELSE 'NO' END AS is_primary_key,
    pk.constraint_name AS pk_constraint,
    CASE WHEN fk.column_name IS NOT NULL THEN 'YES' ELSE 'NO' END AS is_foreign_key,
    fk.constraint_name AS fk_constraint,
    ccu.table_schema AS referenced_schema,
    ccu.table_name AS referenced_table,
    ccu.column_name AS referenced_column
FROM information_schema.columns c
LEFT JOIN (
    SELECT kcu.table_schema, kcu.table_name, kcu.column_name, kcu.constraint_name
    FROM information_schema.key_column_usage kcu
    JOIN information_schema.table_constraints tc
        ON kcu.constraint_name = tc.constraint_name
        AND kcu.table_schema = tc.table_schema
    WHERE tc.constraint_type = 'PRIMARY KEY'
) pk ON c.table_schema = pk.table_schema
    AND c.table_name = pk.table_name
    AND c.column_name = pk.column_name
LEFT JOIN (
    SELECT kcu.table_schema, kcu.table_name, kcu.column_name, kcu.constraint_name
    FROM information_schema.key_column_usage kcu
    JOIN information_schema.table_constraints tc
        ON kcu.constraint_name = tc.constraint_name
        AND kcu.table_schema = tc.table_schema
    WHERE tc.constraint_type = 'FOREIGN KEY'
) fk ON c.table_schema = fk.table_schema
    AND c.table_name = fk.table_name
    AND c.column_name = fk.column_name
LEFT JOIN information_schema.constraint_column_usage ccu
    ON fk.constraint_name = ccu.constraint_name
    AND c.table_schema = fk.table_schema
WHERE c.table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY c.table_schema, c.table_name, c.ordinal_position;
"""

MSSQL_SQL = """
SELECT
    s.name AS table_schema,
    t.name AS table_name,
    c.name AS column_name,
    c.column_id AS kolon_sirasi,
    ty.name AS data_type,
    c.max_length AS max_uzunluk,
    c.[precision] AS numeric_precision,
    c.scale AS numeric_scale,
    CASE WHEN c.is_nullable = 1 THEN 'YES' ELSE 'NO' END AS is_nullable,
    dc.definition AS column_default,
    CASE WHEN pk_col.column_id IS NOT NULL THEN 'YES' ELSE 'NO' END AS is_primary_key,
    pk_kc.name AS pk_constraint,
    CASE WHEN fk_col.parent_column_id IS NOT NULL THEN 'YES' ELSE 'NO' END AS is_foreign_key,
    fk_obj.name AS fk_constraint,
    ref_s.name AS referenced_schema,
    ref_t.name AS referenced_table,
    ref_c.name AS referenced_column
FROM sys.columns c
JOIN sys.tables t ON c.object_id = t.object_id
JOIN sys.schemas s ON t.schema_id = s.schema_id
JOIN sys.types ty ON c.user_type_id = ty.user_type_id
LEFT JOIN sys.default_constraints dc ON c.default_object_id = dc.object_id
LEFT JOIN (
    SELECT ic.object_id, ic.column_id, kc.name
    FROM sys.index_columns ic
    JOIN sys.indexes i ON ic.object_id = i.object_id AND ic.index_id = i.index_id
    JOIN sys.key_constraints kc ON i.object_id = kc.parent_object_id AND i.index_id = kc.unique_index_id
    WHERE i.is_primary_key = 1
) pk_col ON c.object_id = pk_col.object_id AND c.column_id = pk_col.column_id
LEFT JOIN (
    SELECT ic.object_id, ic.column_id, kc.name
    FROM sys.index_columns ic
    JOIN sys.indexes i ON ic.object_id = i.object_id AND ic.index_id = i.index_id
    JOIN sys.key_constraints kc ON i.object_id = kc.parent_object_id AND i.index_id = kc.unique_index_id
    WHERE i.is_primary_key = 1
) pk_kc ON c.object_id = pk_kc.object_id AND c.column_id = pk_kc.column_id
LEFT JOIN sys.foreign_key_columns fk_col
    ON c.object_id = fk_col.parent_object_id AND c.column_id = fk_col.parent_column_id
LEFT JOIN sys.foreign_keys fk_obj
    ON fk_col.constraint_object_id = fk_obj.object_id
LEFT JOIN sys.tables ref_t ON fk_col.referenced_object_id = ref_t.object_id
LEFT JOIN sys.schemas ref_s ON ref_t.schema_id = ref_s.schema_id
LEFT JOIN sys.columns ref_c
    ON fk_col.referenced_object_id = ref_c.object_id
    AND fk_col.referenced_column_id = ref_c.column_id
ORDER BY s.name, t.name, c.column_id;
"""


def parse_connection_file(filepath):
    """Connection string dosyasini parse et."""
    config = {}
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()

    jdbc_pg = re.match(r"jdbc:postgresql://([^:]+):(\d+)/(\S+)", content)
    if jdbc_pg:
        config["type"] = "postgresql"
        config["host"] = jdbc_pg.group(1)
        config["port"] = int(jdbc_pg.group(2))
        config["db"] = jdbc_pg.group(3)

    jdbc_ms = re.match(r"jdbc:sqlserver://([^:;]+)(?::(\d+))?.*?databaseName=(\S+)", content)
    if jdbc_ms:
        config["type"] = "mssql"
        config["host"] = jdbc_ms.group(1)
        config["port"] = int(jdbc_ms.group(2)) if jdbc_ms.group(2) else 1433
        config["db"] = jdbc_ms.group(3)

    for line in content.splitlines():
        line = line.strip()
        if "=" in line:
            key, val = line.split("=", 1)
            key = key.strip().lower()
            val = val.strip()
            if key in ("type", "dbtype", "db_type"):
                config["type"] = val.lower()
            elif key in ("host", "server"):
                config["host"] = val
            elif key in ("port",):
                config["port"] = int(val)
            elif key in ("db", "database", "dbname"):
                config["db"] = val
            elif key in ("user", "username"):
                config["user"] = val
            elif key in ("pass", "password"):
                config["pass"] = val

    return config


def connect_postgresql(config):
    import psycopg2
    return psycopg2.connect(
        host=config["host"],
        port=config.get("port", 5432),
        dbname=config["db"],
        user=config["user"],
        password=config["pass"],
    )


def connect_mssql(config):
    import pymssql
    return pymssql.connect(
        server=config["host"],
        port=config.get("port", 1433),
        database=config["db"],
        user=config["user"],
        password=config["pass"],
    )


def fetch_metadata(config):
    db_type = config["type"].lower()
    if db_type == "postgresql":
        conn = connect_postgresql(config)
        sql = POSTGRESQL_SQL
    elif db_type == "mssql":
        conn = connect_mssql(config)
        sql = MSSQL_SQL
    else:
        raise ValueError(f"Desteklenmeyen DB tipi: {db_type}. Desteklenen: postgresql, mssql")

    try:
        df = pd.read_sql(sql, conn)
        df.columns = METADATA_COLUMNS[: len(df.columns)]
        return df
    finally:
        conn.close()


def write_excel(df, output_path):
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Metadata")
        ws = writer.sheets["Metadata"]

        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=10)
        thin_border = Border(
            left=Side(style="thin"), right=Side(style="thin"),
            top=Side(style="thin"), bottom=Side(style="thin"),
        )

        for col_idx, col_name in enumerate(df.columns, 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", wrap_text=True)
            cell.border = thin_border

        for row in range(2, len(df) + 2):
            for col in range(1, len(df.columns) + 1):
                ws.cell(row=row, column=col).border = thin_border

        for col_idx, col_name in enumerate(df.columns, 1):
            max_len = max(len(str(col_name)), df.iloc[:, col_idx - 1].astype(str).str.len().max())
            ws.column_dimensions[ws.cell(row=1, column=col_idx).column_letter].width = min(max_len + 2, 30)

        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions

    print(f"Metadata yazildi: {output_path} ({len(df)} satir)")


def main():
    parser = argparse.ArgumentParser(description="Veritabani metadata cekici")
    parser.add_argument("--type", choices=["postgresql", "mssql"], help="DB tipi")
    parser.add_argument("--host", help="DB host")
    parser.add_argument("--port", type=int, help="DB port")
    parser.add_argument("--db", help="Veritabani adi")
    parser.add_argument("--user", help="Kullanici adi")
    parser.add_argument("--pass", dest="password", help="Sifre")
    parser.add_argument("--connection-file", help="Connection string dosyasi")
    parser.add_argument("--output", required=True, help="Cikti Excel dosya yolu")
    args = parser.parse_args()

    if args.connection_file:
        config = parse_connection_file(args.connection_file)
        if args.type: config["type"] = args.type
        if args.user: config["user"] = args.user
        if args.password: config["pass"] = args.password
    else:
        if not all([args.type, args.host, args.db, args.user, args.password]):
            parser.error("--type, --host, --db, --user, --pass gerekli (veya --connection-file)")
        config = {
            "type": args.type, "host": args.host, "port": args.port,
            "db": args.db, "user": args.user, "pass": args.password,
        }

    print(f"Baglaniyor: {config['type']}://{config['host']}:{config.get('port', 'default')}/{config['db']}")
    df = fetch_metadata(config)
    write_excel(df, args.output)
    print("Tamamlandi.")


if __name__ == "__main__":
    main()
```

### generate_mapping.py

```python
#!/usr/bin/env python3
"""
Mapping Excel uretici yardimci modul.
Olusturulan mapping satirlarini 15 sutunluk standart formatta Excel'e yazar.

Kullanim:
  python generate_mapping.py --input mapping_data.json --output Attribute_Level_Mapping.xlsx

Girdi JSON formati:
[
  {
    "source_system": "PostgreSQL",
    "source_system_short": "KEY",
    "source_db": "keyuygulama",
    "source_schema": "public",
    "source_table": "kazaincelemeraporu",
    "master_detail": "Master",
    "target_schema": "DWH",
    "source_attribute": "kazatarihi",
    "target_physical_name": "f_kaza",
    "target_logical_name": "Kaza Master",
    "target_attribute": "kaza_tarihi",
    "schema_code": "KEY_KS001",
    "modul": "KEY",
    "kullanim_senaryosu": "KS_001",
    "senaryo_adimi": "Kaza-Risk Korelasyon"
  }
]
"""

import json
import argparse
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

TEMPLATE_COLUMNS = [
    "Source System", "Source System.1", "Source Db", "Source Schema",
    "Source Table", "Master/Detail", "Target Schema", "Source Attribute",
    "Target Physical Name", "Target Logical Name", "Target Attribute",
    "Schema Code", "Modul", "Kullanim Senaryosu", "Senaryo Adimi",
]

JSON_KEY_MAP = {
    "source_system": "Source System",
    "source_system_short": "Source System.1",
    "source_db": "Source Db",
    "source_schema": "Source Schema",
    "source_table": "Source Table",
    "master_detail": "Master/Detail",
    "target_schema": "Target Schema",
    "source_attribute": "Source Attribute",
    "target_physical_name": "Target Physical Name",
    "target_logical_name": "Target Logical Name",
    "target_attribute": "Target Attribute",
    "schema_code": "Schema Code",
    "modul": "Modul",
    "kullanim_senaryosu": "Kullanim Senaryosu",
    "senaryo_adimi": "Senaryo Adimi",
}

FACT_FILL = PatternFill(start_color="DBEEF4", end_color="DBEEF4", fill_type="solid")
DIM_FILL = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
BRIDGE_FILL = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
HEADER_FILL = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=10, name="Calibri")
DATA_FONT = Font(size=10, name="Calibri")
THIN_BORDER = Border(
    left=Side(style="thin"), right=Side(style="thin"),
    top=Side(style="thin"), bottom=Side(style="thin"),
)

COLUMN_WIDTHS = {
    "Source System": 15, "Source System.1": 14, "Source Db": 18,
    "Source Schema": 14, "Source Table": 28, "Master/Detail": 14,
    "Target Schema": 14, "Source Attribute": 28, "Target Physical Name": 28,
    "Target Logical Name": 24, "Target Attribute": 28, "Schema Code": 14, "Modul": 10,
    "Kullanim Senaryosu": 22, "Senaryo Adimi": 28,
}


def get_row_fill(target_physical_name):
    if not target_physical_name:
        return None
    name = target_physical_name.lower()
    if name.startswith("f_"):
        return FACT_FILL
    elif name.startswith("d_"):
        return DIM_FILL
    elif name.startswith("b_"):
        return BRIDGE_FILL
    return None


def generate_excel(rows, output_path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Attribute_Level_Mapping"

    for col_idx, col_name in enumerate(TEMPLATE_COLUMNS, 1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER

    for row_idx, row_data in enumerate(rows, 2):
        target_phys = row_data.get("target_physical_name", "")
        row_fill = get_row_fill(target_phys)

        for col_idx, col_name in enumerate(TEMPLATE_COLUMNS, 1):
            json_key = None
            for k, v in JSON_KEY_MAP.items():
                if v == col_name:
                    json_key = k
                    break
            value = row_data.get(json_key, "") if json_key else ""
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.font = DATA_FONT
            cell.border = THIN_BORDER
            cell.alignment = Alignment(vertical="center")
            if row_fill:
                cell.fill = row_fill

    for col_idx, col_name in enumerate(TEMPLATE_COLUMNS, 1):
        col_letter = ws.cell(row=1, column=col_idx).column_letter
        ws.column_dimensions[col_letter].width = COLUMN_WIDTHS.get(col_name, 15)

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    ws.row_dimensions[1].height = 30

    wb.save(output_path)
    print(f"Mapping Excel yazildi: {output_path} ({len(rows)} satir)")

    facts = set()
    dims = set()
    bridges = set()
    for r in rows:
        tp = r.get("target_physical_name", "").lower()
        if tp.startswith("f_"): facts.add(tp)
        elif tp.startswith("d_"): dims.add(tp)
        elif tp.startswith("b_"): bridges.add(tp)

    print(f"Istatistik: {len(facts)} fact, {len(dims)} dim, {len(bridges)} bridge tablo")
    print(f"Toplam attribute: {len(rows)}")


def main():
    parser = argparse.ArgumentParser(description="Mapping Excel uretici")
    parser.add_argument("--input", required=True, help="Girdi JSON dosyasi")
    parser.add_argument("--output", required=True, help="Cikti Excel dosya yolu")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        rows = json.load(f)

    if not isinstance(rows, list):
        print("Hata: JSON dosyasi bir liste (array) icermeli.", file=sys.stderr)
        sys.exit(1)

    generate_excel(rows, args.output)
    print("Tamamlandi.")


if __name__ == "__main__":
    main()
```

### generate_entity_mapping.py

```python
#!/usr/bin/env python3
"""
Entity Level Mapping Excel uretici.
Attribute-level mapping JSON verisinden entity-level ozet uretir.
Her benzersiz hedef tablo (Target Physical Name) icin tek satir yazar.

Kullanim:
  python generate_entity_mapping.py --input mapping_data.json --output Entity_Level_Mapping.xlsx

Girdi: generate_mapping.py ile ayni JSON formati (mapping_data.json)
Cikti: 8 sutunluk Entity_Level_Mapping.xlsx
"""

import json
import argparse
import sys
from collections import OrderedDict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

TEMPLATE_COLUMNS = [
    "Target Schema", "Target Physical Name", "Target Logical Name",
    "Source System", "Source Db", "Source Schema", "Source Table", "Modul",
]

HEADER_FILL = PatternFill(start_color="A5A5A5", end_color="A5A5A5", fill_type="solid")
HEADER_FONT = Font(bold=True, size=10, name="Calibri")
DATA_FONT = Font(size=10, name="Calibri")
THIN_BORDER = Border(
    left=Side(style="thin"), right=Side(style="thin"),
    top=Side(style="thin"), bottom=Side(style="thin"),
)

COLUMN_WIDTHS = {
    "Target Schema": 16, "Target Physical Name": 28, "Target Logical Name": 28,
    "Source System": 15, "Source Db": 18, "Source Schema": 14, "Source Table": 28, "Modul": 10,
}


def aggregate_entities(rows):
    entities = OrderedDict()
    for row in rows:
        target_phys = row.get("target_physical_name", "")
        if not target_phys:
            continue
        if target_phys not in entities:
            entities[target_phys] = {
                "target_schema": "dwh",
                "target_physical_name": target_phys,
                "target_logical_name": row.get("target_logical_name", ""),
                "source_system": row.get("source_system", ""),
                "source_db": row.get("source_db", ""),
                "source_schema": row.get("source_schema", ""),
                "source_table": row.get("source_table", ""),
                "modul": row.get("modul", ""),
            }
        else:
            if not entities[target_phys]["target_logical_name"]:
                logical = row.get("target_logical_name", "")
                if logical:
                    entities[target_phys]["target_logical_name"] = logical
    return list(entities.values())


def generate_entity_excel(entity_rows, output_path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Source-DWH"

    key_map = {
        "target_schema": "Target Schema", "target_physical_name": "Target Physical Name",
        "target_logical_name": "Target Logical Name", "source_system": "Source System",
        "source_db": "Source Db", "source_schema": "Source Schema",
        "source_table": "Source Table", "modul": "Modul",
    }
    reverse_map = {v: k for k, v in key_map.items()}

    for col_idx, col_name in enumerate(TEMPLATE_COLUMNS, 1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER

    for row_idx, row_data in enumerate(entity_rows, 2):
        for col_idx, col_name in enumerate(TEMPLATE_COLUMNS, 1):
            json_key = reverse_map.get(col_name, "")
            value = row_data.get(json_key, "") if json_key else ""
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.font = DATA_FONT
            cell.border = THIN_BORDER
            cell.alignment = Alignment(vertical="center")

    for col_idx, col_name in enumerate(TEMPLATE_COLUMNS, 1):
        col_letter = ws.cell(row=1, column=col_idx).column_letter
        ws.column_dimensions[col_letter].width = COLUMN_WIDTHS.get(col_name, 15)

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    ws.row_dimensions[1].height = 30

    wb.save(output_path)
    print(f"Entity Mapping Excel yazildi: {output_path} ({len(entity_rows)} entity)")


def main():
    parser = argparse.ArgumentParser(description="Entity Level Mapping Excel uretici")
    parser.add_argument("--input", required=True, help="Girdi JSON dosyasi")
    parser.add_argument("--output", required=True, help="Cikti Excel dosya yolu")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        rows = json.load(f)

    if not isinstance(rows, list):
        print("Hata: JSON dosyasi bir liste (array) icermeli.", file=sys.stderr)
        sys.exit(1)

    entity_rows = aggregate_entities(rows)
    generate_entity_excel(entity_rows, args.output)
    print("Tamamlandi.")


if __name__ == "__main__":
    main()
```

---

## Platform Karsilastirmasi

| Ozellik | Claude Code | ChatGPT | Gemini |
|---------|-------------|---------|--------|
| Skill otomatik yukleme | Evet | Hayir (manuel) | Hayir (manuel) |
| Script calistirma | Evet (terminal) | Code Interpreter | Sinirli |
| DB'ye dogrudan baglanti | Evet | Hayir | Hayir |
| Excel uretimi | Evet (script) | Code Interpreter | Lokal script |
| Canli SQL dogrulama | Evet | Hayir | Hayir |

Claude Code tum adimlari uctan uca otomatik yurutebilir. ChatGPT ve Gemini'de DB baglantisi ve SQL calistirma adimlari manuel yapilmalidir.

## Hizli Baslangic

```
Kullanici: "KEY modulu icin attribute level mapping olustur"

AI:  Su bilgilere ihtiyacim var:
     1. Connection string veya baglanti bilgileri?
     2. Veri sozlugu / kullanim senaryosu dosyasi?
     3. Cikti dizini?

Kullanici: [bilgileri verir]

AI:  [metadata cekar -> analiz eder -> mapping uretir -> dogrular -> raporlar]
```
