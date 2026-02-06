# DW-Mapping: Veri Ambari Attribute-Level Mapping Araci

Herhangi bir veritabani ve modul icin **tekrarlanabilir** veri ambari (Data Warehouse) mapping sureci yuruten bir AI skill/prompt paketidir. Veritabanina baglanir, metadata cekar, kullanim senaryolarini analiz eder, star schema mapping uretir, canli dogrulama yapar ve raporlar.

## Ne Yapar?

Bir veri ambari projesinde kaynak sistemlerden hedef DW tablolarina attribute-level mapping olusturma surecini otomatiklestirir:

1. **Metadata Cekme** — PostgreSQL veya MSSQL veritabanina baglanip tablo/sutun/PK/FK bilgilerini Excel'e cikarir
2. **Senaryo Analizi** — Veri sozlugu ve kullanim senaryolarini okuyup mantiksal tablolari fact/dim/bridge olarak siniflandirir
3. **Mapping Uretimi** — 13 sutunluk standart sablonda, renk kodlamali (fact=mavi, dim=yesil, bridge=sari) Excel uretir
4. **Canli Dogrulama** — Uretilen mapping'i kaynak DB uzerinde SQL sorgulariyla dogrular
5. **Raporlama** — Veri varligi ozeti, kalite kontrolleri ve mapping istatistikleri iceren Markdown rapor olusturur

### Temel Kurallar

- Metadata'da olmayan sutun **uydurulmaz** — her kaynak sutun veritabanindan dogrulanir
- Star schema naming convention: `fact_`, `dim_`, `bridge_` on ekleri
- Hedef attribute'lar snake_case, Turkce karakter icermez
- Audit sutunlari (olusturan, guncelleyen, tarihler) standart esleme ile map'lenir

## Dosya Yapisi

```
dw-mapping/
├── SKILL.md                            # Ana workflow tanimi (6 adim)
├── README.md                           # Bu dosya
├── scripts/
│   ├── extract_metadata.py             # DB metadata cekici (PostgreSQL/MSSQL)
│   └── generate_mapping.py             # Mapping Excel uretici (13 sutun, renk kodlamali)
├── references/
│   ├── mapping_guidelines.md           # DW kurallari, naming conventions, audit mapping
│   └── template_format.md              # Attribute_Level_Mapping sablon sutun tanimlari
└── examples/
    └── sample_workflow.md              # Uctan uca ornek akis
```

## Gereksinimler

```bash
pip install psycopg2-binary pymssql openpyxl pandas
```

## Kurulum

Iki kurulum secenegi vardir:
- **Ayrik dosyalar**: Skill dizini olarak kopyala (Claude Code, gelistirme ortami)
- **Tek dosya**: `dw-mapping.skill.md` tum icerigi (script'ler dahil) icerir, herhangi bir tool'a dogrudan yapistirilar

### AI CLI Tool'lar (Terminal Tabanli)

| Tool | Komut |
|------|-------|
| **Claude Code** | `cp -r dw-mapping/ ~/.claude/skills/dw-mapping/` |
| **OpenAI Codex CLI** | `cp dw-mapping.skill.md ~/.codex/skills/dw-mapping/dw-mapping.md` |
| **Gemini CLI** | `cp dw-mapping.skill.md GEMINI.md` (proje kokune) |
| **OpenCode** | `cp dw-mapping.skill.md .config/opencode/skills/dw-mapping/dw-mapping.md` |
| **Aider** | `aider --read dw-mapping.skill.md` veya `.aider/conventions/` altina kopyala |
| **Cursor** | `.cursor/rules/` altina kopyala veya Rules ayarindan ekle |

> **Not:** Claude Code haricinde `dw-mapping.skill.md` (tek dosya, script'ler gomulu) kullanin.
> Claude Code icin ayrik dosya yapisi (`SKILL.md` + `scripts/` + `references/`) daha iyidir cunku skill sistemi otomatik yukler.

### Web Tabanli AI Platformlar

#### ChatGPT (Custom GPT veya Project)

**Custom GPT:**
1. GPT Editor'de yeni GPT olustur
2. Instructions alanina `dw-mapping.skill.md` icerigini yapistir
3. Code Interpreter aktif et
4. Script dosyalarini Knowledge'a yukle

**Project:**
1. Yeni Project olustur, Instructions'a `dw-mapping.skill.md` yapistir
2. Files'a script dosyalarini yukle

> **Sinirlilik:** ChatGPT sandbox'ta calisir, DB'ye dogrudan baglanamaz. Metadata'yi onceden cekin ve Excel olarak yukleyin.

#### Google Gemini (Gems)

1. Yeni Gem olustur
2. Talimatlar alanina `dw-mapping.skill.md` icerigini yapistir

> **Sinirlilik:** Script calistirma sinirli. Gemini SQL/script kodu uretir, kullanici lokal olarak calistirir.

---

## Platform Karsilastirmasi

| Ozellik | CLI Tool'lar | ChatGPT | Gemini Web |
|---------|-------------|---------|------------|
| Script calistirma | Evet | Code Interpreter (sandbox) | Sinirli |
| DB'ye dogrudan baglanti | Evet | Hayir | Hayir |
| Excel uretimi | Evet | Code Interpreter | Lokal script |
| Canli SQL dogrulama | Evet | Hayir | Hayir |
| Dosya sistemi erisimi | Evet | Sandbox | Hayir |

**CLI tool'lar** (Claude Code, Codex, Gemini CLI, OpenCode, Aider) tum adimlari uctan uca otomatik yurutebilir. Web platformlarinda (ChatGPT, Gemini) DB baglantisi ve SQL calistirma adimlari manuel yapilir.

## Hizli Baslangic

```
Sen: "KEY modulu icin attribute level mapping olustur"

AI:  Tamam, su bilgilere ihtiyacim var:
     1. Connection string veya baglanti bilgileri?
     2. Veri sozlugu / kullanim senaryosu dosyasi?
     3. Cikti dizini?

Sen: [bilgileri verir]

AI:  [metadata cekar → analiz eder → mapping uretir → dogrular → raporlar]
```
