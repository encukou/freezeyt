# Freezeyt sraz sedmnáctý

> Tento článek není hotový. Záznam ze srazu je [zde](https://youtu.be/_9rH05_bAUk).

Začali jsme review Pull requestů.
První přidával konfiguraci pro freezeyt. Tak jsme zjistili, jak by to mohlo být lepší.

Je možné rozdělit změny na více commitů. Pomocí
```
git reset -p origin/master
```
jsme schopni rozdělit změny na přidané a nepřidané. Pomocí
```
git restore
```
jsme schopni se vrátit do stejné verze.

Druhý Pull request přidával rozpracované články na blog.

Třetí přidával demo aplikaci s odkazem v CSS na font. Abychom font používali správně, je ještě potřeba přidat licenci.

Následně jsme pokračovali ve čtení standardu WSGI. A povedlo se nám ho dočíst.

Pustili jsme se do issue, které řeší že v cestě mohou být i znaky, které nejsou ASCII.

> Záznam ze srazu [zde](https://youtu.be/_9rH05_bAUk).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
