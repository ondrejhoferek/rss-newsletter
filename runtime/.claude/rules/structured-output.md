# Structured Output Rules

- Respond only with JSON. No prose, no markdown, no code fences.
- Match the exact field names and types from the schema.
- All required fields must be present.
- Numeric scores must be integers between 0 and 10 inclusive.
- String fields must not be empty unless explicitly optional.
- Array fields must contain the expected number of items.
- IDs must match the article_id values provided in the input.
