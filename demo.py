from entity_detection import EntityDetector, EntityMatcher

# 1. Initialize detector and matcher
print("Initializing Entity Detector (spaCy)...")
detector = EntityDetector("en_core_web_sm")
matcher = EntityMatcher(similarity_threshold=80.0, type_matching=True)

# 2. Sample texts representing a corporate history with hallucinations
source_text = "Acme Corp was founded in 1998 by John Doe and Jane Smith in Chicago, Illinois. In June 2021, Acme Corp was acquired by Globex International for $450 million."
response_text = "Globex International acquired Acme Corp in July 2022 for a total of $550 million. Acme was originally set up in Boston back in 1995 by Jane Smith and John Doe."

print("\n=== INPUT TEXTS ===")
print(f"Source Context:\n  \"{source_text}\"")
print(f"\nGenerated Response:\n  \"{response_text}\"")

# 3. Extract named entities
source_ents = detector.extract_entities(source_text)
response_ents = detector.extract_entities(response_text)

print("\n=== EXTRACTED ENTITIES ===")
print("Entities in Source Context:")
for ent in source_ents:
    print(f"  - [{ent['label']}] \"{ent['text']}\"")

print("\nEntities in Generated Response:")
for ent in response_ents:
    print(f"  - [{ent['label']}] \"{ent['text']}\"")

# 4. Compare entities to calculate consistency
print("\n=== COMPARING ENTITIES & SCORING ===")
results = matcher.compare_entities(source_ents, response_ents)

print(f"\nFactual Consistency Score: {results['factual_consistency_score']}%")

print("\nVerified Entities:")
if results['verified']:
    for item in results['verified']:
        print(f"  [OK] \"{item['entity']['text']}\" ({item['entity']['label']}) -> Matches Source \"{item['best_match']['text']}\" (Fuzzy Score: {item['similarity_score']}%)")
else:
    print("  None")

print("\nHallucinated Entities:")
if results['hallucinated']:
    for item in results['hallucinated']:
        best_match = f"Close match \"{item['best_match']['text']}\" (Score: {item['similarity_score']}%) below threshold" if item['best_match'] else "No match found"
        print(f"  [FAIL] \"{item['entity']['text']}\" ({item['entity']['label']}) -> {best_match}")
else:
    print("  None")
