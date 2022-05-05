import pandas as pd


class Schema:
    def __init__(self, schema: dict, strict=True):
        assert type(schema) is dict
        self.schema = schema
        self.strict = strict  # If True, self.schema must have a rule for every column in the dataframe passed to .validate()

    def validate(self, df: pd.DataFrame) -> bool:
        schema = self.schema
        errors = []
        # If in strict mode, check that all columns appear in Schema
        if self.strict:
            for col in df:
                if not col in schema:
                    errors.append(f"Column '{col}' not found in Schema")
        for col in schema:
            # Check that the column is in the DataFrame
            if not col in df:
                errors.append(f"Column '{col}' not found in DataFrame")
            # If the column is present, test each unique value against the schema requirements
            else:
                func = schema[col]
                if func:
                    # Iterate over NumPy array of unique values
                    for x in df[col].unique():
                        # If the test returns False, catch the bad value
                        try:
                            result = func(x)
                            if result == False:
                                errors.append(f"Invalid value in column '{col}': {x}")
                        # If the test throws an error, catch the error message
                        except Exception as err:
                            errors.append(
                                f"Invalid value in column '{col}': {x} ({err})"
                            )
        if len(errors):
            [print(e) for e in errors]
            return False
        return True


def validate(args=None, returns=None):
    """
    Decorator for validating function inputs/outputs. Takes two named arguments (both optional):

        args: (Schema, Schema...)
        returns: Schema

    'args' takes a tuple of Schema objects that positionally correspond to the decorated function's arguments.
    'returns' takes a single Schema object.
    For each Schema, the decorator validates the corresponding DataFrame. It only executes the decorated function if all inputs/outputs pass validation.
    """

    def validate_i(schemata, args_):
        for i in range(len(schemata)):
            schema_in = schemata[i]
            if schema_in:
                print(f"Validating input at index {i}...")
                df = args_[i]
                if not schema_in.validate(df):  # If DataFrame fails validation...
                    return False
                else:
                    print("Passed!")
                    return True

    def validate_o(schema_out, output):
        print(f"Validating output...")
        if not schema_out.validate(output):
            return False
        else:
            print("Passed!")
            return True

    def decorator(func):
        def decorated_func(*args_):
            # Validate inputs before attempting to run the function
            valid_inputs = validate_i(args, args_) if args else True
            # Do not run the function unless all inputs pass validation
            if valid_inputs:
                output = func(*args_)
                valid_output = validate_o(returns, output) if returns else True
                # Do not return a value unless the output passes validation
                if valid_output:
                    return output

        return decorated_func

    return decorator
