# Freezeyt sraz třetí

> Tento článek není hotový - poznámky jsou napsány do [této](https://youtu.be/Jl3n5UI_1H4?t=1065) části záznamu.

## Review pull requestů
Začali jsme review pull requestů (PR), které tam tentokrát byly celkem tři. První přidával *.pytest_cache* do *.gitignore*.
Druhý PR upravoval README

### Odbočka k začleňování PR
Administrátoři daného repozitáře mají v základu tři možnosti, jak začlenit PR.
* Merge commit - v historii bude nový commit, který začleňuje změny z PR. Tato možnost je tam od základu. Původní větev bude tak, jak je - nenaruší to větev, ze které byl vytvořen PR, takže se ve změnách může pokračovat.
* Squash - vezme všechny změny kódu a všechny commit messages z daného PR, udělá z nich jeden commit a ten commit začlení do master (případně jiné větve). Celý PR je 1 commit - danou commit message můžeme upravit. Problém s posíláním dalších PR ze stejné větve, protože pak bychom poslali i revize, ze kterých už jsou změny začleněné.
* Rebase - všechny revize (commity) z pull requestu postupně „posadí“ na commity v master. Tady je také problém s pokračováním v práci na stejné větvi.
* Čtvrtá možnost, pro kterou na GitHubu není tlačítko, je aby současný master obsahoval změny z daného PR. Vedle toho tlačítka je ale možnost *view command line instructions*, kde je popsán celý postup.

> Záznam ze srazu [zde](https://youtu.be/Jl3n5UI_1H4).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
