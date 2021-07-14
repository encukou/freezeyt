# Freezeyt sraz čtyřicátý devátý

Sraz začal tím, že jsme se podívali na otevřené PR.
Jeden jsme začlenili a o druhém jsme diskutovali, jak dál.

Při review PR jsme došli k tomu, že testy na získávání odkazů z CSS dělají
pořád to stejné, takže by se daly parametrizovat.
Z testovacích dat jsme udělali slovník, aby testy měli normální názvy.
(Místo zdrojového kódu aplikace jako názvu testu.)

Při tom jsme přišli na to, že v této funkci je chyba,
protože jakmile je v aplikaci jiné kódování,
tak funkce skončí s UnicodeDecodeError, místo toho aby vrátila výsledek.
Freezeyt spadne, přestože dostane validní aplikaci.

Přišli jsme na to, že podobný problém by mohl nastat i v případě,
že HTML hlavičky budou obsahovat jiný charset než UTF-8

Následně jsme se podívali na issues.
Jedno nově otevřené issue jsme prodiskutovali a zavřeli.

Podívali jsme se na issue,
které žádá možnost zkopírovat celý adresář statických souborů.
Začali jsme dokumentací s představou, jak by se to dalo používat.

Na konci jsme si dali odbočku k [`__subclasscheck__`](https://docs.python.org/3/reference/datamodel.html?highlight=__subclasscheck__#class.__subclasscheck__)
a [`__subclasshook__`](https://docs.python.org/3/library/abc.html?highlight=__subclasshook#abc.ABCMeta.__subclasshook__)

Zde je demo kód:
```python
class Meta(type):
    def __subclasscheck__(cls, maybe_subclass):
        if maybe_subclass == Trifid:
            return True
        return super().__subclasscheck__(maybe_subclass)

class Zviratko(metaclass=Meta):
    pass

class Kotatko(Zviratko):
    pass

class Rostlina:
    pass

class Trifid(Rostlina):
    pass

print(issubclass(Kotatko, Zviratko))
print(isinstance(Kotatko(), Zviratko))

print(issubclass(Kotatko, Rostlina))
print(isinstance(Kotatko(), Rostlina))

print(issubclass(Trifid, Zviratko))
print(isinstance(Trifid(), Zviratko))
```

A zde je další:
```python
from collections.abc import Container

class K:
  def __contains__(self, element):
    return (element == 1)

k = K()
pritn(1 in k)
print(12 in k)

print(issubclass(K, Container))
```

> Záznam ze srazu [zde](https://youtu.be/FAQjBZlveJU).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
