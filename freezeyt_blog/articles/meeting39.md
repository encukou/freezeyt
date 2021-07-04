# Freezeyt sraz třicátý devátý -

> Tento článek není hotový. Záznam ze srazu [zde](https://youtu.be/96aohYXMFxc).

PR s články na blogu

Redirect policy - momentálně se ukončí.
Redirect policy safe - zamrazí se stránky, a na kterou se přesměrovává
- vypadá to dobře, neprochází testy
- freezeyt najde broken link.

Pro hledání chyby použijeme pdb.
pytest má přepínač --pdb
nastane-li chyba, spustí debugger

Redirect policy je nastaveno na error, místo na safe.
Redirect policy z configu se nepředává do funkce/ do konfigurace

My jednotlivé kousky konfigurace překopírováváme z CLI params.

Konfigurace je složitá, dala by se přepsat.
Každé přidání nového parametru bude znamenat přidání nového řádku,
bylo by dobré provést refactoring.

Předělávání konfigurace, padající testy
config - try except
set default

Dále bottle framework, úprava konfigurace v CLI

Rozpracované redirects

Get all links vrací URL, vrací řetězec, my z toho děláme strukturu
Máme na to funkci, přidává port, když chybí.
Důležité, když používáme is external.
Is external je používá, když se nerovnají.
A chybí-li port, tak se nerovnají.

To by bylo potřeba dodat do is_external.
Poznámka do docstringu.
Přidána podmínka.
Zjistili jsme, že na `is_extranal` nemáme testy.
Tak jsme je dospali.

Na chvíli jsme se zasekli u True/Flase při psaní testů.

Dále jsme pokračovali s redirecty (přesměrováním).
Byl otevřen PR, ale změny závisí na jiném PR tak to bylo otevřeno jen jako work-in-progress.

> Záznam ze srazu [zde](https://youtu.be/96aohYXMFxc).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
