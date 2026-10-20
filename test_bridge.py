from llm_bridge import format_data_for_llm, ask_ollama

print("--- 1. Testing Data Formatter ---")
# จำลองข้อมูลฟันผุ
fake_teeth = {'18': True, '24': True}
fake_probs = {'18': 0.95, '24': 0.60}

text = format_data_for_llm(fake_teeth, fake_probs)
print(f"Result:\n{text}\n")

print("--- 2. Testing Ollama Connection ---")
print("Sending to AI... (Please wait)")
try:
    report = ask_ollama(text)
    print("\n--- AI REPORT ---")
    print(report)
    print("-----------------")
    print("Test Passed! ✅")
except Exception as e:
    print(f"Test Failed ❌: {e}")