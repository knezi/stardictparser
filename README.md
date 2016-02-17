Zápočtový program pro první semestr na Matematicko-fyzikální fakultě

INSTALACE
=========
Závislosti:

`python`

Pro kompilaci readidx:

`gcc, python-dev` (v Archu již součástí systému)

Ve složce je již zkomplivaný modul readidx pro x86\_64. Pro opětovnou kompilaci stačí odkomentovat první dvě řádky v build.sh

POUŽITí
=======
./main.py - parser

./find.py - prohledává textový formát

Přesný popis parametrů viz ./main.py -h a ./find.py -h

TESTOVÁNÍ
=========
Stačí spustit ./build.sh. Stáhnou se slovníky do složky data a v res se objeví již v textovém formátu. Je tam příklad různých verzí - viz data/get

PROGRAMÁTORSKÁ DOKUMENTACE
==========================
Popis stardict na adrese: https://web.archive.org/web/20131108165307/http://code.google.com/p/babiloo/wiki/StarDict format

Program zvládá verze 2.4.2 a 3.0.0 se sametypesequence={m,g,h,t}.

Textový formát začíná hlavičkou:

`#DICTFORMAT:k@d@p`

Kde @ je oddělovač a písmena za dvojtečkou specifikují, která pole jsou v každém záznamu.

Každá další řádka je jeden záznam. Nepřítomnost nějakého pole je ekvivalentní ''.

Formát escapuje \n a oddělovač.

ZDROJOVÝ KÓD
============

main.py
-------
Načítá vstup, prochází složku se slovníky a na každý slovník pouští Třídu Parser, která se stará o samotné parsování. Dále ještě dekomprimuje soubory, pokud jsou v gzip formátu.


parse.py
--------
Obsahuje třídu Parser, metoda parse přebírá cesty k souborům vstupním i výstupním a stará se o samotný převod do txt formátu.


exceptions.py
-------------
Definuje nové chyby pro slovníky.


readidx.c
---------
Modul v c, který umožňuje číst idx soubor.

startRead dostane cestu a velikost idxoffset (4B vs. 8B).

nextRecot vrátí překódovaný další záznam do UTF-8 a zároveň se stará o překódování z Big endianu.

stopRead uvolní zdroje.

find.py
-------
Veškeré vyhledávání se provádí v tomto souboru.
