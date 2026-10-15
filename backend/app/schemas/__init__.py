from app.schemas.auth import UserRegister, UserLogin, Token, TokenData, UserOut, PasswordResetRequest
from app.schemas.profile import ProfileUpdate, StudentProfileOut, AchievementOut, DashboardMetrics
from app.schemas.document import DocumentOut, DocumentDetailOut, DocumentChunkOut, DocumentSummaryOut
from app.schemas.test import (
    OptionCreate, OptionOut, OptionOutWithAnswer, QuestionCreate, QuestionOut, QuestionDetailOut,
    GenerateTestRequest, TestOut, TestDetailOut, ExamBlueprintRequest, ExamBlueprintResponse
)
from app.schemas.attempt import (
    StartAttemptResponse, AnswerSaveRequest, AnswerSaveResponse, SubmitAttemptRequest,
    QuestionResultDetail, AttemptResultResponse
)
from app.schemas.revision import (
    TopicMasteryOut, WeaknessConcept, WeaknessAnalysisResponse, MistakeItemOut,
    ResolveMistakeRequest, FlashcardOut, FlashcardCreateRequest, FlashcardReviewRequest, DailyPlanOut
)
from app.schemas.doubt import DoubtCitation, DoubtAskRequest, DoubtResponseOut

__all__ = [
    "UserRegister", "UserLogin", "Token", "TokenData", "UserOut", "PasswordResetRequest",
    "ProfileUpdate", "StudentProfileOut", "AchievementOut", "DashboardMetrics",
    "DocumentOut", "DocumentDetailOut", "DocumentChunkOut", "DocumentSummaryOut",
    "OptionCreate", "OptionOut", "OptionOutWithAnswer", "QuestionCreate", "QuestionOut", "QuestionDetailOut",
    "GenerateTestRequest", "TestOut", "TestDetailOut", "ExamBlueprintRequest", "ExamBlueprintResponse",
    "StartAttemptResponse", "AnswerSaveRequest", "AnswerSaveResponse", "SubmitAttemptRequest",
    "QuestionResultDetail", "AttemptResultResponse",
    "TopicMasteryOut", "WeaknessConcept", "WeaknessAnalysisResponse", "MistakeItemOut",
    "ResolveMistakeRequest", "FlashcardOut", "FlashcardCreateRequest", "FlashcardReviewRequest", "DailyPlanOut",
    "DoubtCitation", "DoubtAskRequest", "DoubtResponseOut"
]
