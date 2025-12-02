from flask import Flask, request, jsonify
from rag_core import answer

app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask():
    """
    Attendu JSON: { "question": "Votre question ici", "top_k": 5 }
    """
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "Veuillez fournir la clé 'question'"}), 400

    question = data["question"]
    k = data.get("top_k", 5)

    try:
        resp_text, rows = answer(question, k=k)
        # Préparer le contexte récupéré
        context = [
            {"source": src, "modality": mod, "chunk": chunk, "score": float(score)}
            for src, chunk, mod, score in rows
        ]
        return jsonify({
            "answer": resp_text,
            "context": context
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
