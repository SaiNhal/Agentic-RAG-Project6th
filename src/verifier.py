"""
Verifier module to check invoice and PO match and generate confidence score
"""

def calculate_match_score(invoice_amount, po_amount):
    """
    Simple percentage match score based on difference between amounts
    """
    if po_amount == 0:
        return 0.0
    diff = abs(invoice_amount - po_amount)
    score = max(0, 100 - (diff / po_amount) * 100)  # percent match score
    return round(score, 2)

def get_confidence_level(score):
    """
    Return confidence label based on match score
    """
    if score >= 95:
        return "High"
    elif score >= 80:
        return "Medium"
    else:
        return "Low"

def verify_invoice_po(invoice, po):
    """
    Given invoice and po dicts, verify match and produce score + confidence
    """
    invoice_amount = invoice.get("amount", 0)
    po_amount = po.get("amount", 0)
    score = calculate_match_score(invoice_amount, po_amount)
    confidence = get_confidence_level(score)
    return {
        "match_score": score,
        "confidence": confidence
    }

# Example quick test
if __name__ == "__main__":
    invoice_example = {"amount": 5800}
    po_example = {"amount": 5000}
    result = verify_invoice_po(invoice_example, po_example)
    print("Verification result:", result)
