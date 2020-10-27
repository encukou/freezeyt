# Freezeyt sraz pátý

> Tento článek není hotový - poznámky jsou napsány do přibližně [této](https://youtu.be/2Ei8t5xgnQ0?t=2767) části záznamu.

## Review Pull requestů

Přidání testů s url_for()
* ideálně bychom v testech neměli používat jiné funkce z naší aplikace, ty by měly být testovány jinde
* Petr přidal cesty do testů takže také testujeme, že soubory se opravdu vytvoří

Parametry místo argumentů v dokumentačních řetězcích
* opraveny z minula

2 Pull requesty opravující issue #21

## Vylepšování freezeytu
Přeskakujeme odkazy na externí stránky

## Úprava testů
Přidali jsme test s fragmentem například [https://github.com/encukou/freezeyt/#usage](https://github.com/encukou/freezeyt/#usage) obsahuje fragment `#usage` - je to odkaz na konkrétní místo na dané stránce, ale náš freezer to může ignorovat, protože to zajímá prohlížeč.
Přidat test s ftp -> nyní freezer bere jen http a https schéma
Rozebrali jsme strukturu url adresy a to, co nás v ní zajímá
  * schéma - bereme jen http a https
  * netloc - zajímá nás - náš server to musí být
  * path - zajímá nás
  * parametry - nepoužívají se
  * query (dotazy) - nás nezajímají, to funguje jen v aplikacích
  * fragmenty - zajímají prohlížeč a ne freezer

Z proměnné url jsme udělali url_path - aby to bylo výstižnější



> Záznam ze srazu [zde](https://youtu.be/2Ei8t5xgnQ0).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
