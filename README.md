# py-nexd
Unofficial Python port of [nexd](https://hg.sr.ht/~m15o/nexd)[]()

[NEX Protocol Specification](https://nightfall.city/nex/info/specification.txt)

You can pass a directory to serve files

```py
python py-nexd.py ~/public/gemini/
```

You can make the file executable and run as script

```sh
# add shebang to the top of the file
#! /usr/bin/python
```
then make it executable
```sh
chmod u+x py-nexd.py
```

it will serve `index` files by default, or list directory contents as links

This is a work in progress. Will add more functionality as I need it. 

