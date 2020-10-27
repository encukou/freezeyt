# Freezeyt sraz čtrnáctý

> Tento článek není hotový. Záznam ze srazu je [zde](https://youtu.be/52pb6IDXxGc).

Tentokrát bylo opět pár pull requestů začleněno již před srazem. Jedním z nich byl PR, který se věnoval mimetypes a k tomuto pull requestu jsme se začátkem srazu vrátili.

> Ze záznamu o začleňování pull requestu o mimetypes
> `git revert <commit>` - zahodí změny z daného commitu a vytvoří nový commit.

## Zamezení přepisování funkcí
Dále jsme se pustili do řešení issue, které by zamezilo tomu, aby se v kódu přepisovaly funkce. Jak už bylo minule zmíněno, šlo by to vyřešit pravděpodobně pomocí linteru. A tak jsme vyzkoušeli [PyFlakes](https://pypi.org/project/pyflakes/). V dokumentaci jsme našli, jak je možné limitovat adresáře. (Aby si to nestěžovalo na adresář tox a virtuální prostředí.) PyFlakes vadilo, že v souboru `__init__.py` máme nepoužitý import, to jsme vyřešili pomocí

```python
__all__=["freeze"]
```

Do toxu jsme přidali i kontrolu pomocí PyFlakes a následně ho přidali do GitHub actions.

Následně byl poslán Pull request.

## Implementace celého protokolu WSGI
Pak jsme se podívali na to, abychom implementovali celý protokol WSGI. První věc, vše musí být v kódování [Latin 1](https://cs.wikipedia.org/wiki/ISO_8859-1) - python používá Unicode - tohle bude dělat problémy, jakmile věci v environ nebudou v tomto kódování. Zbytek budeme řešit příště/později.

> Komentář k pull requestu o mimetyes [zde](https://youtu.be/yKCb8-c_vxw).
> Záznam ze srazu [zde](https://youtu.be/52pb6IDXxGc).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
