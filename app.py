import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from planner import plan_query
from retriever import Retriever
from verifier import verify_invoice_po
from llm_synthesizer import generate_explanation
from memory import ShortTermMemory
from audit_logger import log_event

from flask import Flask, request, render_template_string

app = Flask(__name__)
memory = ShortTermMemory()
retriever = Retriever()

# Global conversation history list
conversation_history = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>Agentic RAG Invoice Assistant</title>
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      margin: 40px auto;
      max-width: 800px;
      background: #f0f4f8;
      color: #333;
      padding: 20px;
      border-radius: 10px;
      box-shadow: 0 6px 18px rgba(0,0,0,0.1);
    }
    h2 {
      color: #2c3e50;
      text-align: center;
      margin-bottom: 30px;
      font-weight: 700;
    }
    form {
      margin-bottom: 30px;
    }
    textarea {
      width: 100%;
      font-size: 1.1rem;
      padding: 15px;
      border-radius: 8px;
      border: 2px solid #3498db;
      resize: vertical;
      min-height: 100px;
      transition: border-color 0.3s ease;
    }
    textarea:focus {
      border-color: #2980b9;
      outline: none;
    }
    input[type=submit] {
      background: #3498db;
      color: white;
      font-size: 1.1rem;
      padding: 12px 30px;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: background 0.3s ease;
      font-weight: bold;
    }
    input[type=submit]:hover {
      background: #2980b9;
    }
    .response {
      background: white;
      padding: 25px;
      border-radius: 10px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      white-space: pre-wrap;
      font-size: 1rem;
      line-height: 1.5;
      border-left: 6px solid #3498db;
    }
    .history {
      margin-top: 40px;
    }
    .history h3 {
      border-bottom: 2px solid #3498db;
      padding-bottom: 5px;
      color: #2c3e50;
      margin-bottom: 20px;
      font-weight: 600;
    }
    .history-item {
      background: #fff;
      box-shadow: 0 4px 12px rgba(0,0,0,0.05);
      padding: 15px 20px;
      border-radius: 8px;
      margin-bottom: 20px;
      transition: background 0.2s ease;
    }
    .history-item:hover {
      background: #eaf4fc;
    }
    .user {
      font-weight: 700;
      color: #2980b9;
      display: inline-block;
      margin-bottom: 5px;
    }
    .bot {
      color: #555;
      white-space: pre-wrap;
      display: block;
      margin-left: 10px;
      margin-top: 5px;
    }

    /* Spinner styles */
    .spinner {
      display: none;
      margin: 20px auto;
      border: 6px solid #f3f3f3;
      border-top: 6px solid #3498db;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  </style>
</head>
<body>
  <h2>Agentic RAG Invoice Assistant</h2>
  <form method="post">
    <textarea name="query" rows="4" placeholder="Enter your query here...">{{ query }}</textarea><br><br>
    <input type="submit" value="Ask">
  </form>

  <!-- Loading Spinner -->
  <div id="loading-spinner" class="spinner"></div>
  
  {% if response %}
    <div class="response"><strong>Response:</strong><br>{{ response }}</div>
  {% endif %}
  
  {% if history %}
    <div class="history">
      <h3>Conversation History</h3>
      {% for item in history %}
        <div class="history-item">
          <span class="user">You:</span> <span class="bot">{{ item.query }}</span><br>
          <span class="user">Assistant:</span> <span class="bot">{{ item.response }}</span>
        </div>
      {% endfor %}
    </div>
  {% endif %}

  <script>
    const form = document.querySelector('form');
    const spinner = document.getElementById('loading-spinner');

    form.addEventListener('submit', () => {
      spinner.style.display = 'block';
    });
  </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    response = None
    query = ""
    if request.method == "POST":
        query = request.form.get("query", "").strip()
        print("Received query:", query)  # Debug

        if not query:
            response = "Please enter a valid query."
            print("No query received.")  # Debug
        else:
            try:
                log_event("QUERY", f"User asked: {query}")

                if query.lower() in {"approve it", "approve"}:
                    last_invoice = memory.retrieve("last_invoice")
                    print("Retrieved last invoice from memory:", last_invoice)  # Debug

                    if not last_invoice:
                        response = "No previous invoice found to approve."
                        print("No last invoice in memory.")  # Debug
                    else:
                        response = f"Approving the last queried invoice: {last_invoice}"
                        log_event("ACTION", f"Invoice {last_invoice} approved by user command")
                        print("Approval processed.")  # Debug

                else:
                    plan = plan_query(query)
                    print("Planner output:", plan)  # Debug

                    invoice_id = plan.get("invoice_id")
                    print("Extracted invoice_id:", invoice_id)  # Debug

                    if not invoice_id:
                        response = "Could not determine invoice from query."
                        print("No invoice_id found in plan.")  # Debug
                    else:
                        invoice = retriever.get_invoice(invoice_id)
                        print("Retrieved invoice:", invoice)  # Debug

                        if not invoice:
                            response = f"Invoice {invoice_id} not found."
                            print(f"Invoice {invoice_id} missing in retriever.")  # Debug
                        else:
                            po = retriever.get_po(invoice.get("po_id")) if invoice.get("po_id") else None
                            print("Retrieved PO:", po)  # Debug

                            receipts = retriever.get_receipts_by_invoice(invoice_id)
                            print("Retrieved receipts:", receipts)  # Debug

                            verification = verify_invoice_po(invoice, po) if po else {"match_score": 0, "confidence": "Low"}
                            print("Verification result:", verification)  # Debug

                            explanation = generate_explanation(invoice, po, receipts, verification, query)
                            print("Generated explanation:", explanation)  # Debug

                            log_event("EXPLANATION", "Generated explanation provided to user")

                            memory.store("last_invoice", invoice_id)
                            response = explanation

                # Store interaction in conversation history
                if response and query:
                    conversation_history.append({"query": query, "response": response})
                    print("Added to conversation history.")  # Debug

            except Exception as e:
                error_msg = f"Sorry, an error occurred: {str(e)}"
                log_event("ERROR", error_msg)
                response = error_msg
                print("Exception caught:", str(e))  # Debug

    return render_template_string(HTML_TEMPLATE, query=query, response=response, history=conversation_history)

if __name__ == "__main__":
    app.run(debug=True)
