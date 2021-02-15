# Freezeyt sraz osmnáctý

> Tento článek není hotový. Záznam ze srazu je [zde](https://youtu.be/zV0tPtqz1BM).

Sraz, jako už klasicky, začal kontrolou pull requestů (PR), které přistály na GitHubu.

První z nich odebíral `else`, ke kterému by se program nikdy neměl dostat, ale PR byl zavřen, protože, kdyby někdo upravil podmínku nad tím, tak by se to mohlo pokazit.

Druhý PR přidával `extra_pages` do CLI, mělo to dva problémy, první byl, že to bylo, že je to v množném místo jednotném čísle. A druhý problém byl, že nemáme testy na CLI (a to není problém jen tohoto PR). Takže jsme založili Issue.

Následně proběhla konzultace k tomu, kde jsme se u rozpracovaných pull requestů zasekli a dostali jsme rady, jak pokračovat.

Vrátili jsme se k tomu, co jsme rozpracovali minule.

Flask výjímky - dodat (jak nevyhazovat 404 a místo toho nějaké jiné).

Potom jsme zkoumali, jak jsou cesty v URL adresách zakódovány. A zjistili jsme, že WSGI adresy kóduje pomocí UTF-8 a dekóduje pomocí Latin-1, takže v Pythonu by toto kódování mohlo vypadat nějak takto:
```
>>> "čau".encode("utf-8").decode("latin-1")
```

kódovací odbočka

> Záznam ze srazu [zde](https://youtu.be/zV0tPtqz1BM).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
