import os
import json

from jsonschema import Draft4Validator


def validate_mapping(mapping):
    """ Validate a mapping configuration file against the relevant schema. """
    file_path = os.path.join(os.path.dirname(__file__),
                             'schemas', 'mapping.json')
    with open(file_path, 'rb') as fh:
        validator = Draft4Validator(json.load(fh))
        validator.validate(mapping)
    return mapping
