# Skooma

Skooma is a lightweight validation tool for Pandas DataFrames.

Features:

- No dependencies other than Pandas
- Simple, intuitive, lambda-based syntax for validation rules
- Lazy, element-wise validation for easier debugging (executes all rules and logs all invalid values _before_ raising an error)

## Setup

First, import the `Schema` class and the `@validate` decorator:

```python
import pandas as pd
from skooma import Schema, validate
```

For simplicity's sake, we'll create a small Pandas DataFrame with dummy values for testing:

```python
df = pd.DataFrame({
    'nums': range(5),
    'chars': list('abcde')
})

df
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }

</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>nums</th>
      <th>chars</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>a</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>b</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>c</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>d</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>e</td>
    </tr>
  </tbody>
</table>
</div>

## `Schema`

Next, we'll create a schema for our DataFrame using the `Schema` class. To create a new `Schema`, we'll pass in a dictionary with keys corresponding to the columns in `args`. The value for each key is a lambda function that evaluates to `True` or `False` for each unique value in the column. This allows us to go beyond basic data types and set more granular constraints.

For example, let's define a Schema that expects a DataFrame with two columns: `nums` (which must contain only numbers less than 100), and `chars` (which must contain only strings):

```python
example_schema = Schema({
    'nums': lambda x: x < 100 and not isinstance(x, bool),
    'chars': lambda x: isinstance(x, str)
})

# -> <skooma.Schema at 0x116e85f50>
```

Now that we have defined the Schema, we can validate any DataFrame against it by calling the `.validate()` method:

```python
example_schema.validate(df)

# -> True
```

This triggers an element-wise evaluation of every unique value in every column defined in the Schema. If all columns pass validation, then `validate` returns `True`. Otherwise, all invalid values in the column are logged, and `validate` returns `False`.

In this example, all values meet the validation rules, so `.validate()` returns `True`.

Note that if we add `99` to each value in `df['nums']`, then validation will fail—but only after all invalid values are logged:

```python
example_schema.validate(
  df.assign(nums=df['nums'] + 99) # -> [99, 100, 101, 102, 103]
)

# Invalid value in column 'nums': 100
# Invalid value in column 'nums': 101
# Invalid value in column 'nums': 102
# Invalid value in column 'nums': 103
# -> False
```

Similarly, if a value throws an error, then the error will be logged alongside the invalid value:

```python
example_schema.validate(
  df.replace({1: None}) # -> [0, None, 2, 3, 4]
)

# Invalid value in column 'nums': None ('<' not supported between instances of 'NoneType' and 'int')
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
    {'nums': lambda x: x < 100},
    strict=False
)

permissive_schema.validate(df)

# -> True
```

## `@validate`

The `@validate` decorator extends `Schema.validate()` to function arguments and return values.

```python
@validate(
    args=(example_schema, None),
    returns=Schema({'nums': lambda x: x % 2 == 0}, strict=False)
)
def multiply(df: pd.DataFrame, x: int) -> pd.DataFrame:
    return df * x

multiply(df, 2).head()
```

    Validating input at index 0...
    Passed!
    Validating output...
    Passed!

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }

</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>nums</th>
      <th>chars</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>aa</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>bb</td>
    </tr>
    <tr>
      <th>2</th>
      <td>4</td>
      <td>cc</td>
    </tr>
    <tr>
      <th>3</th>
      <td>6</td>
      <td>dd</td>
    </tr>
    <tr>
      <th>4</th>
      <td>8</td>
      <td>ee</td>
    </tr>
  </tbody>
</table>
</div>
