# Freezeyt sraz dvanáctý - blogový

Dnešní sraz začal jako obvykle kontrolou pull requestů, které přistály na GitHubu.
První PR byl ten z minula, který přidával GitHub action. V komentáři se objevil
dotaz, zda by nestačilo nastavit `shallow` na False. Tento parametr má jen `.cmp`
a `.cmpfiles`, ale `.dircmp`, který používáme tento parametr nemá, takže
v základnám nastavení neprovede důkladné porovnání souborů.

Někdo už tu chybu reportoval a byla na to i napsána změna, ale chybí k ní testy,
a proto v Pythonu ještě není. Tady je dobrá příležitost zapojit se do vývoje
Pythonu samotného.

Druhý PR aktualizoval aplikaci na blog. Následovalo upravování blogové aplikace.

Aby se ukazovaly mezery v popisu obrázku, musel se `alt_text` dát do uvozovek
v [app.py](https://github.com/encukou/freezeyt/blob/74b0e00a49ac1f07a1906fac4f1601cbbb5f5b13/freezeyt_blog/app.py#L35).
Problém nastane, jakmile v textu budou uvozovky, to se dá vyřešit pomocí
[html.escape](https://docs.python.org/3/library/html.html#html.escape).

Obrázky na blogu bude potřeba ještě vylepšit, a proto bylo založeno nové issue.

### Odbočka ohledně `imghdr`/`mimetype`
Jak počítač pozná co je v danem souboru (jak počítač pozná že text je text nebo
že obrázek je obrázek)? To záleží na systému, na Windows se to určuje pomocí
přípony, na Unix se systém podívá přímo do souboru, například, pokud nejsou importy
v souboru nepozná, že jde o `.py` soubor, protože se nedívá na přípony souboru.

Když něco posíláme přes internet, kromě obsahu souboru posíláme i typ souboru
(více informaci [zde](https://www.iana.org/assignments/media-types/media-types.xhtml))
aby prohlížeč nemusel detekovat pomoci přípony nebo analyzovat obsah souboru což řeší
nějaká knihovna která je na každém počítači jiná a není to tedy konzistentní způsob.

`imghdr`, které používáme, nám neříká nic o [mimetypes](https://docs.python.org/3/library/mimetypes.html)
`mimetypes.guess_type(url, strict=True)` - vytáhne argument z URL adresy.

Python http server používá `mimetypes`. V hlavičkách vždy mimetype dostaneme,
ale tato informace se nám ztratí (soubor uložíme na disk ale bez tohoto mimetype)
takže jediná informace, kterou máme je přípona souboru. Takže zatím doufáme že
server statických stránek na servírování použije stejný mimetype jako ten, který
jsme dostali v hlavičkách od aplikace kterou se snažíme zamrazit. Takže je potřeba
zkontrolovat že typ který dostaneme z aplikace, kterou freezujeme je stejný, tzn.
odpovídá příponě souboru, kterou by server statických stránek vybral když chce
servírovat soubor dané přípony. A tak jsme na to založili issue.

Budeme potřebovat [db.json](https://github.com/jshttp/mime-db/blob/master/db.json)
z `mime-db`- pokud chceme freezovat stránky, které se budou pouštět na GitHub
pages, tak by se měla použít tato databáze.

Nastavení hlaviček je specifikováno ve
[Flask Response Objects](https://flask.palletsprojects.com/en/1.1.x/api/#response-objects).
Celé mimetypes je zabaleno do [content_type](https://flask.palletsprojects.com/en/1.1.x/api/#flask.Request.content_type)
a content_type se používá v hlavičkách.

Mimetype se použije pokud není nastaven content_type a content_type se používá když
není nastavena hlavička. Takže to jsou tři způsoby jak nastavit
[flask.Response](https://flask.palletsprojects.com/en/1.1.x/api/#flask.Response)
a jsou tam tak aby se to lépe používalo když známe jenom jeden z nich. Je potřeba
také zkontrolovat zda je tam kódování UTF-8, protože servery statických
stránek vždy používají UTF-8 kódování.

## Pokračování kontroly pull requestů
Další PR přesouvá testy s prefix do `test_expected_output`
Cílem je, aby aplikace, které by měly být testovány tím, že se porovnávají
s očekávaným výsledkem nebyly v hlavním adresáři projektu a zároveň, aby každá
testovací aplikace měla svůj vlastní adresář ve fixtures kde bude aplikace včetně
očekávaného výstupu.

Modul daného jména se importuje standardně jen jednou.
V `sys.modules` je databáze naimportovaných modulů.

Všechny testovací aplikace se přejmenovávají na app, takže `module_name` bude
vždy `app`, takže se bude muset smazat ze `sys.modules` aby bylo možné
naimportovat jinou aplikaci se stejným jménem.
Ideálně v bloku `try`/`finally` použít `del sys.modules['app']`.

Další PR přidával článek z lekcí 9 a 10, problémem bylo, že se články z blogu
mezitím přesuly, tudíž vzniklo mnoho merge konfliktů a ty bylo potřeba vyřešit.
Také tam byl problém s obrázky, které jsou v gitu, ale v článku nejsou.
`git grep <something>` hledá daný řetězec v repozitáři, pomocí toho jsme našli,
které obrázky jsou potřebné a které nikoli. Obrázky, které v PR měly být jsme
přidali pomocí `git add <image>` a ty, které tam neměly být jsme odebrali pomocí
`git rm <image>` Změny a opravy pull requestu byly pushnuty rovnou do větve,
ze které byl PR otevřen.

## Jak vylepšit blog?

* Bylo by dobré, kdyby se články na blog automaticky přidaly na blog.
To by se dalo vyřešit přidáním dalšího workflow na GitHubu.

* Přejmenovat články tak, aby byly seřazené a aby se jmenovaly "meeting" místo "lekce"

* Bootstrap potřebuje strukturu i v html, nestačí jen přidat CSS soubor.

* Přidáni div s class="container" kolem obsahu, aby byly okraje odsazené.

* Podtržítka mají v Markdownu speciální význam a proto je problém s názvy některých
pythonních metod a souborů. Dá se to vyřešit tím, že se tento kousek kódu
dá do zpětných uvozovek.

* Jméno funkce, kterou používáme je také dobré dát do zpětných apostrofů,
aby se místo dvou podtržítek nezobrazovaly tučně.

Sraz jsme zakončili kontrolou otevřených issues a toho, co je potřeba udělat.

> Záznam ze srazu [zde](https://youtu.be/MonD2jaagK8).
Více informací o projektu [zde](https://tinyurl.com/freezeyt).
