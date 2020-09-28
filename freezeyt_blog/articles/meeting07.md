# Freezeyt lekce sedmá


## Review pull requestů
Začali jsme tím, že jsme se koukli na pull requesty (PR),
které přistály na GitHubu.

První z nich aktualizoval dokumentační řetězce (docstringy).
Druhý řešil [Issue #31](https://github.com/encukou/freezeyt/issues/31).
Jelikož používáme metodu Test Driven Developementu (TDD),
znamenalo to zajistit, aby prošel příslušný test.
Díky tady tomuto PR freezeyt spadne v případě, že v dané webové aplikaci
bude „pokažený“ odkaz, např. e-mail link bez `mailto:`

Komentář k tomuto PR říkal, že by bylo dobré, kdyby chybová hláška
byla více informativní. K tomu se dostaneme později v projektu.

> Poznámka ke GitHubu: chceme-li zajistit, aby se dané Issue zavřelo
automaticky, je potřeba použít jedno
z [těchto](https://docs.github.com/en/github/managing-your-work-on-github/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword)
klíčových slov.

Třetí PR přidává adresář na blog, ale jelikož je blog stále „a Work in progress“,
tak jsme PR (zatím) do projektu nezačlenili.

> Poznámka ke GitHubu: chceme-li se podívat na obrázky, které byly přidány přímo
na GitHubu bez toho, aniž bychom si k sobě stahovali danou větev, můžeme použít
tlačítko *Display the rich diff* vpravo v rohu u daného souboru v sekci *Files changed* na GitHubu.

> ![Tlačítko pro zobrazení obrázků na GitHubu](../static/images/rich_diff.png)


## Úprava odchytávání chybných odkazů
Následně jsme zkontrolovali Issues a poté jsme se pustili do práce na samotném kódu.
Začleněný PR na odchytávání špatných odkazů obsahoval i tuto podmínku:

```python
if "200" in status:
    ...
```
V řetězci, který obsahuje status code, se `"200"` teoreticky může vyskytovat kdekoliv,
takže pro jistotu jsme tuto podmínku upravili, protože dle [standardu](https://tools.ietf.org/html/rfc7231)
je status code vždy na začátku. Podmínku jsme upravili tak, že zjišťuje, zda status začíná kódem 200.

```python
if not status.startswith("200"):
    ...
```


## Úprava slovníku `environ`
Když už jsme se věnovali těm standardům, tak jsme se pustili na úpravu `environ`
aby bylo podle WSGI standardu, tedy dle [PEP 3333](https://www.python.org/dev/peps/pep-3333/#environ-variables).
Prošli jsme všechny proměnné, které environ může obsahovat a vybrali vše, co potřebujeme.

Momentálně to není celá implementace protokolu WSGI a proto se k ní někdy v budoucnu vrátíme.
Bylo na to založeno Issue.


### Odbočka ke standardním výstupům
V průběhu toho jsme si udělali odbočku ke standardním vstupům, výstupům a souborům,
kam se ukládají chybové hlášky. Ve zkratce:

* `sys.stdout`, tedy standardní výstup, v základu je to příkazový řádek.
* `sys.stderr` - standardní chybový výstup. Tento soubor není ovlivněn změnou výstupu
(např. pomocí `>` v příkazovém řádku) vypíše se jinam než na stdout.
* `sys.stdin`, neboli standardní vstup.


## Jiná host adresa
Momentálně freezeyt nefunguje (tak, jak bychom chtěli), když je jiná host adresa než *localhost:8000*.

Jelikož používáme TDD, začali jsme napsáním testů. Upravili jsme funkce
`freezeyt.freezing.freeze` a `freezeyt.freezing.url_to_filename`.
Rozšířili jsme nápovědu. A zajistit, aby to fungovalo je úkol do příště.

### Odbočka k doménám
Pro pokusné a testovací účely jsou rezervovány [jisté](https://tools.ietf.org/html/rfc2606)
domény, například doména `test` a `localhost`.


## Reorganizace testů
Ke konci jsme se dostali k tomu, že většina první stránky repozitáře jsou
testy a testovací aplikace.

Testy (momentálně) fungují tak, že zkopírujeme předchozí test a něco tam upravíme
(něco upravit zapomeneme).
Testovací metoda [Gold Master Testing](https://codeclimate.com/blog/gold-master-testing/)
by mohla náš problém elegantně vyřešit. Ve zkratce: máme uložený vstup
a správný/chtěný výstup - testovací aplikace projde vstupy, spustí je a ověří,
že výsledky jsou stejné.
Víme, že jakmile aplikaci zmrazíme, tak zmražení bude vždy stejné, takže testy
nebudeme muset upravovat.

V adresáři *fixtures* jsou data, která budou testy potřebovat,
tzn. testovací aplikace V adresáři *test_expected_output* budou adresáře
s očekávanými výstupy programu.

Pro testy potřebujeme funkci, která vezme obsah dvou adresářů a porovná jejich obsah.
Tu si buď můžeme napsat vlastní, nebo pro to můžeme použít třídu
[`filecmp.dircmp`](https://docs.python.org/3/library/filecmp.html#the-dircmp-class)
standardní knihovny.

V reorganizaci testů budeme pokračovat příště.

### Odbočka k `__name__` a `__file__`
* `__name__` vrátí název modulu.
* `__file__` vrátí název souboru s celou cestou a příponou.

> Záznam z lekce [zde](https://youtu.be/DzpNvEarVAE).
Více informací o projektu [zde](https://tinyurl.com/freezeyt).
