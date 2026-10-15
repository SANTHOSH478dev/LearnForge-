import os
import datetime
import json
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base
from app.models.user import User, StudentProfile, Achievement
from app.models.document import Document, DocumentChunk
from app.models.test import Test, Question, QuestionOption
from app.models.attempt import TestAttempt, StudentResponse
from app.models.revision import TopicMastery, MistakeNotebook, Flashcard
from app.services.auth_service import get_password_hash
from app.services.feedback_coach import generate_detailed_mistake_feedback

def run_seed():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # Check if demo student exists
    demo_user = db.query(User).filter(User.email == "student@learnforge.ai").first()
    if demo_user:
        print("Demo seed data already present. Skipping.")
        db.close()
        return

    print("Seeding LearnForge AI with production demo data...")

    # 1. Create Demo Student
    demo_user = User(
        email="student@learnforge.ai",
        hashed_password=get_password_hash("password123"),
        full_name="Alex Rivera",
        role="student",
        is_active=True
    )
    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)

    profile = StudentProfile(
        user_id=demo_user.id,
        academic_level="Senior Undergraduate (Computer Science & Engineering)",
        primary_subjects=json.dumps(["Distributed Systems", "Data Structures & Algorithms", "Cloud Architecture"]),
        learning_goals="Prepare for placement exams and master core systems engineering concepts.",
        daily_goal_minutes=45,
        current_streak=5,
        longest_streak=12,
        last_active_date=datetime.date.today().isoformat()
    )
    db.add(profile)

    # 2. Seed Document 1: Distributed Systems & Raft Consensus
    doc1 = Document(
        user_id=demo_user.id,
        title="Raft Consensus Algorithm & Distributed State Machines",
        file_name="raft_consensus_systems.pdf",
        file_type="pdf",
        file_size_bytes=420000,
        storage_path="virtual/raft_consensus_systems.pdf",
        processing_status="completed",
        page_count=6,
        summary_text="Comprehensive technical breakdown of the Raft distributed consensus protocol. Covers leader election, randomized heartbeats, log matching properties, committed entries, and safety invariants.",
        detected_topics=json.dumps(["Leader Election", "Log Replication", "Safety Invariants", "Split Brain Protection"]),
        key_concepts=json.dumps([
            {"term": "Heartbeat Mechanism", "definition": "Periodic empty AppendEntries RPCs sent by the leader to suppress candidate elections across followers."},
            {"term": "Term Number", "definition": "A monotonic logical clock identifying distinct epochs of leadership in Raft clusters."},
            {"term": "Quorum", "definition": "A strict majority of cluster nodes ((N/2) + 1) required to elect a leader or commit an entry."}
        ]),
        suggested_questions=json.dumps([
            {"prompt": "What ensures that two leaders cannot be elected in the same term?", "difficulty": "medium", "type": "mcq"}
        ])
    )
    db.add(doc1)
    db.commit()
    db.refresh(doc1)

    # Chunks for Doc 1
    chunks_doc1 = [
        DocumentChunk(
            document_id=doc1.id,
            chunk_index=0,
            page_number=1,
            section_heading="Overview & Server Roles",
            content="In the Raft protocol, each cluster node exists in one of three states: Leader, Follower, or Candidate. Under normal operations, exactly one leader handles all client requests and coordinates state machine replication. Followers are passive; they only respond to incoming RPCs from leaders and candidates.",
            token_count=52
        ),
        DocumentChunk(
            document_id=doc1.id,
            chunk_index=1,
            page_number=2,
            section_heading="Leader Election & Heartbeats",
            content="If a follower receives no communication over an election timeout interval (randomized between 150ms and 300ms), it assumes the leader has failed, increments its current term, transitions to candidate state, votes for itself, and broadcasts RequestVote RPCs.",
            token_count=48
        ),
        DocumentChunk(
            document_id=doc1.id,
            chunk_index=2,
            page_number=3,
            section_heading="Log Replication & Safety Invariants",
            content="Once elected, the leader begins accepting client log proposals. An entry is considered committed once it has been replicated across a strict majority (quorum) of nodes. Raft guarantees the Log Matching Property: if two entries in different logs have the same index and term, they store the same command, and their logs are identical in all preceding entries.",
            token_count=62
        )
    ]
    for c in chunks_doc1:
        db.add(c)
    db.commit()

    # 3. Seed Document 2: Data Structures & Balanced Trees
    doc2 = Document(
        user_id=demo_user.id,
        title="Balanced Search Trees & Asymptotic Analysis",
        file_name="balanced_trees_algorithms.docx",
        file_type="docx",
        file_size_bytes=310000,
        storage_path="virtual/balanced_trees_algorithms.docx",
        processing_status="completed",
        page_count=5,
        summary_text="Theoretical notes exploring self-balancing binary search trees (AVL Trees, Red-Black Trees) and multiway search trees (B-Trees). Focuses on tree rotations, height bounds, and worst-case search complexity.",
        detected_topics=json.dumps(["AVL Balance Factor", "Red-Black Invariants", "Tree Rotations", "B-Tree Branching"]),
        key_concepts=json.dumps([
            {"term": "Balance Factor", "definition": "The difference between the height of the left subtree and the right subtree: Balance = height(left) - height(right)."},
            {"term": "Black Height", "definition": "In Red-Black trees, the number of black nodes on any simple path from a node to any of its descendant leaves."}
        ])
    )
    db.add(doc2)
    db.commit()
    db.refresh(doc2)

    chunks_doc2 = [
        DocumentChunk(
            document_id=doc2.id,
            chunk_index=0,
            page_number=1,
            section_heading="AVL Tree Balance Factor",
            content="An AVL tree maintains the invariant that for every node, the height difference between left and right subtrees (the balance factor) is strictly in {-1, 0, +1}. When an insertion causes the balance factor to become +2 or -2, a rotation (Single Left, Single Right, Left-Right, or Right-Left) restores balance in O(1) time.",
            token_count=60
        ),
        DocumentChunk(
            document_id=doc2.id,
            chunk_index=1,
            page_number=2,
            section_heading="Red-Black Properties",
            content="Red-Black trees ensure that no simple path from the root to a leaf is more than twice as long as any other path. Every node is colored red or black, the root is black, red nodes cannot have red children, and every path contains the same number of black nodes.",
            token_count=52
        )
    ]
    for c in chunks_doc2:
        db.add(c)
    db.commit()

    # 4. Create an Initial Test for Raft Consensus
    test1 = Test(
        user_id=demo_user.id,
        document_ids=json.dumps([doc1.id]),
        title="Mastery Exam: Raft Consensus Protocols",
        subject="Distributed Systems",
        topic="Consensus & Replication",
        test_type="timed_exam",
        difficulty="medium",
        total_questions=5,
        time_limit_minutes=10,
        negative_marking=True,
        negative_mark_value=0.25,
        passing_percentage=60.0
    )
    db.add(test1)
    db.commit()
    db.refresh(test1)

    # Questions for Test 1
    q1 = Question(
        test_id=test1.id,
        order_index=0,
        question_text="What role is played by randomized election timeouts in the Raft consensus algorithm?",
        question_type="mcq",
        difficulty="medium",
        topic_tag="Leader Election",
        marks=2.0,
        source_document_id=doc1.id,
        source_document_title=doc1.title,
        source_page=2,
        source_passage_snippet="If a follower receives no communication over an election timeout interval (randomized between 150ms and 300ms)...",
        explanation_text="Randomized timeouts (e.g., 150-300ms) prevent split votes by ensuring one candidate almost always initiates an election before others."
    )
    db.add(q1)
    db.commit()
    db.refresh(q1)

    db.add(QuestionOption(question_id=q1.id, option_key="A", option_text="To prevent split-vote scenarios during concurrent candidate elections", is_correct=True))
    db.add(QuestionOption(question_id=q1.id, option_key="B", option_text="To increase disk writing latency across followers", is_correct=False))
    db.add(QuestionOption(question_id=q1.id, option_key="C", option_text="To allow non-majority clusters to commit state", is_correct=False))
    db.add(QuestionOption(question_id=q1.id, option_key="D", option_text="To bypass term counter increments during network partitions", is_correct=False))

    q2 = Question(
        test_id=test1.id,
        order_index=1,
        question_text="Under the Log Matching Property, what is guaranteed if two log entries share the exact same index and term?",
        question_type="mcq",
        difficulty="hard",
        topic_tag="Log Replication",
        marks=2.0,
        source_document_id=doc1.id,
        source_document_title=doc1.title,
        source_page=3,
        source_passage_snippet="if two entries in different logs have the same index and term, they store the same command...",
        explanation_text="Raft guarantees that identical (index, term) pairs store the exact same command, and all preceding log entries are identical."
    )
    db.add(q2)
    db.commit()
    db.refresh(q2)

    db.add(QuestionOption(question_id=q2.id, option_key="A", option_text="The logs are identical in all preceding entries and store the identical command", is_correct=True))
    db.add(QuestionOption(question_id=q2.id, option_key="B", option_text="The cluster immediately triggers a forced re-election", is_correct=False))
    db.add(QuestionOption(question_id=q2.id, option_key="C", option_text="One of the entries must be truncated immediately", is_correct=False))
    db.add(QuestionOption(question_id=q2.id, option_key="D", option_text="The entry is only valid on the leader node", is_correct=False))

    q3 = Question(
        test_id=test1.id,
        order_index=2,
        question_text="What minimum threshold of cluster nodes must acknowledge an entry before it is committed?",
        question_type="mcq",
        difficulty="easy",
        topic_tag="Quorum & Safety",
        marks=1.0,
        source_document_id=doc1.id,
        source_document_title=doc1.title,
        source_page=3,
        source_passage_snippet="An entry is considered committed once it has been replicated across a strict majority (quorum)...",
        explanation_text="A strict majority quorum ((N/2) + 1 nodes) is strictly required to commit an entry."
    )
    db.add(q3)
    db.commit()
    db.refresh(q3)

    db.add(QuestionOption(question_id=q3.id, option_key="A", option_text="A strict majority quorum ((N/2) + 1 nodes)", is_correct=True))
    db.add(QuestionOption(question_id=q3.id, option_key="B", option_text="Unanimous 100% agreement of all nodes", is_correct=False))
    db.add(QuestionOption(question_id=q3.id, option_key="C", option_text="At least one follower node", is_correct=False))
    db.add(QuestionOption(question_id=q3.id, option_key="D", option_text="Any two nodes regardless of cluster size", is_correct=False))

    q4 = Question(
        test_id=test1.id,
        order_index=3,
        question_text="True or False: In Raft, followers actively initiate client requests and write commands directly to disk.",
        question_type="true_false",
        difficulty="easy",
        topic_tag="Server Roles",
        marks=1.0,
        source_document_id=doc1.id,
        source_document_title=doc1.title,
        source_page=1,
        source_passage_snippet="Followers are passive; they only respond to incoming RPCs from leaders and candidates.",
        explanation_text="False: In Raft, followers are passive and only respond to RPCs. Only the elected leader accepts client requests."
    )
    db.add(q4)
    db.commit()
    db.refresh(q4)

    db.add(QuestionOption(question_id=q4.id, option_key="A", option_text="True", is_correct=False))
    db.add(QuestionOption(question_id=q4.id, option_key="B", option_text="False", is_correct=True))

    q5 = Question(
        test_id=test1.id,
        order_index=4,
        question_text="What happens when a follower receives an AppendEntries RPC containing a term number lower than its own current term?",
        question_type="mcq",
        difficulty="hard",
        topic_tag="Term Verification",
        marks=2.0,
        source_document_id=doc1.id,
        source_document_title=doc1.title,
        source_page=2,
        source_passage_snippet="Followers reject requests from stale leaders with lower terms.",
        explanation_text="Followers reject stale requests from past leaders whose term is strictly less than the follower's current term."
    )
    db.add(q5)
    db.commit()
    db.refresh(q5)

    db.add(QuestionOption(question_id=q5.id, option_key="A", option_text="The follower rejects the RPC request immediately", is_correct=True))
    db.add(QuestionOption(question_id=q5.id, option_key="B", option_text="The follower adopts the lower term number", is_correct=False))
    db.add(QuestionOption(question_id=q5.id, option_key="C", option_text="The follower resigns from the cluster", is_correct=False))
    db.add(QuestionOption(question_id=q5.id, option_key="D", option_text="The follower resets its state machine to zero", is_correct=False))
    db.commit()

    # 5. Create a Seeded Completed Attempt for Test 1
    started_time = datetime.datetime.utcnow() - datetime.timedelta(hours=2, minutes=10)
    sub_time = started_time + datetime.timedelta(minutes=6, seconds=45)
    deadline_time = started_time + datetime.timedelta(minutes=10)

    attempt1 = TestAttempt(
        test_id=test1.id,
        user_id=demo_user.id,
        started_at=started_time,
        server_deadline=deadline_time,
        submitted_at=sub_time,
        is_submitted=True,
        status="submitted",
        total_score=6.0,
        max_possible_score=8.0,
        percentage=75.0,
        grade="B",
        time_taken_seconds=405,
        correct_count=4,
        incorrect_count=1,
        unanswered_count=0,
        ai_summary_feedback="Strong understanding of leader election and quorum requirements in Raft. The single misconception was on stale term rejection.",
        ai_study_plan_recommendation="Review term comparison mechanics in Section 'Leader Election & Heartbeats'. Practice 3 questions on network partitions."
    )
    db.add(attempt1)
    db.commit()
    db.refresh(attempt1)

    # Responses for Attempt 1: Q1, Q2, Q3, Q4 correct; Q5 answered wrongly (selected B instead of A)
    r1 = StudentResponse(attempt_id=attempt1.id, question_id=q1.id, selected_option_key="A", is_correct=True, score_awarded=2.0)
    r2 = StudentResponse(attempt_id=attempt1.id, question_id=q2.id, selected_option_key="A", is_correct=True, score_awarded=2.0)
    r3 = StudentResponse(attempt_id=attempt1.id, question_id=q3.id, selected_option_key="A", is_correct=True, score_awarded=1.0)
    r4 = StudentResponse(attempt_id=attempt1.id, question_id=q4.id, selected_option_key="B", is_correct=True, score_awarded=1.0)
    
    # Q5 wrong
    fb_q5 = generate_detailed_mistake_feedback(
        question_text=q5.question_text,
        selected_option_key="B",
        selected_option_text="The follower adopts the lower term number",
        correct_option_key="A",
        correct_option_text="The follower rejects the RPC request immediately",
        explanation_text=q5.explanation_text,
        topic_tag="Term Verification",
        source_heading="Leader Election & Heartbeats",
        source_page=2
    )
    r5 = StudentResponse(
        attempt_id=attempt1.id,
        question_id=q5.id,
        selected_option_key="B",
        is_correct=False,
        score_awarded=-0.25, # Negative marking
        ai_feedback_json=json.dumps(fb_q5)
    )
    for r in [r1, r2, r3, r4, r5]:
        db.add(r)
    db.commit()

    # 6. Seed Topic Mastery
    tm1 = TopicMastery(
        user_id=demo_user.id,
        subject="Distributed Systems",
        topic="Leader Election",
        total_attempted=4,
        total_correct=4,
        accuracy_rate=100.0,
        mastery_level="mastered"
    )
    tm2 = TopicMastery(
        user_id=demo_user.id,
        subject="Distributed Systems",
        topic="Log Replication",
        total_attempted=3,
        total_correct=2,
        accuracy_rate=66.7,
        mastery_level="competent"
    )
    tm3 = TopicMastery(
        user_id=demo_user.id,
        subject="Distributed Systems",
        topic="Term Verification",
        total_attempted=2,
        total_correct=0,
        accuracy_rate=0.0,
        mastery_level="learning"
    )
    tm4 = TopicMastery(
        user_id=demo_user.id,
        subject="Algorithms",
        topic="AVL Balance Factor",
        total_attempted=5,
        total_correct=4,
        accuracy_rate=80.0,
        mastery_level="mastered"
    )
    for tm in [tm1, tm2, tm3, tm4]:
        db.add(tm)
    db.commit()

    # 7. Seed Mistake Notebook
    mistake1 = MistakeNotebook(
        user_id=demo_user.id,
        question_id=q5.id,
        attempt_id=attempt1.id,
        question_text=q5.question_text,
        user_wrong_answer="Option B: The follower adopts the lower term number",
        correct_answer="Option A: The follower rejects the RPC request immediately",
        explanation=q5.explanation_text,
        core_concept="Term Monotonicity & Stale Leader Rejection",
        topic_tag="Term Verification",
        source_reference="Page 2: Leader Election & Heartbeats",
        reviewed_count=1,
        is_resolved=False
    )
    db.add(mistake1)
    db.commit()

    # 8. Seed Achievements
    badges = [
        Achievement(
            user_id=demo_user.id,
            badge_type="welcome",
            badge_title="Cadet of Knowledge",
            badge_description="Activated LearnForge AI and personalized learning workspace.",
            icon_name="Sparkles"
        ),
        Achievement(
            user_id=demo_user.id,
            badge_type="first_upload",
            badge_title="Knowledge Ingestion",
            badge_description="Uploaded and successfully chunked academic source documents.",
            icon_name="FileText"
        ),
        Achievement(
            user_id=demo_user.id,
            badge_type="exam_initiate",
            badge_title="Exam Pioneer",
            badge_description="Completed first timed assessment under server-side deadline monitoring.",
            icon_name="Timer"
        )
    ]
    for b in badges:
        db.add(b)
    db.commit()

    # 9. Seed Spaced Repetition Flashcards
    cards = [
        Flashcard(
            user_id=demo_user.id,
            document_id=doc1.id,
            topic="Distributed Systems",
            front_prompt="What are the three core states a node can inhabit in the Raft consensus protocol?",
            back_explanation="Leader (handles requests), Follower (passive responder), and Candidate (seeks votes during elections).",
            difficulty="easy",
            interval_days=3,
            repetition_count=2,
            ease_factor=2.6,
            next_review_date=datetime.date.today()
        ),
        Flashcard(
            user_id=demo_user.id,
            document_id=doc1.id,
            topic="Distributed Systems",
            front_prompt="What is the significance of the randomized election timeout in Raft?",
            back_explanation="It splits the election initiation window between 150ms and 300ms, effectively avoiding split votes where candidates simultaneously request votes.",
            difficulty="medium",
            interval_days=1,
            repetition_count=1,
            ease_factor=2.5,
            next_review_date=datetime.date.today()
        ),
        Flashcard(
            user_id=demo_user.id,
            document_id=doc2.id,
            topic="Data Structures",
            front_prompt="What is the definition of the Balance Factor in an AVL Tree?",
            back_explanation="Balance Factor = height(left subtree) - height(right subtree). For an AVL tree to remain valid, this value must always belong to {-1, 0, +1}.",
            difficulty="medium",
            interval_days=6,
            repetition_count=3,
            ease_factor=2.7,
            next_review_date=datetime.date.today() + datetime.timedelta(days=2)
        )
    ]
    for c in cards:
        db.add(c)
    db.commit()

    db.close()
    print("Seed complete! Demo student (student@learnforge.ai / password123) is ready.")

if __name__ == "__main__":
    run_seed()
