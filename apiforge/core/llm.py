"""Uniform LLM Client abstraction supporting Google Gemini, OpenAI, Anthropic, and deterministic Mock/Offline mode."""

from __future__ import annotations
import json
import os
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

T = TypeVar("T", bound=BaseModel)


class BaseLLMClient(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str:
        """Generate plain text from prompt."""
        pass

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Generate structured JSON from prompt."""
        response = self.generate_text(prompt, system_prompt, **kwargs)
        # Extract markdown json block if present
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response)
        text = json_match.group(1) if json_match else response
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError as err:
            # Fallback: find first { and last }
            first_brace = text.find("{")
            last_brace = text.rfind("}")
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                return json.loads(text[first_brace:last_brace + 1])
            raise ValueError(f"Failed to parse LLM response as JSON: {err}\nResponse was:\n{response}")

    def generate_structured(self, model_cls: Type[T], prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> T:
        """Generate typed Pydantic model from prompt."""
        data = self.generate_json(prompt, system_prompt, **kwargs)
        return model_cls.model_validate(data)


class GeminiLLMClient(BaseLLMClient):
    """Client for Google Gemini models via google-genai or direct REST."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required for GeminiLLMClient.")
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
        except ImportError:
            self.client = None

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str:
        if self.client:
            from google.genai import types
            config = types.GenerateContentConfig(
                system_instruction=system_prompt if system_prompt else None,
                temperature=kwargs.get("temperature", 0.2),
            )
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )
            return response.text or ""
        else:
            # Direct HTTP fallback
            import httpx
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            payload: Dict[str, Any] = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            if system_prompt:
                payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}
            res = httpx.post(url, json=payload, timeout=60.0)
            res.raise_for_status()
            data = res.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]


class OpenAILLMClient(BaseLLMClient):
    """Client for OpenAI models (GPT-4o, etc.)."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for OpenAILLMClient.")
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.2),
        )
        return resp.choices[0].message.content or ""


class MockLLMClient(BaseLLMClient):
    """Deterministic, rule-guided mock LLM for offline testing, benchmarks, and predictable workflows."""

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str:
        prompt_lower = prompt.lower()
        if any(k in prompt_lower for k in ("requirements to analyze", "structured requirements", "requirement analysis", "structured json")):
            if "healthcare" in prompt_lower or "patient" in prompt_lower:
                return json.dumps({
                    "title": "Healthcare Clinical API",
                    "version": "1.0.0",
                    "description": "API for patient health records and clinical appointments.",
                    "auth_type": "bearer",
                    "entities": [
                        {"name": "Patient", "description": "Patient record", "fields": {"id": "uuid", "full_name": "string", "birth_date": "string"}},
                        {"name": "Appointment", "description": "Clinical appointment", "fields": {"id": "uuid", "patient_id": "string", "appointment_time": "datetime", "status": "string"}}
                    ],
                    "endpoints": [
                        {"path": "/patients", "method": "GET", "summary": "List patients", "auth_required": True, "response_schema": "PatientListResponse", "expected_status_codes": [200, 401]},
                        {"path": "/patients", "method": "POST", "summary": "Register patient", "auth_required": True, "request_schema": "PatientCreate", "response_schema": "PatientResponse", "expected_status_codes": [201, 400, 401]},
                        {"path": "/patients/{patient_id}", "method": "GET", "summary": "Get patient", "auth_required": True, "response_schema": "PatientResponse", "expected_status_codes": [200, 401, 404]},
                        {"path": "/appointments", "method": "POST", "summary": "Schedule appointment", "auth_required": True, "request_schema": "AppointmentCreate", "response_schema": "AppointmentResponse", "expected_status_codes": [201, 400, 401]},
                        {"path": "/appointments/{appointment_id}", "method": "DELETE", "summary": "Cancel appointment", "auth_required": True, "expected_status_codes": [204, 401, 404]}
                    ],
                    "business_rules": ["All clinical actions require Bearer JWT"]
                }, indent=2)

            if "ecommerce" in prompt_lower or "e-commerce" in prompt_lower or "product" in prompt_lower:
                return json.dumps({
                    "title": "E-Commerce Store API",
                    "version": "1.0.0",
                    "description": "API for products, orders, and customer management.",
                    "auth_type": "bearer",
                    "entities": [
                        {"name": "Product", "description": "Store merchandise", "fields": {"id": "uuid", "title": "string", "price": "number", "stock": "integer"}},
                        {"name": "Order", "description": "Customer purchase order", "fields": {"id": "uuid", "customer_id": "string", "total_amount": "number", "status": "string"}}
                    ],
                    "endpoints": [
                        {"path": "/products", "method": "GET", "summary": "List products", "auth_required": False, "response_schema": "ProductListResponse", "expected_status_codes": [200]},
                        {"path": "/products", "method": "POST", "summary": "Create product", "auth_required": True, "request_schema": "ProductCreate", "response_schema": "ProductResponse", "expected_status_codes": [201, 400, 401]},
                        {"path": "/products/{product_id}", "method": "GET", "summary": "Get product", "auth_required": False, "response_schema": "ProductResponse", "expected_status_codes": [200, 404]},
                        {"path": "/orders", "method": "POST", "summary": "Place order", "auth_required": True, "request_schema": "OrderCreate", "response_schema": "OrderResponse", "expected_status_codes": [201, 400, 401]},
                        {"path": "/orders", "method": "GET", "summary": "List orders", "auth_required": True, "response_schema": "OrderListResponse", "expected_status_codes": [200, 401]},
                        {"path": "/orders/{order_id}", "method": "GET", "summary": "Get order", "auth_required": True, "response_schema": "OrderResponse", "expected_status_codes": [200, 401, 404]}
                    ],
                    "business_rules": ["Order creation requires valid bearer token"]
                }, indent=2)

            if "iot" in prompt_lower or "telemetry" in prompt_lower or "device" in prompt_lower:
                return json.dumps({
                    "title": "IoT Device Telemetry API",
                    "version": "1.0.0",
                    "description": "API for IoT hardware devices and sensor telemetry ingestion.",
                    "auth_type": "bearer",
                    "entities": [
                        {"name": "Device", "description": "Hardware sensor node", "fields": {"id": "uuid", "serial_number": "string", "status": "string"}},
                        {"name": "Telemetry", "description": "Telemetry reading", "fields": {"id": "uuid", "device_id": "string", "temperature": "number", "humidity": "number"}}
                    ],
                    "endpoints": [
                        {"path": "/devices", "method": "GET", "summary": "List devices", "auth_required": True, "response_schema": "DeviceListResponse", "expected_status_codes": [200, 401]},
                        {"path": "/devices", "method": "POST", "summary": "Provision device", "auth_required": True, "request_schema": "DeviceCreate", "response_schema": "DeviceResponse", "expected_status_codes": [201, 400, 401]},
                        {"path": "/devices/{device_id}", "method": "GET", "summary": "Get device", "auth_required": True, "response_schema": "DeviceResponse", "expected_status_codes": [200, 401, 404]},
                        {"path": "/telemetries", "method": "POST", "summary": "Ingest telemetry", "auth_required": True, "request_schema": "TelemetryCreate", "response_schema": "TelemetryResponse", "expected_status_codes": [201, 400, 401]},
                        {"path": "/telemetries/{telemetry_id}", "method": "GET", "summary": "Get telemetry", "auth_required": True, "response_schema": "TelemetryResponse", "expected_status_codes": [200, 401, 404]}
                    ],
                    "business_rules": ["Device provisioning requires Bearer token"]
                }, indent=2)

            # Default: Task Management
            return json.dumps({
                "title": "Task & Project Management API",
                "version": "1.0.0",
                "description": "API for managing projects, tasks, team assignments, and statuses.",
                "auth_type": "bearer",
                "entities": [
                    {
                        "name": "Project",
                        "description": "A workspace containing tasks",
                        "fields": {"id": "string", "name": "string", "description": "string", "created_at": "string"},
                        "relationships": ["Task"]
                    },
                    {
                        "name": "Task",
                        "description": "An actionable work item within a project",
                        "fields": {"id": "string", "project_id": "string", "title": "string", "status": "string", "assigned_to": "string"},
                        "relationships": ["Project"]
                    }
                ],
                "endpoints": [
                    {
                        "path": "/projects",
                        "method": "POST",
                        "summary": "Create a new project",
                        "description": "Creates a project workspace",
                        "auth_required": True,
                        "request_schema": "ProjectCreate",
                        "response_schema": "ProjectResponse",
                        "expected_status_codes": [201, 400, 401]
                    },
                    {
                        "path": "/projects",
                        "method": "GET",
                        "summary": "List all projects",
                        "description": "Retrieves paginated list of projects",
                        "auth_required": True,
                        "response_schema": "ProjectListResponse",
                        "expected_status_codes": [200, 401]
                    },
                    {
                        "path": "/projects/{project_id}",
                        "method": "GET",
                        "summary": "Get project by ID",
                        "description": "Fetches a project by its unique ID",
                        "auth_required": True,
                        "response_schema": "ProjectResponse",
                        "expected_status_codes": [200, 401, 404]
                    },
                    {
                        "path": "/projects/{project_id}",
                        "method": "DELETE",
                        "summary": "Delete project",
                        "description": "Deletes project by ID",
                        "auth_required": True,
                        "expected_status_codes": [204, 401, 404]
                    },
                    {
                        "path": "/tasks",
                        "method": "POST",
                        "summary": "Create task",
                        "description": "Creates a new task",
                        "auth_required": True,
                        "request_schema": "TaskCreate",
                        "response_schema": "TaskResponse",
                        "expected_status_codes": [201, 400, 401]
                    },
                    {
                        "path": "/tasks",
                        "method": "GET",
                        "summary": "List tasks",
                        "description": "Retrieves tasks",
                        "auth_required": True,
                        "response_schema": "TaskListResponse",
                        "expected_status_codes": [200, 401]
                    },
                    {
                        "path": "/tasks/{task_id}",
                        "method": "GET",
                        "summary": "Get task",
                        "description": "Fetches task by ID",
                        "auth_required": True,
                        "response_schema": "TaskResponse",
                        "expected_status_codes": [200, 401, 404]
                    },
                    {
                        "path": "/tasks/{task_id}",
                        "method": "DELETE",
                        "summary": "Delete task",
                        "description": "Deletes task by ID",
                        "auth_required": True,
                        "expected_status_codes": [204, 401, 404]
                    }
                ],
                "business_rules": [
                    "Task status must be one of: todo, in_progress, completed",
                    "Only authenticated users can create or modify projects and tasks"
                ]
            }, indent=2)

        return json.dumps({"status": "ok", "message": "Mock LLM completion"})


def get_llm_client(provider: str = "auto", api_key: Optional[str] = None, model: Optional[str] = None) -> BaseLLMClient:
    """Factory to get the appropriate LLM client."""
    provider = provider.lower()
    if provider == "gemini" or (provider == "auto" and os.getenv("GEMINI_API_KEY")):
        return GeminiLLMClient(api_key=api_key, model=model or "gemini-2.5-flash")
    if provider == "openai" or (provider == "auto" and os.getenv("OPENAI_API_KEY")):
        return OpenAILLMClient(api_key=api_key, model=model or "gpt-4o")
    if provider == "mock":
        return MockLLMClient()
    # Default to MockLLMClient if no keys are found in environment
    return MockLLMClient()
