import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

def load_json(filename):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'r') as f:
        return json.load(f)

class Retriever:
    def __init__(self):
        self.invoices = load_json("invoices.json")
        self.pos = load_json("pos.json")
        self.receipts = load_json("receipts.json")
    
    def get_invoice(self, invoice_id):
        for inv in self.invoices:
            if inv["invoice_id"] == invoice_id:
                return inv
        return None

    def get_po(self, po_id):
        for po in self.pos:
            if po["po_id"] == po_id:
                return po
        return None

    def get_receipts_by_invoice(self, invoice_id):
        return [r for r in self.receipts if r["invoice_id"] == invoice_id]

# Example quick test
if __name__ == "__main__":
    retriever = Retriever()
    inv = retriever.get_invoice("INV-123")
    print("Invoice INV-123:", inv)
    po = retriever.get_po(inv["po_id"])
    print("PO for INV-123:", po)
    receipts = retriever.get_receipts_by_invoice("INV-123")
    print("Receipts for INV-123:", receipts)
