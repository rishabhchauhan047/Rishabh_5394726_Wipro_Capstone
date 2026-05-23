from configparser import ConfigParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "config.ini"


def read_config(path=CONFIG_PATH):
    parser = ConfigParser()
    parser.read(path, encoding="utf-8")
    return parser


def get_config_value(section, option, fallback=None):
    parser = read_config()
    return parser.get(section, option, fallback=fallback)


def get_config_bool(section, option, fallback=False):
    parser = read_config()
    return parser.getboolean(section, option, fallback=fallback)


def get_config_int(section, option, fallback=0):
    parser = read_config()
    return parser.getint(section, option, fallback=fallback)
