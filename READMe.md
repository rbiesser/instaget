# Instaget

## Usage

```bash
python instaget.py <username>
python instaget.py --help
```

## Help
```bash
usage: instaget.py <username>

positional arguments:
  username       An Instagram username

optional arguments:
  -h, --help     show this help message and exit
  -i, --images   Get only images
  -V, --videos   Get only videos
  -b, --both     Get all images and videos, same as -iV
  -f, --fetch    Fetch latest profile
  -r, --resume   Resume a previous session
  --limit LIMIT  Get the newest n posts
  --dry-run      Skip downloading is the default
  -v, --version  show program's version number and exit

Save an Instagram story.
```

## Create the environment
https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/

```bash
python -m venv venv
pip install -r requirements.txt
```

## Activate the environment

```bash
# MacOS and Linux
source venv/bin/activate

# Windows VSCode
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\activate
```

## Libraries

### argparse
https://docs.python.org/3/library/argparse.html

### pathlib
https://docs.python.org/3/library/pathlib.html#correspondence-to-tools-in-the-os-module

### pillow
https://pillow.readthedocs.io/en/stable/

### piexif
https://piexif.readthedocs.io/en/latest/