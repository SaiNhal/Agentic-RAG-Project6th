"""
Simple short-term memory for storing current query context
"""

class ShortTermMemory:
    def __init__(self):
        self.context = {}

    def store(self, key, value):
        self.context[key] = value

    def retrieve(self, key):
        return self.context.get(key, None)

    def clear(self):
        self.context = {}

# Example usage/test
if __name__ == "__main__":
    memory = ShortTermMemory()
    memory.store("last_invoice", "INV-123")
    print("Stored invoice:", memory.retrieve("last_invoice"))
    memory.clear()
    print("After clearing:", memory.retrieve("last_invoice"))
