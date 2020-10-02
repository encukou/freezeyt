# Freezeyt sraz třináctý

## Review PR
Jako už klasicky, sraz začal, kontrolou pull requestů z GitHubu.
Některé byly začleněny už v průběhu týdne, abychom se tím na srazu nezdržovali.

První přesouval testy z hlavní úrovně repozitáře do test_expected_output.

Druhý upravoval obrázky na blogu. Momentálně obrázky na blogu fungují tak,
že je možné je mít jen v adresáři static/images.
Řešit se to bude, jakmile to bude potřeba.

Třetí PR přejmenovával články na blog, tak, aby byly seřazené a nejmenovaly
se lekce.

Čtvrtý PR opravoval odkazy na obrázky ve článcích. Obrázky na blog budou vždy ve
static/images, pro webové aplikace to není ideální, ale pro naše účely by to
nemuselo ničemu vadit.

Pátý a poslední pull request přidával článek z dvanáctého srazu.

## Kontrola otevřených issues

Následně jsme se podívali na otevřené issues. U některých jsme se zastavili
a řekli jsme si, jak by se daly vyřešit.

To, aby se nepřepisovaly funkce se dá vyřešit například pomocí linteru, stačit
nám bude prozatím [PyFlakes](https://pypi.org/project/pyflakes/).
Kontrolu linterem můžeme zařadit do GitHub actions.

### Odbočka k mazání souborů z Gitu

Smažeme-li soubor normálně (buď z prohlížeče souborů, nebo pomocí `rm`
v příkazovém řádku), musíme říct gitu, že je smazán, tedy pomocí `git add <file>`.
Pomocí `git add` dáváme Gitu vědět, že má přidat aktuální stav daného souboru,
tedy i jeho smazání. Další možnost je použít `git rm <file>`

## Stránky, na které nevede odkaz

Je spousta možností, které bychom chtěli konfigurovat. Většina z nich je v issues.
Bylo by složité konfigurovat vše z příkazové řádky, protože by toho mohlo být více,
například extra stránky, vypisovat jejich seznam by bylo složité a zdlouhavé.

Začali jsme tím, že jsme na to napsali testy. Následně jsme aplikaci upravili
tak, aby testy procházely a následoval 3. krok TDD a to refactoring dané podmínky.

Máme-li nějaké nepovinné argumenty, tak je dobré je předávat pomocí slovníku
`kwargs`. To znamená, že funkci `freeze` teď voláme takto, abychom zamezili
exponenciálnímu nárůstu délky `else` bloku v testech: `freeze (app, tmp_path,
**freeze_args)`. Následně byl se změnami poslán PR, který čeká na review.

## Kontrola, že mimetype sedí k příponě souboru
Opět jsme začali napsáním testu. Aplikace vrací správný `mimetype`, ale jakmile
ji spustíme jako statickou stránku, tak `mimetype` není správný. Demonstrovali
jsme si možné řešení. Takže byl otevřen Draft pull request, kde je možní řešení
tohoto issue. Více informací a rad, jak postupovat. Je možno najít v popisku
pull requestu.

> Záznam ze srazu [zde](https://youtu.be/CG5dPqZzC8M).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
