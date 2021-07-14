# Freezeyt sraz devátý - testovací

## Review PR

Opět jsme začali tím, že jsme se podívali na PR, které na GitHubu přistály.

První PR opravoval článek z 6. lekce.
Některé obrázky by byly lepší textově než obrázkově,
například, jedná-li se o příklad nějaké funkce.

Druhý přidával unit testy pro funkci `freezeyt.freezing.parse_absolute_url`,
PR obsahoval pozitivní i negativní testy, takže zadání bylo splněno.

Třetí PR aktualizoval README a docstringy (dokumentační řetězce),
které rozšiřoval o přidané parametry.

Čtvrtý přidával uvozovky do README.

Následně byl čas na dotazy, kdy jsme přišli na to,
že jeden test nebyl pojmenován ideálně.


## Návrat k testům

Jelikož jsme se rozhodli pro testovací metodu
[Gold Master Testing](https://codeclimate.com/blog/gold-master-testing/),
testy budou fungovat tak, že výstup z testů porovnáme s očekávaným výsledkem.

## Rebase větve `reorganize_tests`

Vrátili jsme se k testům, které jsme chtěli přepracovat z předminulého srazu.
Jelikož se mezi touto změnou, která byla pouze na Petrově počítači,
hlavní větev vcelku posunula, podívali jsme se na `git rebase`.
Cíl je vzít změny z naší větve a aplikovat je na současný master.
Může nastat merge conflict, který musíme vyřešit ručně.
(Jakmile to nastane, můžeme se rozhodnout pro více variant,
více info v chybové hlášce gitu.)
`git rebase master` se pokusí dát změny z naší větve „nad“ aktuální master.
Jelikož merge/rebase conflict nastal, tak jsme se chvilku zastavili u toho,
jak tento konflikt vyřešit.
Pokud nastane konflikt, rebase se zastaví, problém musíme vyřešit manuálně,
udělat commit a následně, tak jak nám radí git, použít `git rebase --continue`.

## Porovnávání obsahů dvou adresářů

Ujasnili jsme si, jak mají testy fungovat.
Následně jsme se vrátili do
[dokumentace](https://docs.python.org/3/library/filecmp.html#filecmp.dircmp)
knihovny `filemcp` a zjišťovali, jaké všechny metody třída `dircmp` obsahuje,
a které budeme potřebovat.
Protože tato logika byla složitější,
tak jsme se rozhodli pro to porovnání vytvořit oddělenou funkci.

## Testování testů

A protože se v této logice mohly vyskytnout chyby,
napsali jsme testy na tuto funkci.
V adresáři fixtures jsme přidali adresář s dalšími adresáři,
které se částečně liší od sebe.
A následně jsme přidali funkci, která testuje funkci, která bude v testech.

Když do `assert` dáme podmínku, která neplatí, vyhodí AssertionError.
Když je podmínka platná, tak se nic nestane.

A jelikož je potřeba procházet i podadresáře,
tak jsme funkci rozdělili a vrátili se k rekurzi.

Máme tedy test, který umí porovnat obsah dvou adresářů.

### Odbočka ke Gitu

A teď máme 2 commity, ale jeden z nich nechceme,
chceme změny z těchto commitů sloučit do jedné.

A tak jsme se vrátili ke gitu a došli k interaktivnímu rebase.
```
git rebase --interactive master
```
Stejně jako normální rebase se pokusí aplikovat změny z daných commitů.
Oproti klasickému rebase můžeme ale commity upravit.
(Např. změnit commit message, zbavit se commitu apod.)
Všechny možnosti, které můžeme s danými commity udělat jsou vypsány dole
v nápovědě interaktivního rebase.
U `squash` máme možnost upravit i commit message.

`git reflog` nám ukazuje, jak jsme se posouvali v gitu.
Tady můžeme najít i „ztracené“ commity.

Historie gitu se dá procházet i pomocí `HEAD@{3}`
(kde byla historie před třemi změnami),
případně `HEAD@{3.weeks.ago}` před třemi týdny.

## Příprava očekávaných výstupů

Bylo by dobré, kdybychom si testy nemuseli připravovat plně manuálně,
a proto pomocí proměnné prostředí vyřešíme to,
že si testy očekávané výsledky připraví samy.
Test momentálně zvládne projít jen 1 aplikaci na jednou.
Není dobré, aby test obsahoval for cyklus,
protože jakmile nastane chyba, testy spadnou.

## Parametrizace v testech

Postupně zavoláme daný test s více argumenty pomocí dekorátoru
`@pytest.mark.parametrize()`.

## Kontrola Issues

Ke konci jsme se podívali na issues, které je potřeba vyřešit,
a které mají vyšší prioritu.

> Záznam ze srazu [zde](https://youtu.be/JQMvylmLs2Q).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
