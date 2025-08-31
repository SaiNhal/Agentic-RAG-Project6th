from planner import plan_query
from retriever import Retriever
from verifier import verify_invoice_po
from llm_synthesizer import generate_explanation
from memory import ShortTermMemory
from audit_logger import log_event

def main():
    memory = ShortTermMemory()
    retriever = Retriever()

    print("Agentic RAG Invoice Assistant\nType 'exit' to quit.")
    while True:
        user_query = input("\nEnter your query: ")
        if user_query.lower() == 'exit':
            print("Goodbye!")
            break
        
        log_event("QUERY", f"User asked: {user_query}")

        # Check if user query is a follow-up command like "approve it"
        if user_query.lower() in {"approve it", "approve"}:
            last_invoice = memory.retrieve("last_invoice")
            if not last_invoice:
                print("No previous invoice found to approve.")
                continue
            print(f"Approving the last queried invoice: {last_invoice}")
            log_event("ACTION", f"Invoice {last_invoice} approved by user command")
            continue

        # Otherwise, treat as a new query
        plan = plan_query(user_query)
        log_event("DECISION", f"Planner decided action: {plan['action']}")

        invoice_id = plan.get("invoice_id")
        if not invoice_id:
            print("Could not determine invoice from query.")
            continue

        invoice = retriever.get_invoice(invoice_id)
        if not invoice:
            print(f"Invoice {invoice_id} not found.")
            continue
        po = retriever.get_po(invoice["po_id"]) if invoice.get("po_id") else None
        receipts = retriever.get_receipts_by_invoice(invoice_id)
        log_event("DATA", f"Retrieved invoice {invoice_id} and PO {invoice.get('po_id')}")

        verification_result = verify_invoice_po(invoice, po) if po else {"match_score": 0, "confidence": "Low"}
        log_event("VERIFICATION", f"Match score: {verification_result['match_score']}, Confidence: {verification_result['confidence']}")

        explanation = generate_explanation(invoice, po, receipts, verification_result, user_query)
        log_event("EXPLANATION", "Generated explanation provided to user")

        memory.store("last_invoice", invoice_id)

        print("\nExplanation:")
        print(explanation)

if __name__ == "__main__":
    main()
