# Freezeyt sraz třicátý čtvrtý - adaptér na Frozen-Flask

Začali jsme review PR. První PR specifikoval verzi Pytestu
v requirements, protože MonkeyPatch, který používáme,
je součástí Pytestu od verze 6.2.0., takže těm,
kdo mají nainstalovanou starší verzi Pytestu padají testy s chybou.

Druhý PR se zabývá reorganizací testů.
Řešili jsme, co se mění.
Cílem PR bylo přidat logiku pro rozdělení testů na základě výstupních dat ke kontrole (soubory, dictionary).

Logika byla nastavena následovně:
* pokud nemáme definovanou proměnnou `expected_dict` je test pro kontrolu testovacích dat ve formě slovníku přeskočen a neřeší se ani povinnost mít tento slovník definován
* V případě kontroly vygenerovaných testovacíh souborů, je situace odlišná. Pokud není explicitně definována proměnná `no_expected_directory` s hodnotou `False`, tak je nutnost testovací soubory vygenerovat pro úspěšný průchod testů. Další možností jak říct testům, že testovací aplikace nemá být testována s vygenerovanými soubory bylo vytvořit soubor se jménem  `no_expected_directory`.

Pokud vytvoříme testovací aplikaci, která nebude obsahovat proměnnou `no_expected_directory` nebo `expected_dict`, tak nedojde k žádné verifikaci zafreezovaného výstupu.

Na chvíli jsme se zastavili u cssutils.
Testy, které ověřují odkazy v CSS vyhazují deprecation warning.
Založili jsme na to issue. Abychom to vyřešili chtěli jsme se podívat
do zdrojového kódu cssutils, ale ten jsme nikde nenašli,
takže napíšeme e-mail autorovi projektu a zeptáme se ho,
co s tím můžeme udělat.

Pak jsme pořešili, kde jsme zaseklí na našich Pull Requestech.

Poté Petr začal dělat adaptér na Frozen-Flask.
Abychom zajistili, že freezeyt bude umět udělat to stejné,
tak jsme na spustili testy Frozen-Flasku, ale vyměnili jsme importy.
Tvorba adaptéru probíhá tak, že spustíme testy Frozen-Flasku
a podle toho upravujeme/tvoříme adaptér ve freezeytu.
A když jsme o některé funkci/metodě chtěli vědět více,
tak jsme se koukli do dokumentace Frozen-Flask.

> Záznam ze srazu [zde](https://youtu.be/Gm4bO0B2r1A).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
