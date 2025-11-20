"""
Workflow schemas
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from .node import NodeSchema


class WorkflowCreate(BaseModel):
    """Schema for creating a workflow"""
    name: str = Field(description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    nodes: List[NodeSchema] = Field(description="List of nodes in the workflow")
    start_node: str = Field(description="ID of the starting node")
    trigger_config: Optional[Dict[str, Any]] = Field(None, description="Trigger configuration")


class WorkflowUpdate(BaseModel):
    """Schema for updating a workflow"""
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: Optional[List[NodeSchema]] = None
    start_node: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class WorkflowResponse(BaseModel):
    """Schema for workflow response"""
    id: str
    name: str
    description: Optional[str] = None
    nodes: List[NodeSchema]
    start_node: str
    trigger_config: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class WorkflowExecuteRequest(BaseModel):
    """Schema for workflow execution request"""
    workflow_id: str
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Initial input data")


class WorkflowExecutionResponse(BaseModel):
    """Schema for workflow execution response"""
    execution_id: str
    workflow_id: str
    status: str  # "running", "completed", "failed"
    start_time: datetime
    end_time: Optional[datetime] = None
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    node_results: List[Dict[str, Any]] = Field(default_factory=list)


class WorkflowGenerateRequest(BaseModel):
    """Schema for AI-generated workflow request"""
    description: str = Field(description="Natural language description of desired workflow")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for generation")


class WorkflowListResponse(BaseModel):
    """Schema for workflow list response"""
    workflows: List[WorkflowResponse]
    total: int
    page: int
    page_size: int

