"""State definitions and models for APIForge AI multi-agent framework."""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class RequirementEntity(BaseModel):
    name: str
    description: str = ""
    fields: Dict[str, str] = Field(default_factory=dict, description="field name -> field type")
    relationships: List[str] = Field(default_factory=list)


class RequirementEndpoint(BaseModel):
    path: str
    method: str
    summary: str
    description: str = ""
    auth_required: bool = False
    request_schema: Optional[Any] = None
    response_schema: Optional[Any] = None
    expected_status_codes: List[int] = Field(default_factory=lambda: [200])


class StructuredRequirements(BaseModel):
    title: str
    version: str = "1.0.0"
    description: str = ""
    auth_type: str = "bearer"  # none, api_key, bearer, oauth2
    entities: List[RequirementEntity] = Field(default_factory=list)
    endpoints: List[RequirementEndpoint] = Field(default_factory=list)
    business_rules: List[str] = Field(default_factory=list)


class ReviewFinding(BaseModel):
    rule_id: str
    category: str  # rest_compliance, schema_completeness, security, documentation, error_handling
    severity: str  # critical, warning, info
    path: str  # e.g. /users, paths./users.post
    message: str
    recommendation: str
    suggested_patch: Optional[Dict[str, Any]] = None


class QualityScoreModel(BaseModel):
    overall_score: float = 0.0  # 0 to 100
    rest_compliance_score: float = 0.0
    schema_completeness_score: float = 0.0
    security_score: float = 0.0
    documentation_score: float = 0.0
    summary: str = ""
    passed_threshold: bool = False
    findings_count: Dict[str, int] = Field(default_factory=dict)


class TestResultItem(BaseModel):
    __test__ = False
    test_name: str
    status: str  # PASSED, FAILED, ERROR
    duration_sec: float = 0.0
    error_message: Optional[str] = None


class TestExecutionReport(BaseModel):
    __test__ = False
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    duration_sec: float = 0.0
    success: bool = False
    logs: str = ""
    items: List[TestResultItem] = Field(default_factory=list)


class EvaluationMetricsModel(BaseModel):
    """The 8 core evaluation metrics from the project research paper."""
    openapi_validation_accuracy: float = 0.0       # % syntactically valid OAS
    rest_design_compliance: float = 0.0            # % adherence to REST standards
    documentation_completeness: float = 0.0        # % coverage of docs, examples, descriptions
    security_recommendation_coverage: float = 0.0  # % of security smells addressed
    api_quality_score: float = 0.0                 # 0-100 aggregate review score
    test_case_success_rate: float = 0.0            # % tests passed
    execution_reliability: float = 0.0             # % APIs running cleanly
    error_reduction_rate: float = 0.0              # % defect reduction pre- vs post-review


class AgentTrace(BaseModel):
    agent_name: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    action: str
    details: Dict[str, Any] = Field(default_factory=dict)


class APIForgeState(BaseModel):
    raw_requirements: str
    structured_requirements: Optional[StructuredRequirements] = None
    openapi_spec: Optional[Dict[str, Any]] = None
    spec_draft_history: List[Dict[str, Any]] = Field(default_factory=list)
    review_findings: List[ReviewFinding] = Field(default_factory=list)
    review_iterations: int = 0
    quality_scores: List[QualityScoreModel] = Field(default_factory=list)
    documentation_files: Dict[str, str] = Field(default_factory=dict)
    generated_code_files: Dict[str, str] = Field(default_factory=dict)
    test_code_files: Dict[str, str] = Field(default_factory=dict)
    test_reports: List[TestExecutionReport] = Field(default_factory=list)
    debug_iterations: int = 0
    evaluation_metrics: Optional[EvaluationMetricsModel] = None
    traces: List[AgentTrace] = Field(default_factory=list)
    status: str = "pending"

    def log_trace(self, agent_name: str, action: str, **kwargs: Any) -> None:
        self.traces.append(AgentTrace(agent_name=agent_name, action=action, details=kwargs))
