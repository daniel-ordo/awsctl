#!/usr/bin/env python3

import json
import os
import sys
import re
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

class InvalidMenuConfigurationParameter(Exception):
    "Raised when user specified wrong parameter in menu"
    pass


class Configuration(object):
    def __init__(self, config_path):
        self._config_path = config_path
        self._read_config()

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

    def _print_menu(self):
        print("What would you like to do?\n"
              "add -- for creating a new context\n"
              "del -- to remove existing context\n"
              "mod -- to modify current context"
              "any other will exit")

    def _ask_for_config_data(self, context=None):
        print("what shall be the name of the context?")
        if context and context.get("name") and re.match(r"\w(\w-)*", context["name"]):
            answer = input(f"current name is: {context['name']}, if you still want to use it type [ENTER]")

            if not answer:
                name = context["name"]
            elif re.match(r'\w(w-)*', answer):
                name = answer
            else:
                raise InvalidMenuConfigurationParameter("context shall met the following requirement: \\w(\\w-)*")
        else:
            name = input()

        print("what is the region for this context?")
        if context and context.get("region"):
            answer = input(f"current region is: {context['region']}, if you still want to use it type [ENTER]")

            if not answer:
                region = context["region"]
            else:
                region = answer
        else:
            region = input()

        print("what is the name of the AWS profile you would like to use?")
        if context and context.get("profile"):
            answer = input(f"current profile is: {context['profile']}, if you still want to use it type [ENTER]")

            if not answer:
                profile = context["profile"]
            else:
                profile = answer
        else:
            profile = input()

        return name, region, profile

    def _write_running_config(self):
        if not self.validate_config():
            print("Config is not correctly written, exiting...", file=sys.stderr)
            sys.exit(1)

        with open(self._config_path, "w") as f:
            json.dump(self._running_config, f)

    def configure(self):
        if not os.path.exists(self._config_path):
            name, region, profile = self._ask_for_config_data()
            self._running_config["contexts"] = [{"name": name, "region": region, "profile": profile}]
            self._write_running_config()
            sys.exit(0)

        if not self.validate_config():
            print("Please fix json config file before continuing", file=sys.stderr)
            sys.exit(1)

        self._print_menu()
        answer = input().strip()

        if answer == "add":
            name, region, profile = self._ask_for_config_data()
            self._running_config["contexts"].append({"name": name, "region": region, "profile": profile})
            self._write_running_config()
            sys.exit(0)
        elif answer == "del":
            context_names = [context["name"] for context in self._running_config["contexts"]]
            answer = input("What context would you like to delete " + ", ".join(context_names) + "?").strip()

            if answer in context_names:
                index_of_item_to_delete = context_names.index(answer)

                self._running_config["contexts"].remove(index_of_item_to_delete)
                self._write_running_config()
                sys.exit(0)
            else:
                print("Exiting...")
                sys.exit(1)
        elif answer == "mod":
            context_names = [context["name"] for context in self._running_config["contexts"]]
            answer = input("What element would you like to modify " + ", ".join(context_names) + "?").strip()

            if answer in context_names:
                context_index_to_modify = context_names.index(answer)
                context = self._running_config["contexts"][context_index_to_modify]
                name, region, profile = self._ask_for_config_data(context)
                self._running_config["contexts"][context_index_to_modify]["name"] = name
                self._running_config["contexts"][context_index_to_modify]["region"] = region
                self._running_config["contexts"][context_index_to_modify]["profile"] = profile
                self._write_running_config()
                sys.exit(0)


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
