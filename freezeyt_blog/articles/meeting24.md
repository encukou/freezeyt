# Freezeyt sraz dvacátý čtvrtý - Django & návrh konfigurace


První část srazu zabrala revize [PR 115], který do testů přidává webovku
napsanou ve frameworku Django.
Základní, nově založený projekt v Djangu je mnohem větší než stránka ve Flasku:
sestává z *projektu*, který spojuje několik *aplikací*.
Projekt se zakládá příkazem, který vytvoří adresářovou strukturu se spoustou
souborů.

[PR 115]: https://github.com/encukou/freezeyt/pull/115

Django aplikace jsou pak jednotlivé součásti, které jsou teoreticky použitelné
ve více projektech: základní projekt má aplikaci na přihlašování, administrační
rozhraní, sezení, zprávy a kdo ví co ještě.
Navíc má základní projekt jednu „hlavní“ aplikaci, kam se dává kód specifický
pro ten jeden projekt.

Každá aplikace může mít své vlastní nastavení URL.
Pod `/admin/...` se většinou dává administrační rozhraní; všechny URL co
nezačíná `/admin` se přenechá „hlavní“ aplikaci.
To se definuje v souboru `urls.py`projektu.
V rámci aplikace je pak další `urls.py`, kde se definují URL pro jednotlivé
stránky.

Každá Django aplikace může mít i své vlastní modely (tabulky v databázi).
Základní projekt obsahuje aplikaci pro správu uživatelů
(`django.contrib.auth`), která databázi používá, at tak se kolem prvního
spuštění projektu vytvoří databáze.
Základní projekt používá jednoduchou databázi `sqlite`, která ukládá data
do souboru; tenhle soubor nepatří do Gitu.

Aby bylo možné Django projekt spustit pod WSGI serverem, poskytuje základní
aplikace soubor `wsgi.py`, který vytvoří WSGI aplikaci a uloží ji do proměnné
`application`.
Pro integraci do testů ji bude potřeba dostat do proměnné `app` v `app.py`.

Další, menší problém byl v tom, že nově vytvořený projekt obsahuje spoustu
„načatých“ modulů, které jen něco importují – zbytek modulu je potřeba dopsat.
Freezeyt ale používá linter Pyflakes, kterému se nepoužité importy nelíbí
– v opravdovém kódu nejsou k ničemu.
Pyflakes nemají velké možnosti nastavení, takže se mu nedá říct aby Django
projekt ignoroval, ale můžeme tu udělat trochu podvod: nevyužité proměnné
zmínit v `__all__`.
Normálně se tak označuje API modulu: to, co modul dává k dispozici těm, kdo ho
naimportují.
Vedlejší efekt ale je že pyflakes označí proměnnou zmínějou v `__all__`
za použitou.
(Teď když, když píšu blog, mi ale přijde jednodušší nepoužité importy
zakomentovat. Až budou potřeba, dají se obnovit.)


## Konfigurace

Další část srazu jsme se věnovali vymýšlení konfigurace.
Jak by mohl vypadat konfigurační soubor, který zapíná věci které chceme
umožnit?
Aby to šlo líp přemýšleli jsme nad konkrétním příkladem/ukázkou.
Zatím konfigurák vypadá asi takhle:

```yaml
prefix: "localhost:8080"
extra_pages:
    - /extra.html
extra_files:
    /CNAME: "my.site.example"
```

Pro `extra_files` by bylo fajn umožnit vzít obsah ze souboru, ne jen z řetězce.
Takové věci se dají docela jednoduše doplnit: zatím může být obsah zadaný jen
jako řetězec (zde `"my.site.example"`, takže máme možnost místo toho použít
slovník, který se dají specifikovat nejrůznější rozšíření.
Třeba soubor, ze kterého odkaz vzít:

```
extra_files:
    /CNAME: "my.site.example"
    /favicon.ico:
        file: static/favicon.ico
```

(Tenhle konkrétní soubor by ale bylo lepší dát přímo do aplikace, ale jako
příklad to stačí.)

První rozšíření, které jsme minule navrhli, je progressbar.
Ten se by se měl dát nastavit docela jednoduše:

```yaml
progressbar: true
```

Kdyby bylo někdy potřeba víc detailů, můžeme potom povolit
použtí slovníku s detailním nastavením.
Teď ale bude stačit `True`.

Další rozšíření bude možnost vybrat, kam se bude ukládat výstup.
Může to být do adresáře, slovníku nebo Gitové větve:

```yaml
output:
    dir: "_build"
    dict: true
    git:
        repo: "."
        branch: gh-pages
```

> Spousta podobných nástrojů dává výstup do adresáře `_build` nebo `.build`.
> Je to jenom konvence; divný název umožňuje aplikaci použít `build` pro sebe.
> Varianta s tečkou navíc na Unixu soubor skryje ve výpisech (např. `ls`).

Pokecali jsme o tom, jaké by mělo být výchozí nastavení.
Mně se nelíbí ani jedno.
Ukládání do slovníku je dobré pro testy, ale větší stránky zahltí
paměť počítače.
V Gitu by nebylo hezké jen tak přepsat nějakou větev.
A adresář taky potřebuje konfiguraci: vytvořit `_build` v aktuálním adresáři
může být překvapivé, a stejně tak vždy nefunguje vytvořit adresář v rámci
Pythonního balíčku s webovou aplikací.
(Tohle dělá `frozen-flask`/`elsa` a pokud člověk nevyvíjí přímo aplikaci
ale třeba jen obsah do ní, adresář `build` se objeví schovaný kdesi ve
virtuálním prostředí.)
Nejlepší tak bude při chybějícím `output` požadovat zadání adresáře na
příkazové řádce, tak jako to děláme teď.

Teď ale máme všechny tři varianty zamíchané do sebe.
Kdyby někco začal přidávat další možnosti (např. kopírovat soubory přímo na
vzdálený server, nebo použít jiné verzovací systémy než Git.), mohly by 
v tom být docela chaos.
Stálo by za to udělat z nich seznam?

```yaml
output:
    - dir: "_build"
    - dict: true
    - git:
        repo: "."
        branch: gh-pages
```

Případně mít ve slovníku přímo klíč s typem výstupu?
(Taklhe to dělá např. Ansible)

```yaml
output:
    - type: dir
      dir: "_build"
    - type: dict
    - type: git
      repo: "."
      branch: gh-pages
```

Zapřemýšleli jsme a nepřišli jsme na důvod umožnit víc druhů výstupů.
I kdyby to bylo potřeba, dát adresář do Gitu nebo rozbalit Gitovou větev na
disk není velký problém.
A tak bude asi nejlepší umožnit jen jednu variantu:

```yaml
output:
    type: dir
    dir: "_build"
```

nebo

```yaml
output:
    type: dict
```

nebo

```yaml
output:
    type: git
    repo: "."
    branch: gh-pages
```

Další „rozšíření“ je validace.
Tady už dává smysl umožnit validátorů víc, třeba:

```
validate:
    - type: css
    - type: html
      content-types:
        - text/html
        - text/html+xml
```

Protože ale mají všechny validátory stejný klíč `type`,
daly by se nakonfigurovat i slovníkem:

```yaml
validate:
    css: true
    html:
      content-types:
        - text/html
        - text/html+xml
```

Podobně by mohlo fungovat nastavení pro sbírání odkazů:

```yaml
get_links:
    html: true
    css: true
```

Další na řadě je možnost nadefinovat adresář se statickými soubory,
které se jen nakopírují do výstupu.
Na to je potřeba znát jen začátek URL a příslušný adresář:

```yaml
static_files:
    /static/: ./static/
```

A poslední na řadě je načítání vlastních pluginů, tedy načtení nějaké
Pythonní funkce/třídy z nějakého modulu.
Na podobné věci se dá použít syntax s dvojtečkou, která odděluje jméno
modulu od jména objektu v něm:

```yaml
plugins:
    "freezeyt_validate_png:Validator"
```

Python samotný používá tečky, ale pokud jsou obsaženy jak ve jménu modulu
tak ve jménu objektu, není jasné co je potřeba naimportovat a co pak dostat
jako atribut.
Například pro funkci `PngValidator.plugin_v2` v modulu
`my_plugins.validators.png` by bylo potřeba udělat:

```python
mod = import_module('my_plugins.validators.png')
plugin = mod.PngValidator.plugin_v2
```

Dvojtečka v `my_plugins.validators.png:PngValidator.plugin_v2` ukazuje,
kde končí jméno modulu.

Výsledný návrh je [na Githubu](https://github.com/encukou/freezeyt/blob/342ed8de39/doc/plugin-notes.md).

> Záznam ze srazu se bohužel nepovedl.
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
