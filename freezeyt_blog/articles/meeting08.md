# Freezeyt sraz osmý - jedna velká odbočka

> Tento článek není hotový. Záznam ze srazu je [zde](https://youtu.be/uV-RvpklS1Y).

## Review PR

První PR, již z minula přidával článek na blog z šestého srazu. Problém s obrázky (chybí), cestami k obrázkům (nezačínají tam, kde by měly) a kousky kódu nejsou zvýrazněny.

Druhý PR přidával 7. sraz na blog.
> Poznámka k MD
Do těchto uvozovek ```za tyto troje uvozovky napíšete python a obarví se to```

> Poznámka k blogu
napíšeme si to sami, jinak se doporučuje psát s něčím už připraveném např. [pelican](https://blog.getpelican.com/)

Od toho jsme se dostali k tomu, že blog by byl skvělou testovací aplikací. Blog bude [MVP](https://en.wikipedia.org/wiki/Minimum_viable_product), takže zatím škaredá funkční aplikace. Vše potřebné je napsáno v issue, takže úkol do příště.

Třetí PR přidával výchozí prefix do rozhraní, bez toho to vracelo None.

Čtvrtý a poslední PR přidával prefix do url to filename a řešil issue. Poslední commit přidával test, na to, když bude prefix bez portu. Když nepíšeme port, použije se výchozí port pro daný protokol, pro HTTP je to 80. Pro HTTPS 443. Port je potřeba, ale když ho nemáme, tak se použije výchozí.


## Nastavování defaultních portů
Začali jsme opravováním nového testu, který přidával možnost použít url bez uvedení portu. Přidali jsme do funkcí `freeze` a `url_to_filename` přidání defaultního portu. A následně přišel na řadu „třetí“ krok TDD, a to refactoring. Momentálně se nám při nezadání portu daný port vyhodnocoval dvakrát. Rozhodli jsme se, že nejlepším řešením bude přidat funkci, která URL adresu zpracuje. Parse result dědí z ntice, takže je nemění, nemůžeme tedy přidat/změnit port. Dědí z třídy named tuple, metoda [*_replace*](https://docs.python.org/3.8/library/collections.html#collections.somenamedtuple._replace) z modulu collections (ze standardní knihovny) by nám mohla pomoci s měněním výchozích portů. `_replace` pracuje na pojmenované ntici, jenže port je atribut třídy, takže není v ntici. Bylo by dobré napsat [unit testy](https://en.wikipedia.org/wiki/Unit_testing) na tuto funkci, takže úkol do příště.

### Odbočka ke closures - vnořené funkce
Rekurze & lokální funkce

> Záznam ze srazu [zde](https://youtu.be/uV-RvpklS1Y).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
