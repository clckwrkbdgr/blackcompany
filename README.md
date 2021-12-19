blackcompany
============

A nano-CMS for small teams or personal use (PDS) written in Python and based on bottle.py.

Usage
-----

```python
import blackcompany
```

or (for concurrent web service), as the very first line of the file:

```python
import blackcompany.concurrent
...
import blackcompany
# or even:
import blackcompany.concurrent as blackcompany
```

and then to have CLI runner:

```python
if __name__ == '__main__'
	blackcompany.run_cli(host=..., port=...)
```

Now it could be run from command line:

```bash
$ python -m mywebserver [--debug] ...
```
