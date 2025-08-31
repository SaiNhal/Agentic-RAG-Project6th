def plan_query(user_query):
    """
    Simple planner that extracts invoice_id and decides action from user query.
    """
    # Example: Try to extract invoice ID like 'INV-123' from the query
    import re
    match = re.search(r'(INV-\d+)', user_query)
    invoice_id = match.group(1) if match else None

    # You can add rules to decide action based on keywords
    if 'flagged' in user_query.lower():
        action = "explain_flag"
    else:
        action = "unknown"

    return {
        "action": action,
        "invoice_id": invoice_id
    }

# Test code
if __name__ == "__main__":
    q = "Why was invoice INV-123 flagged?"
    print(plan_query(q))
