# Freezeyt sraz jedenáctý

## Review pull requestů
Sraz začal jako už klasicky review PR. První PR aktualizoval aplikaci na blog.

Následně jsme se vrhli na zkoušku ohněm a přidali další článek na blog. Článek
byl na jiném místě, takže jsme ho následně jen přesunuli, tam, kde má být.

Další PR aktualizoval dokumentační řetězce ve funkcích freeze a url_to_filename.

Poslední PR aktualizoval testy pro parse_absolute_url.

### Odbočka ke Gitu a GitHubu
Pull requesty je možné kontrolovat i jinak než na GitHubu. Změny si můžeme také
stáhnout k sobě a kontrolovat je lokálně, což je dobré v případě, že chceme
například spustit testy, nebo v případě blogu jej spustit lokálně. GitHub
v nápovědě pro merge navrhne, jak to jde udělat z příkazového řádku,
ale bohužel se tyto instrukce zobrazí jen administrátorovi repozitáře.
Dva základní příkazy: `git branch` - seznam všech větví v repozitáři
a `git pull` = `git fetch` + `git merge` (stáhne změny z GitHubu a sloučí je
s aktuálním stavem mého lokálního repozitáře). Toho se dá využít i ke stažení
jiných větví než master. Například: `git fetch --all` stáhne všechny větve
(aktualizuje je) ze všech remote repozitářů.

Návod jak na to bez nápovědy z GitHubu:
* `git fetch <jmeno_remote> <nazev_vetve>` - stáhne z GitHubu danou větev
* `git fetch refs/pull/<cislo_PR>/head` (je možné zkrátit pomocí aliasu) - stáhne
změny z daného PR
* `git pull refs/pull/<cislo_PR>/head` - začlení změny z daného PR


## Continuous Integration
Minule jsme začali s tím, aby se testy spustili pokaždé, jakmile někdo otevře PR.
Minule jsme nakonfigurovali [tox](https://tox.readthedocs.io/en/latest/) tak,
aby se spustil testy se čtyřmi verzemi Pythonu, které bude projekt podporovat.
Rozhodli jsme se, že pro to použijeme GitHub Actions.

Potom nám na GitHubu testy spadly na Pytonu 3.6, 3.7 a 3.9 a tak jsme se pustili
do debuggování. Tady končí 1. část streamu. Druhá část se věnuje debuggování
a tomu, proč testy na GitHubu nefungovaly.  Problémem bylo, že `filecmp.dircmp`
porovnává v základnám nastavení soubory tak, že kontroluje pouze jejich
vlastnosti (datum uložení, velikost, oprávnění apod.), ne obsah.

Napsali jsme test, který vytvořil 2 soubory s jiným obsahem ve stejný čas,
takže tím testujeme, co neprochází. Poté jsme test začali opravovat.

### Odbočka he Gitu č. 2
Jak dát změny z jednoho souboru do více commitů. `git add -p` poté se nám
postupně ukáží části změn a my se u nich můžeme rozhodnout, zda je v daném
commitu chceme, nebo ne.

Po změně souborů byl problém s historií commitů - jakmile v Gitu měníme historii,
můžeme to změnit při `git push` pomocí přepínače `--force-with-lease`.
Jakmile děláte force-push, měli byste vědět, co děláte.

## Plány do příště
Příští aktualizace GitHub actions by mohla být, že každý nový článek se automaticky
přidá na blog, který by byl hostovaný na [GH pages](https://pages.github.com/).

> Záznam ze srazu [zde](https://youtu.be/kFaDcOU7ZQo) a [zde](https://youtu.be/Q7ELr2clx5o).
Více informací o projektu [zde](https://tinyurl.com/freezeyt).
