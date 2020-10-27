# Freezeyt sraz šestnáctý - protokol WSGI

> Tento článek není hotový. Záznam ze srazu je [zde](https://youtu.be/kzIBeKOItgs).

Na začátku jsme si rozdělili, na čem budeme do příště pracovat. A dostali jsme doporučení, jak na to.

Poté jsme pokračovali v procházení protokolu WSGI.

Dostali jsme se k tomu, že `nějaká funkce` musí vracet iterátor s 0 nebo více bytestringy. Iterátorem může být například, seznam, n-tice, nebo [generátor](https://naucse.python.cz/course/mi-pyt/advanced/generators/). Takže soubory, slovníky ani řetězce asi nebudou pro tuto varantu úplně ideální.

Byty musí rovnou poslat, nemůže si je nikam ukládat a posílat je postupně. Takže nás bufferovnání nebude zajímat.
Demo s printem následuje.
Příklad 1
```python
import time

print("abc", end="")
time.sleep(1)
print("def")
```

```python
import time

print("abc", end="", flush=)
time.sleep(1)
print("def")
```

```python
import time
import sys

print("abc", end="")
sys.stdout.flush()
time.sleep(1)
print("def")
```

Procházení vypadá tak, že se postupně otevírají nové issues, případně se dodávají body do todo v [již otevřeném issue](https://github.com/encukou/freezeyt/issues/38).

Pokračovalo se tím, co všechno musí být ve slovníku `environ`.

Došli jsme do poloviny protokolu.

> Záznam ze srazu [zde](https://youtu.be/kzIBeKOItgs).
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
