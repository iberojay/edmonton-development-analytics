# Data Quality Checks

## Transformation Validation

- Raw and cleaned datasets both contain 120,492 records.
- No nonempty values became missing during date or numeric conversion.
- Repeated neighbourhood classification labels were removed while preserving mixed classifications.

## Missing Neighbourhood Names

Initially, 29 records were missing neighbourhood names and six were missing neighbourhood IDs.

Using existing records with a single ID and a single name, we recovered 23 missing names. The lookup was checked for conflicting names before filling values.

Six records still have both the neighbourhood ID and name missing. These records were retained with missing values.

## Neighbourhood Lookup Coverage

Some permit records contain multiple neighbourhood IDs in one cell.

We split these cells into individual IDs and checked whether each ID had a name available from records containing a single ID and a single name.

Four IDs had no matching name in that lookup. We inspected their original permit records and checked a reference dataset.

| ID | Candidate neighbourhood name | Verification status |
|---|---|---|
| 3381 | RIVER VALLEY GLENORA | Confirmed in reference dataset |
| 5456 | HERITAGE VALLEY AREA | Confirmed in reference dataset |
| 4451 | RIVER VALLEY OLESKIW | Confirmed in reference dataset |
| 6212 | ELLERSLIE AREA | Suggested by permit records; unconfirmed |

ID 6212 remains unconfirmed. The reference dataset contains
ELLERSLIE (6211) and ELLERSLIE INDUSTRIAL (6214), but no entry
for 6212. Permit records suggest ELLERSLIE AREA.

The three verified reference mappings were added to the coverage
lookup. Only neighbourhood ID 6212 remains unmatched.

Coverage validation passed: all IDs appearing in multi-ID permit
records have a name in the combined lookup. Three supplemental
mappings were confirmed using the neighbourhood reference dataset;
6212 → ELLERSLIE AREA was inferred from permit record 065305222-040.

### Reference Source

- Dataset: City of Edmonton — Neighbourhoods
- File: City_of_Edmonton_-_Neighbourhoods_20261017.csv
- URL: https://data.edmonton.ca/City-Administration/City-of-Edmonton-Neighbourhoods/65fr-66s6
- Date checked: [Date you checked it]

### Remaining Work

- Add the three confirmed mappings to the neighbourhood lookup.
- Investigate ID 6212 before assigning a name.
- Handle permits associated with multiple neighbourhoods when designing database relationships.