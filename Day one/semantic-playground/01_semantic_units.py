# SEMANTIC PLAYGROUND 0.1
# Manual semantic representation

text = "Zjisti mi jestli pes může jíst ostružiny."

meaning = {
    "subject": "dog",
    "action": "eat",
    "object": "blackberry",
    "intent": "information_request"
}

print("=== RAW INPUT ===")
print(text)

print("\n=== SEMANTIC UNITS ===")
for key, value in meaning.items():
    print(key + ":", value)
