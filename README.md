# Skooma

Skooma is a simple, lightweight, and intuitive validation tool for working with Pandas DataFrames.

## Features

- No external dependencies other than Pandas
- Simple, intuitive, lambda-based syntax for validation rules
- Lazy, element-wise validation for easier debugging (executes all rules and logs all invalid values before raising an error)

## Data types

Skooma has five data types, each represented by a class: `Integer`, `Float`, `Boolean`, `String`, and `DateTime`.

| Skooma class | Pandas dtype | Python type | NumPy type                                                    | Usage                  |
| :----------- | :----------- | :---------- | :------------------------------------------------------------ | :--------------------- |
| **String**   | object\*     | str         | string, unicode                                               | Text                   |
| **Integer**  | int64        | int         | int, int8, int16, int32, int64, uint8, uint16, uint32, uint64 | Integer numbers        |
| **Float**    | float64      | float       | float, float16, float32, float64                              | Floating point numbers |
| **Boolean**  | bool         | bool        | bool\_                                                        | True/False values      |
| **DateTime** | datetime64   | NA          | datetime64[ns]                                                | Date and time values   |

\*_Note that Skooma is opinionated: unlike the Pandas_ `object` _dtype, Skooma's_ `String` _class does not accept mixed numeric and non-numeric values._

## Setup

First, let's import the `Schema`, `Integer`, `Float`, `Boolean`, `String`, and `DateTime` classes, as well as the `@validate` decorator:

```python
import pandas as pd
from skooma import Schema, Integer, Float, Boolean, String, DateTime, validate
```

Then let's create a small Pandas DataFrame with dummy values for each Skooma type:

```python
df = pd.DataFrame({
    'integers': range(5),
    'floats': [x / 2 for x in range(5)],
    'booleans': True,
    'strings': list('abcde'),
    'dates': pd.date_range(start='2022-01-01', end='2022-01-05', freq='D')
})
```

|                    | integers | floats | booleans | strings | dates      |
| :----------------- | :------- | :----- | :------- | :------ | :--------- |
| <strong>0</strong> | 0        | 0.0    | True     | a       | 2022-01-01 |
| <strong>1</strong> | 1        | 0.5    | True     | b       | 2022-01-02 |
| <strong>2</strong> | 2        | 1.0    | True     | c       | 2022-01-03 |
| <strong>3</strong> | 3        | 1.5    | True     | d       | 2022-01-04 |
| <strong>4</strong> | 4        | 2.0    | True     | e       | 2022-01-05 |

## Usage

### The `Schema` class

Let's create a schema for our DataFrame using the `Schema` class.

To create a new `Schema`, we'll pass in a dictionary with keys corresponding to the columns in our DataFrame. The value for each key is an instance of a Skooma datatype. Datatype classes may contain optional lambda functions that evaluate to `True` or `False` for each unique value in the column. This allows us to go beyond basic type checking and set more granular constraints.

For example, let's define a Schema that expects a DataFrame with five columns:

- `integers` must contain only integers less than 5
- `floats` must contain only floats between 0 and 2
- `booleans` must contain only `True` or `False`
- `strings` must contain only single characters
- `dates` must contain datetimes

```python
example_schema = Schema({
    'integers': Integer(lambda x: x < 5),
    'floats': Float(lambda x: 0 <= x <= 2),
    'booleans': Boolean(),
    'strings': String(lambda x: len(x) == 1),
    'dates': DateTime()
})

# -> <skooma.Schema at 0x11435c590>
```

Now that we have defined the Schema, we can validate any DataFrame against it by calling its `.validate()` method:

```python
example_schema.validate(df)

 # ->  True
```

This triggers an element-wise evaluation of every unique value in every column defined in the Schema. If all columns pass validation, then `validate` returns `True`. Otherwise, all invalid values in the column are logged, and `validate` returns `False`.

In this example, all values meet the validation rules, so `.validate()` returns `True`.

Note that if we add `2` to each value in `df['integers']`, then validation will fail—but only after all invalid values are logged:

```python
example_schema.validate(
    df.assign(integers=df['integers'] + 2) # -> [2, 3, 4, 5, 6]
)

# Invalid value in column 'integers': 5
# Invalid value in column 'integers': 6
# -> False
```

Similarly, if a value throws an error, then the error will be logged alongside the invalid value:

```python
example_schema.validate(
  df.replace({1: None}) # -> [0, None, 2, 3, 4]
)

# Invalid value in column 'integers': None
# Invalid value in column 'floats': None
# -> False
```

By default, the Schema is _strict_, meaning that it must have a key for every column in the DataFrame, and likewise every column in the DataFrame must have a key in the Schema.

```python
example_schema.strict

# -> True
```

We can disable this and instead only define validation requirements for a subset of columns by passing the optional argument `strict=False`

```python
permissive_schema = Schema(
    {'integers': Integer(lambda x: x < 5)},
    strict=False
)

permissive_schema.validate(df)

# -> True
```

### The `@validate` decorator

The `@validate` decorator allows us to define `Schema` objects to validate function arguments and return values.

It takes two named arguments (both optional):

        args: (Schema, Schema...)
        returns: Schema

`args` takes a tuple of Schema objects that positionally correspond to the decorated function's arguments.

`returns` takes a single Schema object.

For each Schema, the decorator validates the corresponding DataFrame. It only executes the decorated function if all inputs/outputs pass validation.

```python
@validate(
    args=(example_schema, None),
    returns=Schema({'integers': Integer(lambda x: x % 2 == 0)}, strict=False)
)
def multiply_integers(df: pd.DataFrame, x: int) -> pd.DataFrame:
    df = df.copy()
    df["integers"] = df["integers"] * x
    return df

multiply_integers(df, 2)

# Validating argument at index 0...
# Passed!
# Validating return value...
# Passed!
```

|                    | integers | floats | booleans | strings | dates      |
| :----------------- | :------- | :----- | :------- | :------ | :--------- |
| <strong>0</strong> | 0        | 0.0    | True     | a       | 2022-01-01 |
| <strong>1</strong> | 1        | 0.5    | True     | b       | 2022-01-02 |
| <strong>2</strong> | 2        | 1.0    | True     | c       | 2022-01-03 |
| <strong>3</strong> | 3        | 1.5    | True     | d       | 2022-01-04 |
| <strong>4</strong> | 4        | 2.0    | True     | e       | 2022-01-05 |
