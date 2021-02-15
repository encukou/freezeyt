# Freezeyt sraz devatenáctý

> Tento článek není hotový. Záznam ze srazu je [zde](https://youtu.be/_L2eGHnGHXI).

Začali jsme review Pull requestů - první přidával podporu pro ne ASCII znaky v URL cestě.

Druhý přidával podporu pro odkazy v CSS. Chybí v něm testy na funkci, kterou přidává. Takže stále se jedná o draft.

Poslední, také rozpracovaný, Pull request přidával testy pro CLI. Tak jsme se chvilku nad těmito testy zastavili a zjišťovali, proč to nefunguje.

Následně jsme se bavili o issue s konfiguračním souborem a řešili jsme, jak by to mohlo vypadat.
Chvíli jsme se bavili o funkci `eval`, která je vcelku nebezpečná, když už něco takového potřebujeme, tak je lepší použít `ast.literal_eval()`.

Poté jsme začali řešit, zda to funguje na Windows.

> Záznam ze srazu [zde](https://youtu.be/_L2eGHnGHXI).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
