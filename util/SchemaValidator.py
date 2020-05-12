import json, jsonschema

class SchemaValidator:
    """
    Utility for validating JSON structures according to a provided schema
    """

    @staticmethod
    def is_valid(json_data, schema_filepath):
        """
        Asserts that a JSON dataset matches a provided valid schema file
        Return exception to where its original instantiated.
        Requires custom exception handling in case a custom message is desired.
        """

        with open(schema_filepath) as schema_file:
            schema = json.loads(schema_file.read())
            return jsonschema.validate(json_data, schema)

        return False

