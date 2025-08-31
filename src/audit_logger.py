import logging

logging.basicConfig(
    filename='audit.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_event(event_type, message):
    """
    Log an event with type and descriptive message
    """
    logging.info(f"[{event_type}] {message}")

# Example test
if __name__ == "__main__":
    log_event("QUERY", "User asked: Why was invoice INV-123 flagged?")
    log_event("DECISION", "Planner decided action: explain_flag")
    log_event("DATA", "Retrieved invoice INV-123 and PO PO-987")
    log_event("VERIFICATION", "Match score: 84.0, Confidence: Medium")
    log_event("EXPLANATION", "Generated explanation provided to user")
    print("Audit logs written to audit.log")
