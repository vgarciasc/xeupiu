# Development guide

## Running from source

For development, or to get the latest and greatest code, you can run from source. Clone the repo somewhere locally. Create a Python 3.11 environment with your favorite tool (pyenv/conda/pixi/etc), and then pip install. If you want to do development then you can do an editable install with
```
pip install -e . --config-settings editable_mode=compat
```

This will install a command `xeupiu` into your environment that will run the translation tool.

## Packaging for release

Pyinstaller is used to package for release. This can be done with the convenience script
```
package_executable.bat
```
on windows or
```
package_executable.sh
```
on linux.