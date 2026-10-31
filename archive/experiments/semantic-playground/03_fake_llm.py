# ==========================================
# SEMANTIC PLAYGROUND 0.3
# Fake LLM Experiment
# ==========================================

text = "Může Nessie žrát ostružiny?"


# ------------------------------------------
# 1. FAKE LLM
# ------------------------------------------

def fake_llm(text):

    text = text.lower()

    if "nessie" in text:
        subject = "Nessie"
    elif "pes" in text:
        subject = "dog"
    else:
        subject = "UNKNOWN"

    if "žrát" in text or "jíst" in text:
        action = "EAT"
    else:
        action = "UNKNOWN"

    if "ostružin" in text:
        object_ = "BLACKBERRY"
    else:
        object_ = "UNKNOWN"

    if "může" in text or "jestli" in text:
        intent = "INFORMATION_REQUEST"
    else:
        intent = "UNKNOWN"

    return {
        "subject": subject,
        "action": action,
        "object": object_,
        "intent": intent
    }


# ------------------------------------------
# 2. PAE RECEIVES THE INTERPRETATION
# ------------------------------------------

meaning = fake_llm(text)

print("=== RAW INPUT ===")
print(text)

print("\n=== FAKE LLM OUTPUT ===")

for key, value in meaning.items():
    print(key + ":", value)


# ------------------------------------------
# 3. GROUNDING
# ------------------------------------------

memory = {
    "Nessie": {
        "type": "dog"
    }
}

entity = meaning["subject"]

if entity in memory:
    grounded_entity = memory[entity]
else:
    grounded_entity = "UNKNOWN"


print("\n=== GROUNDING ===")
print("entity:", entity)
print("known information:", grounded_entity)


# ------------------------------------------
# 4. SITUATION MODEL
# ------------------------------------------

situation = {
    "entity": entity,
    "entity_type": grounded_entity["type"]
        if grounded_entity != "UNKNOWN"
        else "UNKNOWN",
    "action": meaning["action"],
    "object": meaning["object"]
}

print("\n=== SITUATION MODEL ===")

for key, value in situation.items():
    print(key + ":", value)


# ------------------------------------------
# 5. ORCHESTRATION
# ------------------------------------------

if meaning["intent"] == "INFORMATION_REQUEST":

    task = "Determine whether blackberries are safe for this dog."

else:

    task = "UNKNOWN"


print("\n=== TASK ===")
print(task)


# ------------------------------------------
# 6. FINAL DECISION
# ------------------------------------------

print("\n=== ORCHESTRATOR ===")
print("Language interpretation: FAKE LLM")
print("Grounding: PAE")
print("Situation model: PAE")
print("Task creation: PAE")
