import os
import json
import re
import time  # <-- Ensure this is here
import requests
import numpy as np
from flask import Flask, request, jsonify

app = Flask(__name__)

# ─── GOOGLE AI STUDIO PLATFORM PLUGIN ───
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
GOOGLE_LLM_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={GOOGLE_API_KEY}"

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"

def query_hosted_llm(prompt, max_tokens=128):
    """Routes evaluation prompts to Gemini Flash Lite using standard structured content envelopes."""
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.0,
            "maxOutputTokens": max_tokens
        }
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(GOOGLE_LLM_URL, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            res_json = response.json()
            return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            print(f"⚠️ Google API Server Error ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"⚠️ Cloud Connection Error: {str(e)}")
    return ""

def get_local_embedding(text):
    """Fetches text vector matrix locally via nomic."""
    payload = {"model": "nomic-embed-text:latest", "prompt": text}
    try:
        response = requests.post(OLLAMA_EMBED_URL, json=payload, timeout=60)
        if response.status_code == 200:
            return response.json().get("embedding", [])
    except Exception as e:
        print(f"⚠️ Embedding Error: {str(e)}")
    return []

def cosine_similarity(v1, v2):
    """Computes exact mathematical cosine similarity vector distance."""
    if not v1 or not v2:
        return 0.0
    arr1, arr2 = np.array(v1), np.array(v2)
    dot_prod = np.dot(arr1, arr2)
    norm1 = np.linalg.norm(arr1)
    norm2 = np.linalg.norm(arr2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot_prod / (norm1 * norm2))

def split_into_sentences(text):
    """Robust structural tokenizer parsing lines and document boundaries."""
    if not text:
        return []
    text = str(text).strip()
    text = text.replace('\\\\n', '|||').replace('\\n', '|||')
    text = text.replace('\n', '|||').replace('\r', '|||').replace('\t', '|||')
    text = re.sub(r'(\[SOP Source \d+[^\]]*\])', r'|||\1|||', text)
    text = re.sub(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s+', '|||', text)
    
    raw_chunks = text.split('|||')
    cleaned_sentences = []
    for s in raw_chunks:
        # Strip out formatting noise, colons, bullets, and structural brackets
        c = s.strip("- *•123. \t\n()").strip(":").strip()
        # Drop short fragments or metadata headers to keep only meaningful claims
        if c and len(c) > 20 and not c.startswith("File:") and not c.startswith("Standard_Operating_Procedure"):
            cleaned_sentences.append(c)
    return cleaned_sentences

def calculate_faithfulness(context, answer):
    """Evaluates grounding sequentially using semantic-matching guidelines."""
    statements = split_into_sentences(answer)
    clean_context = context.replace('|||', '\n')
    
    total_statements = len(statements)
    if total_statements == 0:
        return 1.0
        
    print(f"\n   🔍 [DEBUG FAITHFULNESS] Evaluating {total_statements} Clean Operational Claims:")
    print("\n   📋 [LIVE LOG] Faithfulness Audit Verdicts:")
    verified_statements = 0
    
    for idx, s in enumerate(statements):
        prompt = f"""[Instruction] Act as an expert compliance auditor. Verify if the core operational action described in the Plan Claim is conceptually supported by the corporate SOP reference rules.

[Corporate SOP Context Reference]:
{clean_context}

[Plan Claim to Verify]:
{s}

[Rules]:
1. If the reference rules authorize, outline, or support the core logic of this action, reply with 'YES'.
2. Treat alternative terminology as a match if the operational intent is the same (e.g., if the claim references 'SOP Section [3]' but the nearby context logic matches 'Step 2: Assess Shipping Commitment' or 'SOP Source 3', mark it as YES).
3. Reply with 'NO' only if the claim directly contradicts the corporate guidelines or introduces completely unmentioned procedures.
4. Reply with 'YES' or 'NO' only. Do not add introductory commentary.

Answer:"""
        
        verdict = query_hosted_llm(prompt, max_tokens=10).upper()
        
        is_verified = False
        if "YES" in verdict:
            verified_statements += 1
            is_verified = True
            
        print(f"      🔹 Claim #{idx+1} Grounded? -> { '🟢 YES' if is_verified else '❌ NO' } (Model Output: '{verdict}')")
        
        # ─── ADDED: PACE REQUESTS TO PROTECT FREE TIER RPM ───
        time.sleep(4.5)
    
    score = round(verified_statements / total_statements, 2)
    print(f"   📐 Math Fraction: {verified_statements}/{total_statements} = {score}")
    return score

def calculate_answer_relevance(true_question, answer):
    """Implements back-generation question mapping with verbose vector metric outputs."""
    print(f"\n   🔍 [DEBUG RELEVANCE] Original System Question: '{true_question}'")
    print("   📊 Generating 3 candidate target queries via cloud...")
    
    prompt = f"""[Instruction] Read the following operational response plan and output exactly 3 distinct questions that this text directly answers.

[Text]:
{answer}

[Constraint]:
Return ONLY the questions as a numbered or bulleted list. Do not append any introductory prefixes or summary text.

Questions:"""
    raw_response = query_hosted_llm(prompt, max_tokens=256)
    
    raw_lines = raw_response.split("\n")
    gen_questions = []
    for line in raw_lines:
        cleaned_line = line.strip("- *•123. ").strip()
        if cleaned_line and not any(x in cleaned_line.lower() for x in ["task:", "constraint:", "input:", "here are"]):
            gen_questions.append(cleaned_line)
    gen_questions = gen_questions[:3]
    
    print("   📋 [LIVE LOG] Back-Generated Target Questions:")
    for idx, q in enumerate(gen_questions):
        print(f"      ❓ Question {idx+1}: {q}")
        
    if not gen_questions or len(gen_questions) < 3:
        return 0.5
        
    true_vector = get_local_embedding(true_question)
    similarities = []
    
    print("\n   📐 Computing Vector Cosine Metrics:")
    for idx, q in enumerate(gen_questions):
        sim = cosine_similarity(true_vector, get_local_embedding(q))
        similarities.append(sim)
        print(f"      🧮 Sim(Q_True, Q_{idx+1}) = {round(sim, 4)}")
    
    avg_relevance = round(float(np.mean(similarities)), 2)
    print(f"   📐 Final Relevance Average Score: {avg_relevance}")
    return avg_relevance

def calculate_context_relevance(true_question, context, answer):
    """
    Calculates Rank-Weighted Context Precision using Gemini Flash Lite.
    Loops through individual context chunks to evaluate rank placement quality.
    """
    if not context or len(str(context).strip()) == 0:
        return 0.0

    print(f"\n   🔍 [DEBUG CONTEXT PRECISION] Running rank-weighted chunk audit...")
    
    # ─── STEP 1: PARSE CONTINUOUS TEXT INTO DISTINCT CHUNKS ───
    # We look ahead for [SOP Source X] markers to divide the continuous string
    chunks = re.split(r'(?=\[SOP Source \d+)', str(context))
    retrieved_chunks = [chunk.replace('|||', '\n').strip() for chunk in chunks if chunk.strip()]
    
    total_chunks = len(retrieved_chunks)
    if total_chunks == 0:
        return 0.0
        
    print(f"      📦 Detected {total_chunks} independent SOP context chunks for evaluation.")
    
    # ─── STEP 2: BINARY AUDIT LOOP FOR EACH CHUNK ───
    verdicts = []
    for idx, chunk in enumerate(retrieved_chunks):
        prompt = f"""[Instruction] Act as an expert data retrieval auditor. Determine if the given SOP Context Chunk contains necessary rules, parameter bounds, or operational instructions to support the generated mitigation response.

[Master System Query]:
{true_question}

[Generated Response Plan]:
{answer}

[SOP Context Chunk to Evaluate]:
{chunk}

[Constraint]:
If this specific chunk provides necessary context or structural rules that help justify or execute the generated response plan, reply with '1'. Otherwise, reply with '0'. Output ONLY the single digit '1' or '0'. Do not include explanations or formatting.

Verdict:"""
        
        raw_output = query_hosted_llm(prompt, max_tokens=5).strip()
        
        # Default to 0 if parsing fails
        verdict = 1 if "1" in raw_output else 0
        verdicts.append(verdict)
        print(f"      🔹 Chunk #{idx+1} Verdict -> { '🟢 1 (Relevant)' if verdict == 1 else '❌ 0 (Irrelevant)' }")
        
        # Pace API calls to handle rate limit restrictions
        time.sleep(2.0)

    # ─── STEP 3: APPLY NATIVE RAGAS RANK-WEIGHTED MATH ───
    # Context Precision formula calculates cumulative precision values at each relevant rank position
    numerator = 0.0
    true_positives = 0
    
    for k, verdict in enumerate(verdicts):
        rank = k + 1
        if verdict == 1:
            true_positives += 1
            # Precision at rank k = (cumulative true positives) / k
            precision_at_k = true_positives / rank
            numerator += precision_at_k
            
    total_relevant_items = sum(verdicts)
    
    if total_relevant_items == 0:
        score = 0.0
    else:
        score = round(float(numerator / total_relevant_items), 2)
        
    print(f"   🧮 Rank-Weighted Precision Calculation Result: {score}")
    return score

@app.route('/trigger-ragas', methods=['POST'])

def trigger():
    print("\n================================================================================")
    print("🚀 SIGNAL RECEIVED FROM N8N! STARTING CLOUD-ACCELERATED RAGAS MATRIX...")
    print("================================================================================")
    try:
        payload = request.get_json()
        rag_data = payload.get('rag_triplet', {})
        
        question = str(rag_data.get('question', 'Anomaly detected'))
        answer = str(rag_data.get('answer', 'No plan compiled'))
        
        context_raw = rag_data.get('context', 'No context chunks logged')
        if isinstance(context_raw, list):
            context = "|||".join([str(chunk) for chunk in context_raw])
        else:
            context = str(context_raw)

        faithfulness_score = calculate_faithfulness(context, answer)
        relevance_score = calculate_answer_relevance(question, answer)
        context_relevance_score = calculate_context_relevance(question, context, answer)
        #context_relevance_score = calculate_context_relevance(question, context)

        evaluation_output = {
            "Execution_Time_Sec": float(payload.get('execution_time_sec', 0)),
            "RAGAS_Status": "EVALUATED",
            "Faithfulness_Score": faithfulness_score,
            "Answer_Relevance_Score": relevance_score,
            "Context_Relevance_Score": context_relevance_score
        }
        
        print("\n================================================================================")
        print(f"✅ RUN COMPLETE! METRICS RETURNED: [F: {faithfulness_score} | R: {relevance_score} | CR: {context_relevance_score}]")
        print("================================================================================\n")
        
        final_response = {**payload, **evaluation_output}
        final_response.pop('rag_triplet', None)
        return jsonify(final_response), 200

    except Exception as e:
        print(f"❌ Pipeline Error: {str(e)}")
        return jsonify({"RAGAS_Status": "ERROR", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=False)