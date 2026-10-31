# SEMANTIC PLAYGROUND 0.2
# Simple rule-based extraction

text = "Zjisti mi jestli pes může jíst ostružiny."
lower = text.lower()

if "pes" in lower:
    subject = "dog"
else:
    subject = "UNKNOWN"

if "jíst" in lower or "žrát" in lower:
    action = "EAT"
else:
    action = "UNKNOWN"

if "ostruž" in lower:
    object_ = "BLACKBERRY"
else:
    object_ = "UNKNOWN"

print("=== RAW INPUT ===")
print(text)

print("\n=== RULE-BASED OUTPUT ===")
print("subject:", subject)
print("action:", action)
print("object:", object_)
