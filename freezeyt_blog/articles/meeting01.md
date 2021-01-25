# Freezeyt sraz první

## Co je úkolem projektu?
Vytvořit generátor statických webových stránek, tedy vzít kód webové stránky
a stáhnout ho na disk, aby se daly jednotlivé stránky zveřejnit a nemusel
běžet nějaký složitý webový server.
Budeme to dělat pro stránky, které nejsou webové aplikace.

## Jak vypadal první sraz?
Seznámili jsme se službami, které budeme používat pro komunikaci v průběhu srazů
(jit.si, Etherpad, GSheet). Také jsme se dozvěděli, jak budou "srazy probíhat" -
bude se tvořit a naším úkolem je pro začátek chápat o čem je řeč.
Kvůli/díky koronaviru budou srazy probíhat online, momentálně se naše skupinka
skládá z lidí z Brna a Ostravy. Úkoly budou zadávány formou issues na GitHubu.
Kód bude na GitHubu. Ujasnili jsme si, co bude cílem projektu (viz výše).
Ujasnili jsme si rozdíl mezi stránkou a aplikací.
Na aplikaci uživatel něco mění a aplikace na něj reaguje.
Na stránkách mění obsah pouze administrátoři.

Domluvili jsme se, že kód a commity budu anglicky a komunikace klidně česky.
Freezeyt je pracovní název a nikdo neví, zda bude finální.

A poté jsme se pustili do práce.

## Jak začít?
Potřebujeme vytvořit aplikaci, která vezme kód nějaké stránky a uloží všechen
obsah na disk. To je ovšem celkem složitý proces, jak tedy začít? Pro začátek
jsme vytvořili jednoduchý program, který vezme jednu stránku a uloží ji na disk.
Proto, abychom nějakou aplikaci mohli uložit na disk, budeme (logicky)
potřebovat aplikaci. Pro její vytvoření použijeme webový framework Flask.
Základní konstrukce takové aplikace vypadá následovně:

```python
from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return """
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!
        </body>
    </html>
    """
```
Dále jsme si vytvořili virtuální prostředí a do něj nainstalovali Flask.
Dalším krokem je pustit Flask pomocí následujících příkazů
(na Windows místo `export` použijte `set`):
```console
$ export FLASK_APP=demo_app.py
$ export FLASK_DEBUG=1
$ flask run
```
Abychom si ujasnili, co všechno má generátor udělat, je vhodnou metodou test
driven development (TDD). Nejdříve se napíše test který by měl projekt splňovat
a poté zařídíme, aby test procházel.

Pro testování použijeme, stejně jako na
[začátečnickém kurzu](https://naucse.python.cz/course/pyladies/beginners/testing/),
[Pytest](https://docs.pytest.org/).
Nainstalovali jsme si ho do aktivovaného virtuálního prostředí.

První test ověřuje, že nová funkce `freeze` zmrazí obsah aplikace, tam kam má.
Funkce `freeze(app, tmp_path)` ještě není napsaná, ale test zajistí,
že jakmile ji vytvoříme, bude se chovat tak, jak chceme

Test momentálně neprochází kvůli *ModuleNotFoundError*, protože modul
`freezeyt` ještě neexistuje. První test tedy vypadá nějak takto:

```python
import pytest
from demo_app import app
from freezeyt import freeze


def test_one_page(tmp_path):
    freeze(app, tmp_path)
    with open(tmp_path / "index.html", encoding='utf-8') as f:
        read_text = f.read()
    assert read_text == """
    <html>
        <head>
            <title>Hello world</title>
        </head>
        <body>
            Hello world!
        </body>
    </html>
    """
```
> `tmp/frozen` je dočasný adresář a na Windows to nebude fungovat.
> Na konci srazu to bylo změněno tak, aby to fungovalo i na Windows.
> Testy si tedy vytvoří vlastní adresář a po skončení testu ho smažou.
> K tomu se použijeme
> [`tmp_path`](https://docs.pytest.org/en/stable/tmpdir.html#the-tmp-path-fixture)
> z pytestu.

> Zeptá-li se prohlížeč na nějaký adresář, server statických stránek sáhne po
> souboru `index.html` jako hlavní stránce daného adresáře.

Při TDD již při návrhu testu přijdeme na to, jak se daná funkce volá a můžeme
na to přijít mnohem dříve, než kdybychom testy napsané neměli.


## Jak dostat obsah stránky z aplikace?
Pro to je potřeba porozumět (alespoň základům) technologii WSGI.

WSGI (Web Server Gateway Interface) definuje jednoduché a univerzální rozhraní
(interface) mezi webovým serverem a webovou aplikací nebo frameworkem.
Vše o tomto rozhraní je popsáno v [PEP 3333](https://www.python.org/dev/peps/pep-3333/).

Webové aplikace napsané v Pythonních frameworcích (např. Flask, Django)
mají společné rozhraní WSGI.
WSGI nám také umožňuje používat různé kombinace frameworků s různými HTTP servery.
Znamená to tedy, že pokud bude náš freezer kompatibilní s tímto rozhraním bude
kompatibilní s jakoukoliv webovou aplikací napsanou v Pythonu.
Aplikaci můžeme vytvořit v mnoha frameworcích. Také ji můžeme nasadit na mnoho
HTTP serverů, které se o vše postarají.

Standardní knihovna Pythonu obsahuje knihovnu *wsgiref*, kde `wsgiref.simple_server`
je schopno servírovat Pythonní web aplikaci, napsanou například ve Flasku.
Tím jsme si ukázali, že aplikace demo_app.py je kompatibilní s tímto webovým
rozhraním. Soubor wsgi_demo.py ukazuje způsob, jak je možno takovou aplikaci
spustit pomocí `wsgiref.simple_server` a ne pomocí Flask. A téměř celá aplikace
je zkopírována z [dokumentace](https://docs.python.org/3.8/library/wsgiref.html#module-wsgiref.simple_server):

```python
from wsgiref.simple_server import make_server
from demo_app import app

# Create a demo WSGI server from a Flask app.
with make_server('', 8000, app) as server:
    print("Serving HTTP on port 8000...")

    # Respond to requests until process is killed
    server.serve_forever()
```
Naši spuštěnou aplikaci najdeme na portu 8000, proto do prohlížeče zadáme `localhost:8000`.


## Jak toto rozhraní funguje?
Proto, abychom z aplikace dostali nějaký obsah, tak ji potřebujeme zavolat.
Každá webová aplikace v Pythonu je volatelná, může to být třeba funkce nebo třída.

Tato aplikace potřebuje `environ`, což je slovník, a `start_response`,
což je funkce, jako argumenty. Následně jsme postupně do slovníku `environ`
přidali vše potřebné, dokud nám volání nevrátilo odpověď *200 OK*. Zatím tam máme vše,
pro to, aby bylo možné spustit jednoduchou WSGI aplikaci, ale není to vše,
co by tento slovník měl obsahovat. Co všechno tam musí být specifikuje
[dokumentace](https://www.python.org/dev/peps/pep-3333/#environ-variables).
To, co daná aplikace vrací je iterátor, takže se to dá projít for-cyklem.

Server zavolá funkci a zpátky dostane sekvenci bytových řetězců, stav a hlavičky.
Aplikace zavolá funkci `start_response` a následně vrátí obsah.

## Jak začít s generátorem statických stránek?
Funkce, která zmrazí stránku musí vytvořit slovník `environ`. Následně funkce
vytvoří lokální funkci `start_response`.

Povedlo se nám zajistit, že test prochází. Jakmile něco alespoň trochu funguje,
je dobré to uložit do Gitu. Začali jsme vytvořením repozitáře a přidáním první
revize. Na GitHubu byl vytvořen [repozitář pro projekt](https://github.com/encukou/freezeyt).
My už nový repozitář tvořit nemusíme, my si repozitář jen naklonujeme z GitHubu.

## Co by bylo dobré přidat?
Přidali jsme projektu licenci. Na webu [choosealicense.com](https://choosealicense.com/)
je seznam nejčastěji používaných open source licencí a pomůže nám i s výběrem.
My jsme vybrali MIT licenci.

Dále by bylo dobré přidat README - popis projektu. Tak jsme si ukázali, jak se
README píše a co by v něm mělo být. README máme
v [markdownu](https://guides.github.com/features/mastering-markdown/) a při psaní
nám může pomoct služba [HackMD](https://hackmd.io/#), kde na jedné
straně vidíme zdrojový kód a na druhé straně, jak to vypadá.

## S čím můžeme pomoci?
Úkoly budou v [Issues](https://github.com/encukou/freezeyt/issues). Bylo by dobré,
abychom úkoly, které si zamluvíme, dokončili. Momentálně jsou úkoly napsat článek
na blog, následně napsat test, kdy na jedné stránce je odkaz a na ní je odkaz
na stránku druhou. A dále by bylo dobré napsat README.

Aby se nám lépe pracovalo na projektu, je dobré si u projektu nastavit „Watching“
u [repozitáře](https://github.com/encukou/freezeyt) projektu. Tím nám budou chodit
upozornění o Issues a Pull requestech.

> Záznam ze srazu [zde](https://youtu.be/6xDkqmQPefw).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
