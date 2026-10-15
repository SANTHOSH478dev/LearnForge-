import json
import re
import random
import time
from typing import List, Dict, Any, Optional, Set
from app.config import settings

def call_gemini_api(prompt: str) -> Optional[str]:
    """Call Google Gemini API if API key is present."""
    if not settings.GEMINI_API_KEY or settings.USE_MOCK_AI:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(
            settings.GEMINI_MODEL,
            generation_config={"temperature": 0.75, "top_p": 0.9}
        )
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text
    except Exception as e:
        print(f"Gemini API call failed: {e}. Falling back to Smart Grounded Engine.")
    return None

def extract_meaningful_sentences(text: str) -> List[str]:
    """Extract clean, meaningful declarative sentences from text."""
    raw = re.split(r"(?<=[.!?])\s+", text)
    clean = []
    for s in raw:
        s_clean = s.strip()
        # Filter out short lines, headers, or bullet symbols
        if len(s_clean) >= 30 and len(s_clean.split()) >= 6:
            clean.append(s_clean)
    return clean

def generate_dynamic_distractor(correct_sentence: str, other_sentences: List[str], topic: str) -> List[str]:
    """
    Generate plausible, domain-grounded distractors using
    other document sentences, semantic inversions, and contrasting statements.
    """
    distractors: List[str] = []

    # 1. Semantic negation / inversion of the correct statement
    negated = correct_sentence
    negation_pairs = [
        (r"\balways\b", "never"),
        (r"\bguarantees\b", "does not guarantee"),
        (r"\brequires\b", "bypasses the requirement for"),
        (r"\bincreases\b", "reduces"),
        (r"\bdecreases\b", "amplifies"),
        (r"\bprevents\b", "allows unrestricted"),
        (r"\bis identical\b", "can differ arbitrarily"),
        (r"\bstrict majority\b", "single minority node"),
        (r"\bmajority\b", "minority"),
        (r"\ball\b", "only the initial"),
        (r"\bpassive\b", "active coordinating"),
        (r"\bactive\b", "strictly passive"),
        (r"\bcan be\b", "can never be"),
        (r"\bO\(1\)\b", "O(N) linear time"),
        (r"\bO\(log n\)\b", "O(N^2) quadratic time"),
    ]

    for pattern, replacement in negation_pairs:
        if re.search(pattern, negated, flags=re.IGNORECASE):
            negated = re.sub(pattern, replacement, negated, count=1, flags=re.IGNORECASE)
            break
    else:
        # Fallback inversion
        if " is " in negated:
            negated = negated.replace(" is ", " is not ", 1)
        elif " are " in negated:
            negated = negated.replace(" are ", " are not ", 1)
        elif " will " in negated:
            negated = negated.replace(" will ", " will not ", 1)
        else:
            negated = f"It negates the requirement that {correct_sentence[:60].lower()}."

    if negated != correct_sentence and len(negated) > 15:
        distractors.append(negated[:140] + ("." if not negated.endswith(".") else ""))

    # 2. Pick contrasting claims from other sentences in the document
    if other_sentences:
        sampled_others = random.sample(other_sentences, min(len(other_sentences), 4))
        for s in sampled_others:
            if s != correct_sentence and len(distractors) < 3:
                # Frame as alternative outcome
                distractors.append(f"It instead mandates that {s[:90].lower()}...")

    # 3. Fill remaining with domain-plausible distractors
    fillers = [
        f"It operates independently of {topic} without affecting state consistency.",
        f"It is only executed as a secondary recovery fallback during cluster partition.",
        f"It relies strictly on client-side caching rather than server validation.",
        f"It delegates execution priority to unverified replica nodes.",
        f"It automatically aborts all active transactions and resets the state machine."
    ]
    random.shuffle(fillers)
    for f in fillers:
        if len(distractors) < 3:
            distractors.append(f)

    return distractors[:3]

def synthesize_grounded_questions(
    chunks: List[Dict[str, Any]],
    requested_count: int = 10,
    difficulty: str = "medium",
    topic_filter: Optional[str] = None,
    question_types: Optional[List[str]] = None,
    document_id: Optional[int] = None,
    document_title: Optional[str] = None,
    existing_question_texts: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Intelligent Grounded Synthesizer:
    - Never generates duplicate questions.
    - Uses varied cognitive question archetypes (definition, operational, scenario, differentiation, negation).
    - Extracts authentic, dynamic distractors from actual document text.
    - Supports Gemini API with dynamic temperature and non-repeating prompt directives.
    """
    if not question_types:
        question_types = ["mcq"]

    if not chunks:
        chunks = [{
            "chunk_index": 0,
            "page_number": 1,
            "section_heading": "General Course Notes",
            "content": f"Foundational concepts in {document_title or 'Study Topic'}."
        }]

    # Filter chunks by topic if requested
    filtered_chunks = chunks
    if topic_filter and topic_filter.lower() not in ["all", "comprehensive", "general"]:
        matched = [
            c for c in chunks
            if topic_filter.lower() in c.get("section_heading", "").lower()
            or topic_filter.lower() in c.get("content", "").lower()
        ]
        if matched:
            filtered_chunks = matched

    existing_set: Set[str] = set()
    if existing_question_texts:
        for eq in existing_question_texts:
            existing_set.add(eq.strip().lower())

    # Try Gemini LLM first if API key is configured
    existing_avoid_prompt = ""
    if existing_set:
        sample_avoid = list(existing_set)[:5]
        existing_avoid_prompt = f"\nDO NOT repeat or duplicate any of these existing questions:\n" + "\n".join([f"- {q}" for q in sample_avoid])

    prompt = f"""
You are an expert academic examiner. Based strictly on the following study material, generate {requested_count} completely fresh, non-repeating {difficulty} assessment questions.
Mix conceptual understanding, operational mechanisms, and application scenarios.
Questions must be grounded ONLY in this text. Do not invent outside facts.{existing_avoid_prompt}

STUDY MATERIAL:
{"".join([f'--- Page {c.get("page_number", 1)} | Section: {c.get("section_heading", "")} ---\n{c.get("content", "")[:500]}\n' for c in filtered_chunks[:10]])}

Output strictly valid JSON with this exact structure:
[
  {{
    "question_text": "Clear unique question text here",
    "question_type": "mcq",
    "difficulty": "{difficulty}",
    "topic_tag": "Relevant topic",
    "marks": 1.0,
    "source_page": 1,
    "source_passage_snippet": "exact short quotation from the text supporting the answer",
    "explanation": "Clear explanation citing the underlying concept",
    "options": [
      {{"key": "A", "text": "Option text", "is_correct": true}},
      {{"key": "B", "text": "Option text", "is_correct": false}},
      {{"key": "C", "text": "Option text", "is_correct": false}},
      {{"key": "D", "text": "Option text", "is_correct": false}}
    ]
  }}
]
"""
    llm_output = call_gemini_api(prompt)
    if llm_output:
        try:
            cleaned = re.sub(r"^```json\s*", "", llm_output.strip())
            cleaned = re.sub(r"\s*```$", "", cleaned)
            parsed = json.loads(cleaned)
            if isinstance(parsed, list) and len(parsed) > 0:
                valid_gemini = []
                for q in parsed:
                    q_text_norm = q.get("question_text", "").strip().lower()
                    if q_text_norm and q_text_norm not in existing_set:
                        q["source_document_id"] = document_id
                        q["source_document_title"] = document_title
                        valid_gemini.append(q)
                        existing_set.add(q_text_norm)
                if len(valid_gemini) >= requested_count:
                    return valid_gemini[:requested_count]
                elif valid_gemini:
                    # Supplement remaining from smart synthesizer
                    remaining_needed = requested_count - len(valid_gemini)
                    supplemental = _synthesize_local(
                        filtered_chunks, remaining_needed, difficulty, question_types,
                        document_id, document_title, existing_set
                    )
                    return valid_gemini + supplemental
        except Exception as e:
            print(f"Failed to parse Gemini output: {e}. Falling back to Smart Grounded Engine.")

    # High-Variability Smart Grounded Synthesizer
    return _synthesize_local(
        filtered_chunks, requested_count, difficulty, question_types,
        document_id, document_title, existing_set
    )

def _synthesize_local(
    chunks: List[Dict[str, Any]],
    requested_count: int,
    difficulty: str,
    question_types: List[str],
    document_id: Optional[int],
    document_title: Optional[str],
    existing_set: Set[str]
) -> List[Dict[str, Any]]:
    """Synthesizes high-diversity, non-repeating grounded questions without fixed seeds."""
    generated = []

    # Gather all candidate sentences across chunks
    all_sentences_with_meta = []
    all_raw_sentences = []

    for c in chunks:
        sentences = extract_meaningful_sentences(c.get("content", ""))
        heading = c.get("section_heading", "Core Principles")
        page_num = c.get("page_number", 1)
        for s in sentences:
            all_sentences_with_meta.append({
                "sentence": s,
                "heading": heading,
                "page": page_num,
                "chunk": c
            })
            all_raw_sentences.append(s)

    if not all_sentences_with_meta:
        all_sentences_with_meta.append({
            "sentence": f"Core technical mechanisms governing {document_title or 'System Architecture'}.",
            "heading": "General Overview",
            "page": 1,
            "chunk": chunks[0] if chunks else {}
        })
        all_raw_sentences.append(all_sentences_with_meta[0]["sentence"])

    # Shuffle pool with true non-deterministic randomness
    shuffled_pool = list(all_sentences_with_meta)
    random.shuffle(shuffled_pool)

    # Question archetype templates
    question_templates = [
        ("definition", "According to Section '{heading}', what is the primary role or definition of {keyword}?"),
        ("mechanism", "Under the operational principles of '{heading}', how is {keyword} enforced?"),
        ("scenario", "In a scenario governed by '{heading}', what is the verified outcome when {keyword} is active?"),
        ("differentiation", "Which of the following statements accurately characterizes {keyword} as analyzed in '{heading}'?"),
        ("constraint", "According to the rules established in '{heading}', what invariant must be preserved regarding {keyword}?"),
        ("implication", "What direct system guarantee is established in '{heading}' concerning {keyword}?")
    ]

    attempts = 0
    max_attempts = requested_count * 8
    idx = 0

    while len(generated) < requested_count and attempts < max_attempts:
        attempts += 1
        item = shuffled_pool[idx % len(shuffled_pool)]
        idx += 1

        target_sentence = item["sentence"]
        heading = item["heading"]
        page_num = item["page"]

        # Extract keyword (exclude generic filler words)
        words = re.findall(r"\b[A-Za-z]{4,}\b", target_sentence)
        stopwords = {"this", "that", "with", "from", "have", "were", "which", "there", "their", "about", "would", "these", "other", "into", "more", "first", "could", "after", "where", "been", "through", "using", "under", "every", "state"}
        meaningful_words = [w for w in words if w.lower() not in stopwords]
        keyword = meaningful_words[0].capitalize() if meaningful_words else "System State"

        # Determine question type
        q_type = random.choice(question_types)
        archetype, template_str = random.choice(question_templates)

        diff = difficulty
        if difficulty == "mixed":
            diff = random.choice(["easy", "medium", "hard"])

        if q_type == "true_false":
            is_true = random.choice([True, False])
            if is_true:
                q_text = f"True or False: According to Section '{heading}', {target_sentence}"
                corr_key = "A"
                exp = f"True: Directly verified in Section '{heading}' (Page {page_num}): '{target_sentence}'"
            else:
                negated = target_sentence.replace(" is ", " is not ").replace(" can ", " cannot ").replace(" always ", " never ")
                if negated == target_sentence:
                    negated = f"It is never the case that {target_sentence[:80].lower()}."
                q_text = f"True or False: According to Section '{heading}', {negated}"
                corr_key = "B"
                exp = f"False: The document affirms: '{target_sentence}'"

            norm_key = q_text.strip().lower()
            if norm_key in existing_set:
                continue

            options = [
                {"key": "A", "text": "True", "is_correct": (corr_key == "A")},
                {"key": "B", "text": "False", "is_correct": (corr_key == "B")}
            ]
            explanation = exp
        else:
            # MCQ
            q_text = template_str.format(heading=heading, keyword=keyword)
            norm_key = q_text.strip().lower()

            # Prevent duplicate question text
            if norm_key in existing_set:
                # Add variation if duplicate
                q_text = f"Based on '{heading}' (Page {page_num}): {target_sentence[:75]}... What is the core principle?"
                norm_key = q_text.strip().lower()
                if norm_key in existing_set:
                    continue

            corr_text = target_sentence
            if len(corr_text) > 130:
                corr_text = corr_text[:125].rsplit(" ", 1)[0] + "..."

            # Generate dynamic distractors from document context
            distractors = generate_dynamic_distractor(target_sentence, all_raw_sentences, keyword)

            options_list = [
                {"text": corr_text, "is_correct": True},
                {"text": distractors[0], "is_correct": False},
                {"text": distractors[1], "is_correct": False},
                {"text": distractors[2], "is_correct": False}
            ]
            random.shuffle(options_list)

            options = []
            for opt_i, opt in enumerate(options_list):
                key = chr(ord('A') + opt_i)
                options.append({
                    "key": key,
                    "text": opt["text"],
                    "is_correct": opt["is_correct"]
                })

            explanation = (
                f"Grounded in Section '{heading}' on Page {page_num}: "
                f"The text specifies that '{target_sentence[:180]}'."
            )

        existing_set.add(norm_key)
        generated.append({
            "question_text": q_text,
            "question_type": q_type,
            "difficulty": diff,
            "topic_tag": heading[:40],
            "marks": 1.0 if diff == "easy" else (2.0 if diff == "medium" else 3.0),
            "source_document_id": document_id,
            "source_document_title": document_title,
            "source_page": page_num,
            "source_passage_snippet": target_sentence[:220],
            "explanation": explanation,
            "options": options
        })

    return generated

def generate_exam_blueprint(
    chunks: List[Dict[str, Any]],
    document_title: str,
    total_questions: int = 15,
    target_difficulty: str = "mixed"
) -> Dict[str, Any]:
    """Create a balanced topic coverage plan based on uploaded material."""
    headings_map: Dict[str, int] = {}
    for c in chunks:
        h = c.get("section_heading", "Core Principles")
        if not h.startswith("Page "):
            headings_map[h] = headings_map.get(h, 0) + 1

    if not headings_map:
        headings_map = {
            "Foundational Theory": 3,
            "Operational Methodology": 4,
            "Applied Problem Solving": 3,
            "Advanced Case Evaluation": 2
        }

    topics_summary = []
    total_chunks = max(sum(headings_map.values()), 1)
    allocated = 0

    items = list(headings_map.items())[:6]
    for idx, (h, count) in enumerate(items):
        if idx == len(items) - 1:
            q_count = max(1, total_questions - allocated)
        else:
            q_count = max(1, round((count / total_chunks) * total_questions))
            allocated += q_count

        topics_summary.append({
            "topic": h,
            "question_allocation": q_count,
            "recommended_focus": "High-frequency conceptual principles and application scenarios"
        })

    if target_difficulty == "easy":
        diff_split = {"easy": int(total_questions * 0.7), "medium": int(total_questions * 0.3), "hard": 0}
    elif target_difficulty == "hard":
        diff_split = {"easy": int(total_questions * 0.1), "medium": int(total_questions * 0.3), "hard": total_questions - int(total_questions * 0.4)}
    else:  # mixed
        diff_split = {
            "easy": max(1, int(total_questions * 0.3)),
            "medium": max(1, int(total_questions * 0.5)),
            "hard": max(1, total_questions - int(total_questions * 0.3) - int(total_questions * 0.5))
        }

    return {
        "title": f"Mastery Blueprint: {document_title}",
        "summary": f"Balanced assessment blueprint distributed across {len(topics_summary)} core modules with calibrated cognitive load.",
        "topics": topics_summary,
        "difficulty_split": diff_split,
        "recommended_time_minutes": max(10, total_questions * 2)
    }
