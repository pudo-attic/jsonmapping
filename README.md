# jsonmapping [![Build Status](https://travis-ci.org/pudo/jsonmapping.svg?branch=master)](https://travis-ci.org/pudo/jsonmapping)

To transform flat data structures into nested object graphs matching JSON
schema definitions, this package defines a mapping language. It defines how
the columns of a source data set (e.g. a CSV file, database table) are to be
converted to the fields of a JSON schema.

The format allows mapping nested structures, including arrays. It also supports
the application of very basic data transformation steps, such as generating a
URL slug or hashing a column value.

## Example mapping

The mapping format is independent of any particular JSON schema, such that
multiple mappings could be defined for any one particular schema.

```json
{
    "schema": {"$ref": "http://www.popoloproject.com/schemas/person.json"},
    "mapping": {
        "id": {"column": "person_id"},
        "name": {"column": "person_name"},
        "memberships": [{
            "mapping": {
                "role": {"default": "Member of Organization"},
                "organization": {
                    "mapping": {
                        "id": {
                            "columns": ["org_id"],
                            "constant": "default-org"
                        },
                        "name": {
                            "column": "org_name",
                            "constant": "Default Organization",
                            "transforms": ["strip"]
                        }
                    }
                }
            }
        }]
    }
}
```

This mapping would apply to a four-column CSV file and map it to a set of
nested JSON objects (a [Popolo](http://www.popoloproject.com/) person, with a
membership in an organization).

## Data Transforms

While ``jsonmapper`` is not a data cleaning tool, it supports some very basic
data transformation operations that can be applied on a particular column or
set of columns. These include:

* ``coalesce``: Select the first non-null value from the list of items.
* ``slugify``: Transform each string into a URL slug form.
* ``join``: Merge together the string values of all selected columns.
* ``upper``: Transform the text to upper case.
* ``lower``: Transform the text to lower case.
* ``strip``: Remove leading and trailing whitespace.
* ``hash``: Generate a SHA1 hash of the given value.

## Tests

The test suite will usually be executed in it's own ``virtualenv`` and perform a
coverage check as well as the tests. To execute on a system with ``virtualenv``
and ``make`` installed, type:

```bash
$ make test
```
