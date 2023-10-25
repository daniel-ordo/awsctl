import json
import os
import pytest
from jsonschema import validate, exceptions
from awsctl import config_schema


def get_all_json_schema_tests():
    for test_dir in os.listdir(os.path.join("tests", "json_schema_tests")):
        expected_file = os.path.join(os.path.join("tests", "json_schema_tests", test_dir, "expected.txt"))
        test_file = os.path.join(os.path.join("tests", "json_schema_tests", test_dir, "test_file.json"))

        yield test_file, expected_file


@pytest.mark.parametrize("test_file,expected_file", get_all_json_schema_tests())
def test_if_short_correct_config_is_ok(test_file, expected_file):
    with open(expected_file, "r") as f:
        expected_file_content = f.read().strip()
        assert expected_file_content in ["fail", "pass"]
        expected = expected_file_content

    with open(test_file, "r") as f:
        if expected == "pass":
            assert validate(json.load(f), schema=config_schema) is None
        else:
            try:
                assert validate(json.load(f), schema=config_schema)
            except exceptions.ValidationError:
                assert True
