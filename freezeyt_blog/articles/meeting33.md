# Freezeyt sraz třicátý třetí - info pro nově příchozí

## O čem projekt je?
🎉 Dneska se k nám připojili noví členové,
tak jsme na úvod zařadili info o projektu a krátké demo jeho použití.

Abychom shrnuli o čem projekt je: první potřebujeme vytvořit webovou aplikaci
(třeba ve webovém fremeworku [Flask](https://flask.palletsprojects.com/en/1.1.x/).
Příkazem `flask run` se spustí jednoduchý server.
Chceme-li tyto stránky publikovat, existuje mnoho možností, jak to udělat.
Jedna z těchto možností je nasadit ji na server statických stránek.
Na takovém serveru žádná aplikace neběží.
Tento server jen „naservíruje“ stránky, které jsou někde uložené na disku.
Na takové stránce nemůžeme mít třeba přihlašování, protože to je dynamická věc.
To, že máme statické stránky přináší pár výhod, jednou z nich je to,
že nemusíme platit drahé servery, na kterých něco běží.

## Co se skrývá v kódu freezeyt?
Následovala exkurze kódem projektu.

### Freezeyt

V základu zmrazení stránky začne zmrazením hlavní stránky.
Pak freezeyt tuto stránku projde a najde na ní odkazy,
ty si uloží a následně zmrazí stránky, které jsou na těchto odkazech.
Ta se projde, tam se najdou odkazy a zmrazí se stránky na hlavních odkazech.

Poté jsme prošli kód po jednotlivých souborech.

Začali jsme v souboru *freezer.py*.
V něm je třída `Freezer`, při inicializaci objektu třídy se vytvoří objekt s konfigurací.
Následně se vytvoří seznam stránek, o kterých freezer ví a ještě je nenavštívil.
Zavolá se freezer dle toho, jak chceme stránky zamrazit
(buď do souboru nebo do slovníku).
Vrátí se informace z těch stránek. Ty se uloží a pak se ty stránky projdou
a najdou se na nich všechny odkazy. Ty se přidají do seznamu nenavštívených odkazů.
V tomto souboru je i funkce `freeze`, která vytvoří instanci třídy,
a zavolá potřebné metody, tahle funkce slouží pro používání z Pythonu.

Soubor *\_\_init\_\_.py* dává k dispozici třídu `Freezer` a funkci `freeze`.

Dále *freezer.py* obsahuje funkci `check_mimetype`, která kontroluje,
že přípona souboru odpovídá typu souboru, který poslala aplikace.

Následně jsme se podívali na konfiguraci freezeytu.
Tu můžeme dodat buď pomocí slovníku, nebo pomocí souboru.
Jedna z důležitých věcí, kterou můžeme nakonfigurovat je `prefix` aplikace,
ten zajistí, že odkazy budou odkazovat tam, kam mají.
Také se dle něj dá poznat, zda je odkaz externí, nebo ne.
Další možností konfigurace je to, kam se bude výsledek ukládat a to zda do
adresáře na disk, nebo do slovníku. Ukládání do slovníku je hlavně kvůli testům,
při ukládání do slovníku je tam také metoda, která kontroluje, že výsledek
dostaneme zpět.

Je tam také interní funkce `_add_extra_pages`, která přidá stránky,
na které nevedou žádné odkazy z aplikace.

Na chvíli jsme se zastavili u WSGI.
Je to rozhraní, které je definováno v [PEP 3333](https://www.python.org/dev/peps/pep-3333/).
Všechny Pythonní webové aplikace by měly být kompatibilní s tímto rozhraním.
My vlastně píšeme nový server, náš freezer musí být schopen spolupracovat
s tímto rozhraním.
To hlavní je, že máme aplikaci, kterou zavoláme jako funkci.
Předáme jí slovník s požadavky a funkci `start_response`.
V této funkci jsou hlavičky, typ souboru apod.
Ve freezeytu máme metodu na uložení hlaviček a kontrolu status kódu.

Z hlaviček zjistíme, jaký je to dokument, pokud je to soubor typu HTML,
nebo CSS, podíváme se do těchto souborů a zkontrolujeme,
zda v nich nejsou další odkazy.
Funkce `get_all_links` a `get_all_links_css` jsou definovány jinde.

Dále jsme se podívali do souboru *filesaver.py*, což je nástroj,
který ukládá dokumenty na disk.
Obsahuje třídu `FileSaver` a v ní metodu `url_to_filename`,
která z URL adres udělá názvy souborů.
Třída `DictSaver` v *dictsaver.py* zajišťuje ukládání do slovníku.

V souboru *encoding.py* jsou složitosti ohledně kódování.

V souboru *cli.py* je definováno rozhraní pro příkazovou řádku (CLI).
Tady se volá funkce `main` a díky tomu můžeme freezeyt použít pomocí `python -m freezeyt`.

V souboru *util.py* jsou pomocné funkce a to je veškerý kód. 🎉

### Testy
Většina testů se přidává spolu s novou funkcionalitou,
dle Test Driven Developement [TDD](https://developer.ibm.com/devpractices/software-development/articles/5-steps-of-test-driven-development/)
Testy jako např. `test_check_mimetype` kontrolují jednu funkci.
Důležité jsou testy v `test_expected_output`, tyto testy testují kompletní
zmrazení aplikace.
Tady tyto testy zajišťují, že se freezeyt chová pořád stajně.
V těchto testech je adresář fixtures a v něm jsou aplikace a očekávaný výstup.

### Blog

Krom samotného projektu máme i blog, který slouží částečně i jako dokumentace.
Hledá se v něm snáze než ve videích na YouTube.
Ve článcích jsou shrnutí ze srazů.
Blog sídlí [zde](../) na GH pages.
Nasazení blogu se děje automaticky.
Články se posílají přes PR na GitHub.
Články přijdou do adresáře `freezeyt_blog/articles`.
Při každém PR se blog „zamrazí“ pomocí freezeytu.
Někdo ten PR musí začlenit (ideálně to před tím i schválí).
Poté, co se tento commit pushne do masteru, tak se blog publikuje.

### Continuous Integration (CI)

Když na GitHub pošleme PR, tak na něm GH pustí testy.
Testujema na 4 verzích Pythonu (3.6, 3.7, 3.8 a 3.9),
pak tam jsou ještě testy s Pyflakes,
které kontrolují většinou zapomenuté importy.
Dále se automaticky zamrazí a publikuje blog.  

Nastavení GH actions je v `.github/workflows`

### Další soubory

Dále je v repozitíři nějaká dokumentace s poznámkama.
Pak tam jsou nějaké Gitové soubory, licence, README a informace o závislostech.
Ty se dělí na závislosti pro běh, pro vývoj a pro blog.

Soubor `setup.py` z toho udělá Pythonní balíček a je tam ještě konfigrace Toxu,
který slouží pro to, abychom testy mohly spustit na více verzích Pythonu.

## TODO nadpis
Na chvíli jsme se pozastavili u toho, jak se píší články na blog.
(Články na blog klidně přidávejte, Pull Requesty jsou velice vítány. 😉)
Pokud nějaký článek píšete/chcete napsat,
hlašte se [zde](https://github.com/encukou/freezeyt/issues/1) nebo na Slacku.

Informace o tom, co všechno se dá nastavit v konfiiguraci by měla být napsána
v README (chybí-li tam něco, určitě pošlete PR s opravou, nebo otevřte issue.)
Dá se tam nastavit adresář, do kterého se výstup zamrazí.
Následně prefix aplikace, to je adresa, na které bude stránka „sídlit“.
Pak můžeme specifikovat stránky, na které nevedou žádné odkazy z aplikace.
Takovými stránkami by mohly být například přesměrovávací stránky.
Dále můžeme specifikovat extra soubory typu `.nojekyll` apod.

## Jak dostat Flask app z defaultního Flask serveru?
Chceme-li dostat Flask aplikaci z defaultního Flask serveru,
budeme ji muset nainstalovat.
Poté si vytvoříme [virtuální prostředí](https://naucse.python.cz/course/mi-pyt/fast-track/install/).
V příkazové řádce zadáme (na Windows místo `export` použijte `set`):
```shell
$ export FLASK_APP=app.py
$ export FLASK_ENV=developement
$ flask run
```

Jen tak mimochodem jsme došli k tomu, že na blog by bylo fajn přidat styly!

Pak jsme v README hledali (a našli), jak se freezeyt používá.
Je potřeba přidat freezeyt do proměnné prostředí PYTHONPATH.
Poté nainstalujeme závislosti (dependencies) freezeytu.
Na statických stránkách je problém s přesměrováním. (Proč je tu tato věta?)
Následně spustíme freezeyt.
Potom „zmrežené“ stránky nasadíme na server,
nebo použijeme v Pythonu vestavěný `http.server`.
V konfiguraci můžeme nastavit `freezeyt.freezing` na `True`, a to znamená,
že některé části by se nezafreezovaly.
Následně je potřeba přepnout se do virtuálního prostředí.
Zjistit, jak se daná aplikace importuje.
Potom jsme nastavili PYTHONPATH (až bude balíčk, bude to jednodušší).
Pak by to mělo jít uložit. (Nemám sebemenší tušení, co by mělo jít uložit.)
(Proč mám pocit, že tu je ta část dvakrát?)

## Kontrola PRs
Každý sraz začínáme procházením Pull Requestů (PR) na GitHubu (GH).
Dnes jsme se k tomu dostali trochu později.
Většinou pokecáme o otevřených PRs, řekneme si co nás blokuje
a jak by se s tím dalo pohnout.
Dnes se jich tam sešlo trochu více než obvykle.

### Článek z meetingu 32
První PR přidával článek z minulého meetingu.
Ten jsme začlenili v průběhu ukázky GH actions.

### Rozepsané články na blog
Dále byly na blog přidány historické draft PRs z předchozích srazů.
Rozepsané články jsou lepší než nic.
Po začlenění PR se články za chvíli objeví na [blogu](../).

### Odebrní WSGI demo
Demo aplikace pro rozhraní WSGI už v repozitáři není potřeba, a navíc
celý její kód je v [článku z prvního srazu](/meeting01).

### Možnost přidat extra soubory jako base64 nebo cestu k souboru
Nově bude soubory navíc specifikovat jako cestu, odkud se to má zkopírovat
nebo přidat v base64, to jest soubor binární, méně čitelné, ale také funkční.
PR přidává dokumentaci, samotnou implementaci (probrali jsme jak to funguje),
dále demo aplikaci, očekávaný výstup ve slovníku, očekávaný výstup
v adresáři a změny testů.
Začlenění proběhlo se slovním approve za zneužití administrátorských privilegií. 😀

### Prázdné odkazy
Další PR přidával test s prázdným odkazem, např:
```html
Odkaz <a href="">někam</a>, tedy spíše nikam.
```
Není to ideální, ale není to chyba.
Approve už tam byl, takže PR byl začleněn.
Na chvilku jsme se u toho zastavili.
Prohlížeč chybu nevyhodí, asi to bere jako relativní URL na tu konkrétní stránku.
Ta prázdná adresa není přesně dle standardu, dělat by se to nemělo.
My buď můžeme vyhodit chybu, nebo se chovat jako prohlížeč.
Přidání testu zdůvodňuje rozhodnutí a zároveň to zaručí,
že neměníme chování nástroje.

### Specifikace stránek pomocí generátoru
Poslední PR přidává možnost specifikovat extra stránky pomocí generátoru,
i když na ně nevede žádný odkaz.
Je to funkce která přidá extra pages, když je tam generátor tak jej spustí a přidá dané URL. (snad?)
Přidána byla také aplikace s testy, kde ve slovníku `freeze_config`
je konfigurace pro aplikaci v testech.
Opět proběhlo sofistikované slovní approve.

## Issues
V issues jsou věci, které je ještě potřeba udělat.
Je tam například kompatibilita s Frozen Flask, na tu se pravděpodobně podíváme příště.
Déle reorganizace testů, měnitelná hodnota `test_created_output` - neurgentní.
V jednom z issues, které dostal za úkol nový člen, je úkolem přidat možnost
předat konfiguraci jako naimportovatelnou proměnnou.
Pozastavili jsme se u toho, jak by se to dalo udělat.
V CLI používáme pro configuraci proměnnou `freeze_config`,
bylo by fajn, kdyby to mohl použít uživatel taky, ať nemusí tvořit soubor.
Úkolem je přidat nový přepínač, konfigurace bude v proměnné v Pythonu.
Dále naimportovat modul, z něj naimportovat proměnnou,
tu použít použít to jako konfiguraci.
(Potom přidat testy a dokumentace.)
A samozřejmostí je, že rádi pomůžeme. 😉

## Padající testy na Windows
Na konci jsme se koukli na testy na Windows, které neprocházejí.
První problém byl způsobený verzí Pytestu, to opravuje specifikace v requirements.
Druhý problém je ve WSGI static middleware,
to se vyřeší to až budeme umět kopírovat statické soubory.

Příští týden začíná týmový začátečnický kurz Pythonu, takže se příště sejdeme v úterý.

> Záznam ze srazu [zde](https://youtu.be/RKRogH-NepY).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
