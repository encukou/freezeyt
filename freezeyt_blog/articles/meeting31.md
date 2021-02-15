# Freezeyt sraz třicátý první -

> Tento článek není hotový. Záznam ze srazu je[zde](https://youtu.be/5STdOQa2Mko).

Na GitHubu bylo tento týden 8 pull requestů (PR), takže jsme začali s review.

První z nich ověřoval, že v host name mohou být i ne-ASCII znaky

Další pull request zapracovává detaily protokolu WSGI. Při review jsme zjistili, že v setup.py máme verzi. 0.1 a v `SERVER_SOFTWARE` byla verze 0.0

Dále byla přidána konfigurace blogu, takže teď by mohly GH pages blogu fungovat. Před tím tam byly špatné odkazy. A už to funguje.
Do budoucna by bylo fajn, kdyby na blogu byla i dokumentace. Blog by možná bylo fajn přidat nějaké CSS, aby ten blog i nějak vypadal.

Pak jsme začlenili PR z minula, který zajistí, že freezeyt smaže adresář před freezem. Zde byl jen approve a žádné komentáře s dotazy, takže jsme jej jen začlenili.

Další mazal soubory a adresáře s ne-ascii znaky v repozitáři. Tady bylo také review bez dotazů, také začleněn během chvilky.

Další PR přidával slovníky s expected output. Problémem je, že GH actions neprocházely, protože Pyflakes narazilo na Recursion limit, protože celý soubor s očekávaným slovníkem má přes 4000 řádků.

Další přidával článek na blog, zjistili jsme, že GH Actions se chovají jinak k prázdným odkazům než naposledy. Když to píšu, tak jsem zjistila, že minule závorky nebyly prázdné ale byla v nich poznámka o tom, že je potřeba přidat odkaz.

Poslední PR prováděl malé změny na blogu.

Nakonec jsme se podívali na to, co by bylo do budoucna dobré udělat, aby někdo mohl přejít na freezeyt.
Tak jsme se podívali na web [pyladies.cz](https://pyladies.cz/).
Přišli jsme na to, že by bylo dobré, kdyby byl freezeyt schopen vzít funkci, která vygeneruje odkazy a vrátí je.

Podívali jsme se na to, aby jméno proměnné bylo nakonfigurovatelné. (Jiné než tradiční `app`.)
Jako tradičně jsme začali testy.
Potom jsme testy upravili.

> Tady chybí část od cca 1:00 po 1:30 záznamu.

Netvořil se adresář s očekávaným výstupem, pak jsme si uvědomili, že by se měl tvořit jen u modulů, kde je soubor `app.py`

Na chvilku jsme se zastavili u slovíček override a overwrite.

Pak jsme se na chvilku zastavili u formátovacích řetězců
{s=}
{s!r}
{s!a}

> Záznam ze srazu [zde](https://youtu.be/5STdOQa2Mko).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
