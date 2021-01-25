# Freezeyt sraz dvacátý sedmý - DictSaver & testy konfigurace

Na začátku srazu jsme vzpomínali, kde jsme minule skončili.
Jako první jsme smazali původní `freezeyt/freezing.py`.
Začali jsme tvorbou rozšíření, které by „zmražené“ stránky
místo do souboru ukládalo do slovníku.

Po chvilce psaní jsme si uvědomili, že nám chybí testy, a tak jsme je dopsali,
aby to byl správný Test Driven Development.
Poté, co jsme napsali test, jsme se vrátili k psaní plug-inu. Metoda
`get_result` zatím vezme jen známý výsledek, ale je možné,
že v budoucnu budeme chtít, aby dělala něco složitějšího.

Následně jsme pokračovali ve tvorbě třídy `DictSaver`.
Potom jsme napsali testy na konfiguraci. To byly testy na freeze z CLI
a funkce `freeze`. Ověřovali jsme ukládání výsledku do souboru a do slovníku.

V průběhu úprav konfigurace jsme zjistili, že mnoho testů je špatně nakonfigurováno.

Napsali jsme testy, které ověřují, že je možno uložit výstup do slovníku bez toho,
abychom mu dali cestu, kam má soubor uložit.
Tady tato změna rozbila spoustu testů, tak jsme pokračovali v úpravách freezeytu.

Následně jsme freezeyt upravili tak, aby byl adresář, kam se má výstup uložit povinný.
A aby nebylo možné ho zadat, když výstup budeme chtít uložit do slovníku.

Na konci srazu se nám z nějakého důvodu pokazily testy, takže se k tomu vrátíme později.

> Záznam ze srazu [zde](https://youtu.be/XOf46FLt78k).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
