import json, jsonschema

class SchemaValidator:
    """
    Utility for validating JSON structures according to a provided schema
    """

    @staticmethod
    def is_valid(json_data, schema_filepath):
        """
        Asserts that a JSON dataset matches a provided valid schema file

        Raises the following exceptions any of the provided JSONs are invalid:
            - jsonschema.exceptions.SchemaError     -> Invalid JSON Schema
            - jsonschema.exceptions.ValidationError -> Invalid JSON

        :return True: if validate check passes with no exceptions
        :returns False: default fail state
        """

        with open(schema_filepath) as schema_file:
            schema = json.loads(schema_file.read())
            jsonschema.validate(json_data, schema)
            return True

        return False

