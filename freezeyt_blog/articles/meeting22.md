# Freezeyt sraz dvacátý druhý - testování CLI


Sraz začal kontrolou PR na GitHubu. První (a poslední) testoval CLI.
První bylo potřeba vyřešit merge konflikty a poté kód trochu optimalizovat.

Pokud uděláme vetší změny a chtěli bychom je rozdělit do více commitů, můžeme
to udělat například pomocí nástroje Git GUI - grafický nástroj pro práci s Gitem.
V Git GUI můžeme přidat jednotlivé řádky místo celých souborů.
V příkazové řádce je možno toho stejného docílit pomocí
`git add -p` tak nám Git nabídne jednotlivé části a my se můžeme rozhodnout,
zda se mají přidat, čí nikoli. Pomocí `s` pak můžeme části rozdělit.

Následně jsme se věnovali tomu, abychom zamezili opakování kódu. Všechny funkce
byly stejné na začátku a na konci a jediné, co se měnilo byl střed funkce.
Zamezit opakování jde udělat vícero způsoby - jeden z nich je, že vytvoříme
jednu funkci, která zajistí, co se má udělat předem a co se má stát po tom.
Druhou možností je napsat vlastní context manager, který by se dal použít
pomocí `with`, třeba takto:

```python
with my_context_manager:
    ...
```
Context manager lze napsat pomocí dekorátoru `@contextmanager` z knihovny `contextlib`.
Místo, kam má uživatel vložit daný kus kódu označíme slovem `yield`, na němž se
funkce zastaví.

Do příště by bylo fajn si rozmyslet, jak by se dal freezeyt používat a jaká by
mohl mít rozšíření.

> Záznam ze srazu [zde](https://youtu.be/4OFdP8usCTw).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
