# Linkers and Loaders

My notes from working through the book [Linkers and Loaders](https://linker.iecc.com/).

## Project

### Setup environment

#### Create virtual environment

```sh
py -m venv venv
```

#### Active virtual environment

```sh
venv\Scripts\activate
```

#### Install requirements

```sh
pip install -r requirements.txt
```

### Running tests

```sh
pytest tests
```

### Running project

I need the project modules to access the `linker` module but I don't know a clean way of handling that, so for now I
need to set the `PYTHONPATH` environment variable to point to the root directory so that the `linker` module is found.

```sh
set PYTHONPATH=.
python projects\project_3_1.py ch4main.lk ch4main_copy.lk
```

## Resources

* [MaskRay](https://maskray.me/blog/) - Maintains lld/ELF
* [Rui Ueyama](https://www.sigbus.info/) - Original designer, implementer and owner of lld.
* [Ian Lance Taylor](https://www.airs.com/ian/) - Author of gold. Wrote 20-part essay on
  [linkers](https://lwn.net/Articles/276782/).
* [The Old New Thing](https://devblogs.microsoft.com/oldnewthing/) - Blog by Raymond Chen, lots useful information
  about Windows including some posts about linkers.
