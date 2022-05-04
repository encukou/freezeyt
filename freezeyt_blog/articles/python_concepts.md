## Python koncepty

* **contextmanager**
    * [official-docs](https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager)
    * [freezeyt-yt-video-72 (52:30)](https://www.youtube.com/watch?v=khUfxwQKX6s&t=3150s)

* **functools.lru_cache (cache načítání souborů yaml)**
    * [official-docs](https://docs.python.org/3/library/functools.html#functools.lru_cache)
    * [freezeyt-yt-video-77 (01:31:00)](https://www.youtube.com/watch?v=osaVARgxpgo&list=PLFt-PM7J_H3EU5Oez3ZSVjY5pZJttP2lT&index=78)

* **git worktree add (v kombinaci s příkazem meld)**
    * [official-docs](https://git-scm.com/docs/git-worktree)
    * [freezeyt-yt-video-78 (00:29:20)](https://www.youtube.com/watch?v=Zi1Yhnpz5g8&list=PLFt-PM7J_H3EU5Oez3ZSVjY5pZJttP2lT&index=79)

* **async**
    * [root.cz](https://www.root.cz/clanky/soubezne-a-paralelne-bezici-ulohy-naprogramovane-v-pythonu/)
    * [naucse.python.cz](https://naucse.python.cz/course/mi-pyt/intro/async/)

* **Pokročilé objektově orientované programování**
   * [freezeyt-yt-video-79 (31:38) - magická metoda `__new__` ve třídách a jak se liší od `__init__` metody](https://www.youtube.com/watch?v=znpSzRKgohw&t=1898s)
   * [freezeyt-yt-video-79 (1:12:40) - jak fungují objekty v Pythonu, aneb descriptory a metody `__get__` a `__set__`](https://www.youtube.com/watch?v=znpSzRKgohw&t=4360s)

* **git rebase**
    * [official-docs](https://git-scm.com/docs/git-rebase)
    * [git online book](https://git-scm.com/book/en/v2/Git-Branching-Rebasing)
    * [freezeyt-yt-video-82 (02:42)](https://www.youtube.com/watch?v=Mv4Q9ktBBRk&t=162s)
    * [freezeyt-yt-video-82 (59:20)](https://www.youtube.com/watch?v=Mv4Q9ktBBRk&t=3560s)

* **Význam "double underscored" atributů (např. `__note__`)**
    * [freezeyt-yt-video-82 (01:27:55)](https://www.youtube.com/watch?v=Mv4Q9ktBBRk&t=5275s)

* **ASCII, Unicode, kódování UTF-8 a vztah mezi nimi**
    * [freezeyt-yt-video-84 (00:58:30)](https://youtu.be/CpemKarhGik?t=3511)
        * [Corrections](https://github.com/encukou/freezeyt/pull/290#issuecomment-1098882874)
    * [must-know-about-unicode-and-character-sets-no-excuses](https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/)
    * [encodings and character sets to work with text](https://kunststube.net/encoding/)
    * [unicode table](https://www.utf8-chartable.de/unicode-utf8-table.pl)

* **Rozdíl mezi použitím argparse.namespace, SimpleNamespace, dict, namedtuple a dataclass**
    * [freezeyt-yt-video-87 (00:11:35)](https://youtu.be/00_EJ1J0bcs?t=695)
    * [argparse.Namespace](https://docs.python.org/3/library/argparse.html#the-namespace-object)
    * [SimpleNamespace](https://docs.python.org/3/library/types.html#types.SimpleNamespace)
    * [namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple)
    * [dataclass](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass)

* **Vytvoření instalačního balíčku wheel, nahrání na pypi a příkazu build (wheel, sdist)**
    * [freezeyt-yt-video-87 (00:46:12)](https://youtu.be/00_EJ1J0bcs?t=2772)
    * [pip wheel](https://pip.pypa.io/en/stable/cli/pip_wheel/)
    * [příkaz build](https://pypa-build.readthedocs.io/en/latest/)
        Příkaz `python -m build` vytvoří dva soubory ve složce `dist`:
            * wheel - instalační balíček
            * sdist - archiv zdrojového kódu (`.tar.gz`)
    * [nahraj wheel na pypi pomocí přikazu twine](https://twine.readthedocs.io/en/latest/#twine-upload)
    * [nahraný projekt na pypi](https://pypi.org/project/freezeyt/)
