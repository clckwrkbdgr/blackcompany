blackcompany
============

A nano-CMS for small teams or personal use (PDS) written in Python and based on [bottle.py](https://bottlepy.org/).

Installation
------------

```bash
python ./setup.py build
python -m pip wheel . --no-deps --wheel-dir=dist
python -m pip install --upgrade dist/*.whl
```

Usage
-----

Example of simplest usage:

```python
# mywebserver.py
import blackcompany
import blackcompany.serve

blackcompany.serve.mime.Text.Html.serve('/', '/home/user/web/index.html')

if __name__ == '__main__'
	blackcompany.run_cli(host='0.0.0.0', port=8080)
```

Now it could be run from command line:

```bash
$ python mywebserver.py
```

See [usage](docs/usage.md) for more details.

Development
-----------

Unit tests are written using default `unittest` module,
so they are discoverable via `python -m unittest discover`.

Additional dependencies: `pyfakefs`.
