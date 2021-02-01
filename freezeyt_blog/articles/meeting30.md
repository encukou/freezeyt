# Freezeyt sraz dvacátý osmý - mazání adresářů

Na začátku jsme se koukli na Pull requasty od minula - první přidával článek
na blog z 27. lekce.
Další se pokoušel „opravit“ blog - na blogu momentálně nefungují odkazy,
tak jak by měly, protože místo toho, aby odkaz na další článek směřoval na
adresu `/freezeyt/meeting01`, tak odkaz směřuje na adresu `/meeting01/`,
a proto blog vyhodí chybu 404, když se budeme chtít na článek dostat
z hlavní stránky blogu.

Další PR přejmenovával testy, aby se jmenovaly přibližně stejně,
aby byly konzistentní.
Před tím byly v některých názvech testů podtržítka a v jiných pomlčky.
Některé názvy aplikací začínaly s `demo_`.
Teď testy vypadají lépe.

Dále jsme se podívali na PR s kódováním hostname.
Následně jsme řešili, že hostname se kóduje trochu jinak, než bychom čekali.
Tak jsme se dozvěděli, jak s PR pokračovat a chvilku jsme se zastavili u kódování.

Potom jsme se dozvěděli, jak pokračovat s našimi rozpracovanými pull requesty.

Následně jsme se vrátili k nastavení serveru WSGI a hledali jsme,
jaké všechny hlavičky musíme předat dle standardu.
Také jsme pokračovali vyhazováním příslušných chyb.
Vypadá to, že vše z poznámek, které jsme do issue napsali před několika týdny,
je zapracováno.

Takže jsme se vrátili k rozpracovanému pull requestu.
V průběhu commitování jsme objevili necommitnutou změnu,
která přidávala `SERVER_SOFTWARE` s verzí freezeyt do slovníku `environ`.
Následně jsme uvažovali, proč jsme to tam chtěli přidat.
Tak jsme opravili změny, na které si stěžovaly pyflakes.

Koukli jsme se na otevřené issues a rozhodli jsme se pracovat na tom,
že freezeyt smaže existující adresář, před tím, než do něj začne ukládat stránku.

Začali jsme, jako už klasicky dle TDD, napsáním testů.
A pak jsme je začali opravovat.
Poté, co jsme začali upravovat freezeyt jsme zjistili,
že vestavěná chyba `FileExistsError` není úplně výstižná.
Výjimky v Pythonu jsou v jisté [hierarchii](https://docs.python.org/3/library/exceptions.html#exception-hierarchy).
Přesnější by bylo, kdyby se chyba jmenovala `DirectoryExistsError`.
A tak jsme si ji vytvořili.
Vytvoření vlastní chyby v Pythonu znamená podědit z nějaké třídy
z výše zmiňované hierarchie.
Následně jsme přidali možnost smazat původní adresář.
PyFlakes si stěžovalo jen na to, že u některých formátovacích řetězců
nevkládáme žádnou proměnnou.
Do README jsme napsali poznámku o tom, že freezeyt smaže existující adresář.

> Tip pro práci v terminálu, když píšete nějaký příkaz, ale ještě přesně nevíte,
> jak by měl končit, na začátek řádku napište `#` a tím to „zakomentujete“.
> (Ekvivalentní příkaz na Windows je `rem`.)

Rozhodli jsme se z repozitáře smazat soubory s „divnými“ názvy.
Tím jsme vyřešili jedno issue.
Abychom nepřišli o testy, které tyto soubory používaly,
převedli jsme je na testy pouze s výstupem do slovníku.

Nakonec jsme zkontrolovali, že v repozitáři nezbyly žádné soubory s divnými jmény.
> Na to jsme použili tento příkaz: `ls -R | grep '[^-a-zA-Z0-9._/:]'`.
> Tento příkaz nebude fungovat na Windows.
> `ls -R` - rekurzivně prohledá adresář (a vrátí názvy souborů).
> Pomocí `|` předáme výstup z předchozího programu dalšímu programu.
> V tomto případě je to `grep`, který najde výsledky,
> které odpovídají danému regulárnímu výrazu.
> regulární výraz `[^-a-zA-Z0-9._/:]` odpovídá všemu bez pomlčky, tečky,
> podtržítka, lomítka, dvojtečky velkých a malých písmen (bez diakritiky)
> a číslic v názvu souboru.

Na chvíli jsme se zastavili u příkazu `git cherry-pick` - ten může na danou
větev přidat i commit, ke kterému se nedostaneme z žádné větve
(protože byla například smazána).
Dostaneme se k němu právě proto, že známe jeho commit hash.
V Gitu existuje [příkaz](), který by tyto commity ze „vzduchoprázdna“ dokáže vylovit.
(V případě, že je nenajdeme v reflogu (`git reflog`).)

Od `git cherry-pick` nebylo moc daleko ke `git rebase`. Tak jsme se zastavili i u toho.
Při rebase se mění historie, a proto se mění i commit hashe daných commitů.
A poznámka bokem, `git rebase` se používá jen u větví v pull requestech,
rozhodně ne v těch oficiálních (ostatním to znesnadní práci).

A když už jsme u toho měnění historie a věcí, které by se neměly dělat,
tak master větve (hlavní větve) u forknutých repozitářů jsou dobré na testování
věcí (protože by na nich nikdo neměl dále „stavět“),
pro které je potřeba, že je to commit v masteru (například GH Actions).
> A tip nakonec, už jsme se o tom na nějakém dřívějším srazu bavili,
> ale když chcete pushnout změny z jedné větve do jiné, tak to jde udělat
> třeba takto `git push <jmeno_remote> master:blog-config`

> Záznam ze srazu [zde](https://youtu.be/lEIp9cmwZ88).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
