# PyManifest

## Description
Easily build a list of files to process with file, directory, and pattern
filters.

## Requirements

* Python 3.0+
* Pip


## Install & Run

```
pip install pymanifest
python -m pymanifest --directory /path/to/include --ignore-directory /path/to/exclude --file /path/to/single/file
```

## Examples

``` python
# Help command
python -m pymanifest -h
```

``` python
# List all files within current directory and all subdirectories ending
# in .txt
python -m pymanifest --recurse-directory . --pattern *.txt
```

``` python
# List all files within current directory and all subdirectories
# excluding those ending in .py
python -m pymanifest --recurse-directory . --exclude-pattern *.py
```

``` python
# Use directly in code to add all arguments listed from '-h' to your own
# argparse parser
ap = ArgumentParser()
pymanifest.add_args(ap)

# ... Add more args ...

args = ap.parse_args()
files = pymanifest.process_from_args(args)
```

``` python
# Use argument mapping to customize command line parameters to better fit
# your naming scheme.  In this example, all command line parameters will
# appear with '--custom' prepended.  But you can map the argument names
# to anything you like!
arg_map = {
    '--file'                        : '--custom-file',
    '--directory'                   : '--custom-directory',
    '--recurse-directory'           : '--custom-recurse-directory',
    '--manifest'                    : '--custom-manifest',
    '--exclude-file'                : '--custom-exclude-file',
    '--exclude-directory'           : '--custom-exclude-directory',
    '--exclude-recurse-directory'   : '--custom-exclude-recurse-directory',
    '--exclude-manifest'            : '--custom-exclude-manifest',
    '--pattern'                     : '--custom-pattern',
    '--exclude-pattern'             : '--custom-exclude-pattern',
}
ap = ArgumentParser()
pymanifest.add_args(ap, arg_map)

# ... Add more args ...

args = ap.parse_args()

# be sure to pass back the arg_map
files = pymanifest.process_from_args(args, arg_map)
```
