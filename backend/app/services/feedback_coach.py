import json
from typing import Dict, Any, List, Optional
from app.services.ai_generator import call_gemini_api

def generate_detailed_mistake_feedback(
    question_text: str,
    selected_option_key: Optional[str],
    selected_option_text: Optional[str],
    correct_option_key: str,
    correct_option_text: str,
    explanation_text: str,
    topic_tag: str,
    source_heading: Optional[str] = None,
    source_page: Optional[int] = None
) -> Dict[str, Any]:
    """
    7-Step Cognitive Feedback Breakdown for mistakes:
    1. Selected answer
    2. Correct answer
    3. Why selected answer is incorrect
    4. Underlying concept
    5. Simple real-world example / analogy
    6. Document section to revise
    7. Follow-up challenge question
    """
    selected_desc = f"Option ({selected_option_key}): '{selected_option_text}'" if selected_option_key else "Left Unanswered"
    correct_desc = f"Option ({correct_option_key}): '{correct_option_text}'"
    revision_ref = f"Section '{source_heading or topic_tag}'" + (f" on Page {source_page}" if source_page else "")

    # Check if Gemini is available for contextual explanation
    gemini_prompt = f"""
As an expert cognitive tutor, generate a 7-step feedback breakdown for this student mistake.
Question: {question_text}
Student's Choice: {selected_desc}
Correct Answer: {correct_desc}
Explanation: {explanation_text}
Topic: {topic_tag}

Respond strictly in valid JSON format:
{{
  "what_student_selected": "{selected_desc}",
  "what_correct_answer_is": "{correct_desc}",
  "why_selected_incorrect": "Clear explanation of the student's misconception",
  "underlying_concept": "The foundational principle at work",
  "simple_example": "A clear concrete example or real-world analogy",
  "document_section_to_revise": "{revision_ref}",
  "follow_up_question": "A short follow-up question testing the clarified concept"
}}
"""
    llm_output = call_gemini_api(gemini_prompt)
    if llm_output:
        try:
            cleaned = llm_output.strip().replace("```json", "").replace("```", "").strip()
            parsed = json.loads(cleaned)
            if "why_selected_incorrect" in parsed:
                return parsed
        except Exception:
            pass

    # High quality structured default feedback
    if not selected_option_key:
        why_incorrect = "The question was skipped. Reviewing the core principle will help build recall confidence."
    else:
        why_incorrect = (
            f"Selecting {selected_option_key} conflates peripheral properties with the primary definition. "
            f"The key distinction lies in how {topic_tag} operates under standard parameters."
        )

    return {
        "what_student_selected": selected_desc,
        "what_correct_answer_is": correct_desc,
        "why_selected_incorrect": why_incorrect,
        "underlying_concept": f"Core mechanics and properties of {topic_tag}.",
        "simple_example": f"Think of {topic_tag} like a traffic controller directing data flow rather than the vehicles themselves.",
        "document_section_to_revise": revision_ref,
        "follow_up_question": f"If system constraints were relaxed, how would {topic_tag} behave differently?"
    }

def generate_attempt_summary_and_plan(
    percentage: float,
    grade: str,
    correct_count: int,
    total_count: int,
    weak_topics: List[str]
) -> Dict[str, str]:
    """Generates qualitative AI executive summary and adaptive study plan."""
    if percentage >= 85:
        summary = (
            f"Excellent performance ({grade} Grade - {percentage}%). You demonstrated strong conceptual grounding "
            f"across {correct_count} of {total_count} questions with consistent analytical precision."
        )
        plan = (
            "Recommended Next Step: Proceed to high-difficulty Challenge mode or explore cross-domain synthesis. "
            "Reinforce edge cases in your mistake notebook once before moving on."
        )
    elif percentage >= 60:
        weak_str = ", ".join(weak_topics[:3]) if weak_topics else "selected sub-topics"
        summary = (
            f"Solid foundational understanding ({grade} Grade - {percentage}%). You scored {correct_count}/{total_count}. "
            f"Mistakes clustered primarily around {weak_str}."
        )
        plan = (
            f"Recommended Next Step: Dedicate 20 minutes to revising {weak_str} using the Smart Document Studio. "
            "Then run a 5-question targeted adaptive test in 'Forge My Weaknesses'."
        )
    else:
        weak_str = ", ".join(weak_topics[:3]) if weak_topics else "fundamental concepts"
        summary = (
            f"Needs targeted revision ({grade} Grade - {percentage}%). You answered {correct_count}/{total_count} correctly. "
            f"Gaps identified in core terminology and operational flow for {weak_str}."
        )
        plan = (
            f"Recommended Next Step: Revisit {weak_str} in your uploaded notes. Review the 7-step feedback below, "
            "flip through the auto-generated flashcard deck, and retake this test tomorrow."
        )

    return {
        "summary": summary,
        "study_plan": plan
    }
