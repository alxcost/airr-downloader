import json, jsonschema

class SchemaValidator:
    """
    Utility for validating JSON structures according to a provided schema
    """

    @staticmethod
    def is_valid(json_data, schema_filepath):
        """
        Asserts that a JSON dataset matches a provided valid schema file

        Raises exception to where its original instantiated if json is invalid:
            - jsonschema.exceptions.ValidationError
            - jsonschema.exceptions.SchemaError

        :return True: if validate check passes
        :returns False: if unable to determine jsonschema file
        """

        with open(schema_filepath) as schema_file:
            schema = json.loads(schema_file.read())
            jsonschema.validate(json_data, schema)
            return True

        return False

