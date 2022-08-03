from connexion.decorators.response import ResponseValidator
from connexion.json_schema import NullableEnumValidator, NullableTypeValidator, Draft4Validator, validate_writeOnly, ValidationError, extend
from flask_sqlalchemy.model import camel_to_snake_case


def validate_required(validator, required, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    for prop in required:
        prop = camel_to_snake_case(prop)
        if prop not in instance:
            properties = schema.get("properties")
            if properties is not None:
                subschema = properties.get(prop)
                if subschema is not None:
                    if "readOnly" in validator.VALIDATORS and subschema.get("readOnly"):
                        continue
                    if "writeOnly" in validator.VALIDATORS and subschema.get(
                        "writeOnly"
                    ):
                        continue
                    if (
                        "x-writeOnly" in validator.VALIDATORS
                        and subschema.get("x-writeOnly") is True
                    ):
                        continue
            yield ValidationError("%r is a required property" % prop)


class CustomResponseValidator(ResponseValidator):
    def __init__(self, operation, mimetype):
        validator = extend(
            Draft4Validator,
            {
                "type": NullableTypeValidator,
                "enum": NullableEnumValidator,
                "required": validate_required,
                "writeOnly": validate_writeOnly,
                "x-writeOnly": validate_writeOnly,
            },
)
        super().__init__(operation, mimetype, validator)
