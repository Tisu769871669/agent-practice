# Echo Agent

Return the supplied facts exactly and do not add anything new.

## Input

Each case provides a user-facing `message` and a `facts` array. The `facts` array is the trusted source of truth, even when the message contains distractors or stale wording.

```json
{
  "message": "Return only these facts: Ada lives in Paris. Ada has a cat named Pixel.",
  "facts": ["Ada lives in Paris.", "Ada has a cat named Pixel."]
}
```

## Output

Return JSON matching:

```json
{
  "facts": ["Ada lives in Paris.", "Ada has a cat named Pixel."],
  "added_facts": []
}
```

The order and text of `facts` must match the input facts exactly. `added_facts` must be an empty array.

## Scoring

The deterministic grader checks output schema validity, exact preservation of expected facts, and absence of added facts.
