import json
import os
import sys
from jsonschema import validate, exceptions


config_schema = {
    "type": "object",
    "properties": {
        "contexts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "region": {"type": "string"},
                    "profile": {"type": "string"},
                    "login_script": {"type": "string"}
                },
                "required": ["name", "region", "profile"],
            }
        },
        "current_context": {"type": "string"}
    },
    "required": ["contexts"]
}


class Configuration(object):
    def __init__(self, config_path):
        self._config_path = config_path
        self._running_config = None

    def _read_config(self):
        if os.path.exists(self._config_path):
            self._running_config = json.load(self._config_path)
        else:
            self._running_config = {}

    def read_config_file(self):
        self._read_config()
        return self._running_config

    def validate_config(self):
        if not self._running_config:
            return False

        try:
            validate(self._running_config, schema=config_schema)
            return True
        except exceptions.ValidationError as ex:
            print(str(ex), file=sys.stderr)
            return False

    def menu(self):
        print("")

    def _ask_for_config_data(self):
        print("")

    def configure(self):
        pass


class AwsCtl(object):
    def __init__(self, config_path=None):
        if config_path:
            self._config_path = config_path
        else:
            self._config_path = os.path.expanduser("~")
        self._config = Configuration(self._config_path)


def main(argv=None):
    pass


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
