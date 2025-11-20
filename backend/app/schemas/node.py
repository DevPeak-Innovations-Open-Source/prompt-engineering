"""
Node schemas for workflow nodes
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum


class NodeType(str, Enum):
    """Supported node types"""
    HTTP_REQUEST = "http_request"
    DELAY = "delay"
    CONDITION = "condition"
    PYTHON_CODE = "python_code"
    LLM = "llm"


class NodeConfig(BaseModel):
    """Base configuration for a node"""
    type: NodeType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    

class HTTPNodeConfig(BaseModel):
    """HTTP Request node configuration"""
    url: str
    method: str = "GET"
    headers: Dict[str, str] = Field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    timeout: int = 30


class DelayNodeConfig(BaseModel):
    """Delay node configuration"""
    seconds: float = Field(gt=0, description="Delay duration in seconds")


class ConditionNodeConfig(BaseModel):
    """Condition node configuration"""
    field: str = Field(description="Field to evaluate from input data")
    operator: str = Field(description="Comparison operator: ==, !=, >, <, >=, <=, contains, in")
    value: Any = Field(description="Value to compare against")
    true_branch: Optional[str] = Field(None, description="Node ID to execute if condition is true")
    false_branch: Optional[str] = Field(None, description="Node ID to execute if condition is false")


class PythonNodeConfig(BaseModel):
    """Python Code node configuration"""
    code: str = Field(description="Python code to execute")
    timeout: int = Field(default=30, description="Execution timeout in seconds")


class LLMNodeConfig(BaseModel):
    """LLM node configuration"""
    prompt: str = Field(description="Prompt template (can use {variables} from input)")
    model: Optional[str] = Field(None, description="Model to use (overrides config default)")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, gt=0)
    system_message: Optional[str] = None


class NodeSchema(BaseModel):
    """Complete node schema"""
    id: str = Field(description="Unique node identifier within workflow")
    name: str = Field(description="Human-readable node name")
    type: NodeType
    config: Dict[str, Any] = Field(description="Node-specific configuration")
    next_nodes: List[str] = Field(default_factory=list, description="IDs of nodes to execute next")
    on_error: Optional[str] = Field(None, description="Node ID to execute on error")


class NodeExecutionResult(BaseModel):
    """Result of a node execution"""
    node_id: str
    status: str  # "success", "error", "skipped"
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float  # seconds
    next_nodes: List[str] = Field(default_factory=list)

