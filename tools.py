def calculator_tool(query):
    try:
        expression = query.lower().replace("calculate", "").strip()
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {e}"

def dictionary_tool(query):
    word = query.lower().replace("define", "").strip()
    return f"Definition of '{word}': [stubbed response – use a real API if needed]"
