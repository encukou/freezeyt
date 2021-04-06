# Freezeyt sraz druhý

> Tento článek není hotový - poznámky jsou napsány do 37. minuty [záznamu](https://youtu.be/xmtqV7PfbD4?t=2219).

Sraz začal kontrolou pull requestů, které přistály na GitHubu.
První z nich upravoval/přidával README. Následně jsme dostali zpětnou vazbu k tomu, jak psát README a co by se na něm dalo ještě vylepšit:
* Obsah - je užitečný, ale spíše pro větší projekty. Je v něm bohužel problém s některými odkazy - GitHub s odkazy pomůže - stačí najet na nadpis a ukáže se tam odkaz na danou sekci. Dále je potřeba myslet na to, že je potřeba každou sekci přidat. Takže bychom ho možná mohli odstranit.
* Cíl projektu - vypadá v pohodě.
* O čem je projekt - ne jen pro PyLadies, ale pro jakéhokoliv začátečníka v Česku. Je tam část o tom, proč projekt vznikl a ne o čem to je.
* README je pro někoho, kdo to chce používat - moc ho nezajímá, jak to vzniklo a jak se do něj zapojit. -> Historii bude lepší přesunout nakonec. Na začátek dát, co to dělá, jak se to používá apod.
* Přidat Flask do příkladů fremeworků.
* Frozen Flask je také komunitní projekt.
* Projekt není založen na else.
* Instalace zatím nejsou nutné, jen pro testy je potřeba instalace. Přidat sekci o tom, jak testovat.
* Použité nástroje nejsou informace o tom, jak se to používá. Je lepší tam napsat něco ve smyslu - zatím se to použít nedá.
* Contributing sekce s omáčkou je fajn - ještě tam můžeme přidat informaci o streamech a info o tom, že to probíhá v ČJ.
* Info o autorech se dá zjistit dle contributors na GitHubu.
* Ujasnili jsme si, jak zapsat licenci do readme a jak to budeme spellovat.

Dále se sešly 2 pull requesty řešící Issue z minula o napsání testu na 2 stránky.
* První PR - začal tím, že přidal funkcionalitu, přišel na všechny problémy. Bohužel ještě formatter black změnil uvozovky. - Pro příště je lepší takové změny dělat zvlášť. Také to trvá déle, než se k tomu někdo dostane. Byla upravena původní aplikace, tím pádem i testy.
* Druhý PR přidal novou aplikaci a nový test, tím jsme zajistili, že nový test nepokazil původní test. Tímto PR bylo začleněno i WSGI demo pro tuto aplikaci, tento soubor není úplně nutný a proto jsme ho odstranili.

> Záznam ze srazu [zde](https://youtu.be/xmtqV7PfbD4).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
