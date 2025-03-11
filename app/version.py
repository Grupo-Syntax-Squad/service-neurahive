# -*- encoding: utf-8 -*-
from os import path
from json import loads
from app.config import WORKING_DIRECTORY

VERSION_FILE = loads(
    open(path.join(WORKING_DIRECTORY, "..", "version.json"), "r").read()
)


VERSION = VERSION_FILE["version"]
DATA_VERSION = VERSION_FILE["date"]