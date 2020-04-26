Create a **python3-videomass.deb** package for your Debian or Debian-based distribution.

Before proceeding go to the [Dependencies](https://github.com/jeanslack/Videomass/wiki/Dependencies) page and follow it to install Python3, then download the [Videomass sources code](https://github.com/jeanslack/Videomass/releases)

### Install the following tools
```
~# apt-get update && apt-get install python3-all python3-stdeb fakeroot
```
This will installs all the need dependencies, including python-setuptools.
Then, go into Videomass sources unzipped folder with your user (not root)

- To generate both source and binary packages type:

```
~$ python3 setup.py --command-packages=stdeb.command bdist_deb
```

The command above should create a python3-videomass_version_all.deb_ in
the new _deb_dist_ directory, installable with

```
~# dpkg -i python3-videomass_version_all.deb
```

- To generate a source packages only:

```
~$ python3 setup.py --command-packages=stdeb.command sdist_dsc
```

#### Resources:

<https://pypi.python.org/pypi/stdeb>
<http://shallowsky.com/blog/programming/python-debian-packages-w-stdeb.html>
