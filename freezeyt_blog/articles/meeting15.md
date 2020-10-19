# Freezeyt sraz patnáctý - odbočka o kódování

Při psaní minulého článku vyvstala otázka ohledně kódování, a tak jsme tomuto
tématu věnovali první polovinu srazu a učinili „menší“ odbočku.
V [záznamu](https://youtu.be/8AITa5OzcnQ) do 34:50.
Více počtení o kódování [zde](https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/)
a pak ještě [zde](https://hsivonen.fi/string-length/).

Poté jsme se vrátili k projektu. Začali jsme (klasicky) kontrolou Pull requestů.
První PR zajišťoval, že freezeyt uhodne správný mimetype.
Druhý PR zajišťoval zmrazení blogu. K „dokonalosti“ mu (zatím) chybí jen název
toho workflow, aby to nebylo `.github/workflows/freezeyt_blog.yaml / build blog content`.
Poslední PR přidával do README informaci o tom, na jaké verzi byl blog testovaný.

Na konci jsme se vrátili k issue, které se věnuje implementaci celého protokolu
WSGI, takže byly založeny další issues, tudíž máme práci do příště. Přišli jsme
na to, že nám ve funkci `start_response` chybí jeden nepovinný argument.
A funkce `start_response` nevrací, co by měla vracet z důvodu zpětné kompatibility
se staršími frameworky.

> Záznam ze srazu [zde](https://youtu.be/8AITa5OzcnQ).
> Záznam s přeskočenou odbočkou o kódování [zde](https://youtu.be/8AITa5OzcnQ?t=2086)
> Více informací o projektu [zde](https://tinyurl.com/freezeyt).
