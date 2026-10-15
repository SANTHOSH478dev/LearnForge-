export interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  email: string;
  full_name: string;
  role: string;
}

export interface DashboardMetrics {
  total_materials_uploaded: number;
  total_tests_completed: number;
  average_score_percentage: number;
  study_time_minutes: number;
  current_streak_days: number;
  longest_streak_days: number;
  daily_goal_minutes: number;
  daily_goal_progress_percent: number;
  weekly_performance: Array<{
    day: string;
    date: string;
    tests_taken: number;
    score: number;
  }>;
  subject_accuracy: Array<{
    subject: string;
    accuracy: number;
    total_questions: number;
  }>;
  weakest_concepts: Array<{
    topic: string;
    accuracy: number;
    attempts: number;
  }>;
  recent_attempts: Array<{
    id: number;
    test_id: number;
    title: string;
    score: number;
    max_score: number;
    percentage: number;
    grade: string;
    date: string;
  }>;
  continue_learning: Array<{
    document_id: number;
    title: string;
    page_count: number;
    topics_count: number;
    status: string;
  }>;
  recommended_next_step: {
    title: string;
    description: string;
    action_text: string;
    action_route: string;
  };
  daily_challenge: {
    title: string;
    objective: string;
    reward_points: string;
    is_completed: boolean;
  };
}

export interface DocumentItem {
  id: number;
  user_id: number;
  title: string;
  file_name: string;
  file_type: string;
  file_size_bytes: number;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  page_count: number;
  detected_topics: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentChunk {
  id: number;
  chunk_index: number;
  page_number: number;
  section_heading: string;
  content: string;
  token_count: number;
}

export interface DocumentDetail extends DocumentItem {
  summary_text?: string;
  key_concepts?: string;
  suggested_questions?: string;
  error_message?: string;
  chunks: DocumentChunk[];
}

export interface DocumentSummary {
  id: number;
  title: string;
  page_count: number;
  summary_text: string;
  key_concepts: Array<{ term: string; definition: string }>;
  detected_topics: string[];
  suggested_questions: Array<{ prompt: string; difficulty: string; type: string }>;
}

export interface QuestionOption {
  id: number;
  option_key: string;
  option_text: string;
}

export interface Question {
  id: number;
  order_index: number;
  question_text: string;
  question_type: string;
  difficulty: string;
  topic_tag: string;
  marks: number;
  source_document_id?: number;
  source_document_title?: string;
  source_page?: number;
  source_passage_snippet?: string;
  options: QuestionOption[];
}

export interface TestDetail {
  id: number;
  user_id: number;
  title: string;
  subject: string;
  topic: string;
  test_type: string;
  difficulty: string;
  total_questions: number;
  time_limit_minutes: number;
  negative_marking: boolean;
  negative_mark_value: number;
  passing_percentage: number;
  created_at: string;
  questions: Question[];
}

export interface AttemptStartData {
  attempt_id: number;
  test_id: number;
  title: string;
  time_limit_minutes: number;
  server_deadline: string;
  started_at: string;
  total_questions: number;
  negative_marking: boolean;
  negative_mark_value: number;
  questions: Question[];
  saved_answers: Record<string, string>;
  marked_for_review: number[];
}

export interface AIFeedbackDetail {
  what_student_selected: string;
  what_correct_answer_is: string;
  why_selected_incorrect: string;
  underlying_concept: string;
  simple_example: string;
  document_section_to_revise: string;
  follow_up_question: string;
}

export interface QuestionResultDetail {
  question_id: number;
  order_index: number;
  question_text: string;
  difficulty: string;
  topic_tag: string;
  marks_possible: number;
  marks_awarded: number;
  user_answer?: string;
  correct_answer: string;
  is_correct: boolean;
  is_unanswered: boolean;
  explanation: string;
  source_citation?: {
    document_id?: number;
    document_title?: string;
    page_number?: number;
    snippet?: string;
  };
  ai_feedback?: AIFeedbackDetail;
}

export interface AttemptResultData {
  attempt_id: number;
  test_id: number;
  test_title: string;
  total_score: number;
  max_possible_score: number;
  percentage: number;
  grade: string;
  status: string;
  time_taken_seconds: number;
  correct_count: number;
  incorrect_count: number;
  unanswered_count: number;
  started_at: string;
  submitted_at?: string;
  topic_breakdown: Array<{
    topic: string;
    accuracy: number;
    correct: number;
    total: number;
  }>;
  difficulty_breakdown: Array<{
    difficulty: string;
    accuracy: number;
    correct: number;
    total: number;
  }>;
  comparison_with_previous: {
    has_previous: boolean;
    previous_percentage?: number;
    previous_grade?: string;
    improvement_percentage: number;
    message: string;
  };
  ai_summary_feedback?: string;
  ai_study_plan_recommendation?: string;
  question_results: QuestionResultDetail[];
}

export interface WeaknessConcept {
  topic: string;
  subject: string;
  accuracy_rate: number;
  total_attempted: number;
  recommended_focus: string;
  suggested_revision_action: string;
}

export interface WeaknessAnalysis {
  overall_mastery_score: number;
  weakest_topics: WeaknessConcept[];
  moderate_topics: WeaknessConcept[];
  strong_topics: WeaknessConcept[];
  recommended_study_hours: number;
  suggested_adaptive_test_id?: number;
}

export interface MistakeItem {
  id: number;
  question_id?: number;
  attempt_id?: number;
  question_text: string;
  user_wrong_answer?: string;
  correct_answer: string;
  explanation: string;
  core_concept?: string;
  topic_tag: string;
  source_reference?: string;
  reviewed_count: number;
  is_resolved: boolean;
  added_at: string;
}

export interface Flashcard {
  id: number;
  document_id?: number;
  topic: string;
  front_prompt: string;
  back_explanation: string;
  key_terms: string;
  difficulty: string;
  interval_days: number;
  repetition_count: number;
  ease_factor: number;
  next_review_date: string;
}

export interface DailyPlan {
  today_date: string;
  greeting: string;
  target_study_minutes: number;
  streak_count: number;
  due_flashcards_count: number;
  unresolved_mistakes_count: number;
  primary_revision_topic: string;
  recommended_actions: Array<{
    title: string;
    type: string;
    estimated_mins: number;
  }>;
}

export interface DoubtCitation {
  document_id?: number;
  document_title: string;
  page_number?: number;
  section_heading?: string;
  passage_snippet: string;
  relevance_score: number;
}

export interface DoubtMessage {
  id: number;
  query_text: string;
  response_text: string;
  citations: DoubtCitation[];
  created_at: string;
}
