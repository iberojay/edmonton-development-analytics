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
| 6212 | ELLERSLIE AREA | Inferred from permit record 065305222-040 |

ID 6212 was absent from the reference dataset. Its mapping to
ELLERSLIE AREA was inferred from permit record 065305222-040,
using the independently confirmed mapping of 6214 to
ELLERSLIE INDUSTRIAL.

Coverage validation passed: all IDs appearing in multi-ID permit
records have a name in the combined lookup. Three supplemental
mappings were confirmed using the neighbourhood reference dataset;
6212 → ELLERSLIE AREA was inferred from permit record 065305222-040.

## Permit-Neighborhood Relationships
Created a separate relationship table with one row per unique
permit–neighbourhood pair.

Checked permit 065305222-040: its original IDs, 6212 and 6214,
appear as two links with the same row_id.

Full relationship validation passed:
- No duplicate permit–neighbourhood pairs.
- No missing values in either relationship column.
- Every linked permit exists in the cleaned dataset.
- Every permit’s neighbourhood links match its original IDs.

The six permits without neighbourhood IDs remain in the cleaned
dataset and have no neighbourhood relationship rows.

## Neighbourhood Lookup Table

Built a reusable neighbourhood table containing 402 rows,
combining single-ID mappings with four supplemental mappings.

Validation passed:
- No duplicate neighbourhood IDs.
- No missing IDs or names.
- Every neighbourhood ID in the permit–neighbourhood relationship
  table exists in the lookup.

### Reference Source

- Dataset: City of Edmonton — Neighbourhoods
- File: City_of_Edmonton_-_Neighbourhoods_20261017.csv
- URL: https://data.edmonton.ca/City-Administration/City-of-Edmonton-Neighbourhoods/65fr-66s6
- Date checked: [2026-10-17]

### Remaining Work

- Create PostgreSQL tables with primary and foreign keys.
- Load the validated permit, neighbourhood, and relationship tables.
- Validate the loaded database records and relationships.