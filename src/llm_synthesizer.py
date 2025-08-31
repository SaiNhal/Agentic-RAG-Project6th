import os
import openai

# Set your OpenAI API key here or via environment variable for security
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_explanation(invoice, po, receipts, verification_result, query):
    prompt = f"""
You are an AI assistant that explains why an invoice may have been flagged.

User Query: {query}

Invoice details: {invoice}
Purchase Order details: {po}
Goods Receipts: {receipts}
Verification Result: Match Score = {verification_result['match_score']}%, Confidence = {verification_result['confidence']}

Please provide a clear and concise explanation addressing the user's question.
"""
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# Example test run
if __name__ == "__main__":
    invoice_example = {
        "invoice_id": "INV-123",
        "amount": 5800,
        "po_id": "PO-987",
        "flagged": True,
        "details": "Invoice amount exceeds PO amount"
    }
    po_example = {
        "po_id": "PO-987",
        "amount": 5000,
        "vendor": "Vendor A"
    }
    receipts_example = [
        {"receipt_id": "GR-111", "invoice_id": "INV-123", "po_id": "PO-987", "received_amount": 4900}
    ]
    verification_result_example = {"match_score": 84.0, "confidence": "Medium"}
    query_example = "Why was invoice INV-123 flagged?"

    explanation = generate_explanation(
        invoice_example,
        po_example,
        receipts_example,
        verification_result_example,
        query_example
    )
    print("Generated explanation:\n", explanation)
