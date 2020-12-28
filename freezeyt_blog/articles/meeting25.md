# Freezeyt sraz dvacátý pátý - první třída

Na začátku jsme se koukli na pull request, který přidával testovací aplikaci
v Djangu.
Při psaní [minulého článku](../meeting24/) jsme přišli na to, že jednodušší než
dávat nevyužité importy do `__all__` je dané importy zakomentovat.
Dále jsme se zabývali tím, proč nejde zamrazit testovací Django aplikace.
Problém byl s použitím produkčního místo vývojářského serveru.
Následně jsme se řešili statické soubory v Djangu.

Potom jsme začali Freezeyt převádět na třídu. Většina věcí se překopírovala,
z logických celků se udělaly metody a následně se přidalo `self` k proměnným,
ze kterých jsme chtěli udělat atributy třídy.
Poté jsme změnili import, spustili testy a začali je opravovat.
Rozpracovaná třída [zde](https://github.com/encukou/freezeyt/pull/114/commits/829b67e8de33a840fdd05cf402a6e801777ccbb2).

> Záznam ze srazu [zde](https://youtu.be/hOjla7qw2Sk).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
