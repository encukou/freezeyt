# Freezeyt sraz třicátý druhý

## Review Pull requestů
Začali jsme review PR, která se v průběhu týdne objevili na GitHubu.
První přidává možnost mít v hostname ne-ASCII znaky.
Ještě v něm chyběla aktualizace poznámek o kódování, jinak to bylo vše,
co bylo ještě potřeba upravit, tak jsme to opravili.
Při psaní PR bylo založeno issue které navrhuje lepší organizaci testů.
Tento PR jsme následně začlenili.

Druhý PR přidával detaily, aby náš freezer odpovídal standardu WSGI.
Podívali jsme se na něj a probrali změny.
Změny jsme prošli po commitech a vysvětlili si, co se v jednotlivých částech děje.
Žádné otázky nevyvstaly, tak jsme PR také začlenili.

Další pull request přidával slovníky `expected_dict` do testů, tak jsme jej začlenili.

Další PR přidával možnost mít pro aplikaci jiné jméno souboru a proměnné
s aplikací než `app`.

## Issues
Po Pull requestech jsme se podívali na issues.

Dále jsme se pozastavili u toho, jak by se měla chovat proměnná
prostředí `TEST_CREATE_EXPECTED_OUTPUT`.

Dále jsme popřemýšleli jak zorganizovat testy, protože některé aplikace testujeme
jak s ukládáním do souboru, tak s do ukládáním do slovníku a některé používají
jen jeden z těchto způsobů.

## Generování `extra_pages`
Potom jsme se rozhodli přidat možnost generovat `extra_pages` pomocí generátoru,
což je speciální funkce.
Chvilku jsme uvažovali, co všechno takový generátor potřebuje.
Napsali jsme testy a začali je opravovat.
Poté, co jsme tyto změny napsali, tak jsme o tom informovali i v README.
A nakonec otevřeli Pull request.

## Testování prázdných odkazů
Pak jsme se podívali na to, co se má stát, když je odkaz prázdný.
Nevytvoří se žádná jiná stránka.
Je to relativní odkaz na tu konkrétní stránku.

Zavřeli jsme issues, které už jsou vyřešené, jen nebyly zavřené.

## Binární soubory v extra files
Potom jsme se rozhodli řešit issue, abychom do konfigurace v YAML mohli uložit
i binární data.
První jsme napsali test.
Potom jsme tuto funkcionalitu přidali.
Problém byl v testech s tím, co je pracovní adresář, tak jsme do toho jednoho testu přidali
[`monkeypatch.chdir()`](https://docs.pytest.org/en/stable/monkeypatch.html),
který změní pracovní adresář.
Ale nakonec jsme to nastavili v té aplikaci a na `monkeypatch` jsme se vykašlali.

## Kompatibilita s Frozen-Flask
Chceme-li tvrdit, že freezeyt je nástupce [Frozen-Flask](https://pythonhosted.org/Frozen-Flask/),
bylo by fajn, kdyby freezeyt uměl to stejné jako Frozen-Flask,
tak jsme na to založili issue.

> Záznam ze srazu [zde](https://youtu.be/rUiKVwKLmbc).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
