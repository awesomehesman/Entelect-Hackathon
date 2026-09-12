# Submission format

The official problem statement defines the submission as a JSON file containing an array of tick entries. Each tick entry includes a tick number and a list of planting actions. The example uses:

```json
{
  "actions": [
    {"tick": 1, "plants": [{"plant_index": 6, "row": 0, "col": 0}]}
  ]
}
```

The schema section then shows:

```json
{ "index": 1, "row": 0, "col": 0 }
```

## Priority discrepancy

This is a HIGH PRIORITY validation issue because the same field is shown as both "plant_index" and "index" in different parts of the challenge specification.

The repository contains no later authoritative resolver for this discrepancy. The official statement is the highest authority, but the data and schema are internally inconsistent. This issue is therefore unresolved and must not be silently normalized.

## Evidence in the repository

- Example action object in the problem statement uses "plant_index"
- Schema definition later uses "index"
- Challenge JSON plant entries use a top-level "index" field for species identity
- The plant catalogue defines each species with a numeric index, but the submission example and schema text disagree about whether the action field value is named "plant_index" or "index"

## Required handling

For implementation and validation, the simulator and submission generator must explicitly support both names until the official mechanic or submission checker is confirmed. Until then, the discrepancy remains unresolved and must be treated as a blocking validation item.
