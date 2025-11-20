"""
Workflow API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from ..storage.db import get_session
from ..storage import crud_workflow, crud_logs
from ..schemas.workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    WorkflowExecuteRequest,
    WorkflowExecutionResponse,
    WorkflowGenerateRequest,
    WorkflowListResponse
)
from ..orchestrator.engine import WorkflowEngine
from ..llm.generator import WorkflowGenerator
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])


@router.post("/", response_model=WorkflowResponse, status_code=201)
async def create_workflow(
    workflow: WorkflowCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new workflow"""
    try:
        # Validate workflow structure
        engine = WorkflowEngine()
        
        # Create temporary workflow response for validation
        temp_workflow = WorkflowResponse(
            id="temp",
            name=workflow.name,
            description=workflow.description,
            nodes=workflow.nodes,
            start_node=workflow.start_node,
            trigger_config=workflow.trigger_config,
            is_active=True,
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00"
        )
        
        is_valid, error = engine.validate_workflow(temp_workflow)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid workflow: {error}")
        
        # Create workflow in database
        created_workflow = await crud_workflow.create_workflow(session, workflow)
        logger.info(f"Workflow created: {created_workflow.id}")
        return created_workflow
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=WorkflowListResponse)
async def list_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    session: AsyncSession = Depends(get_session)
):
    """List all workflows"""
    try:
        workflows = await crud_workflow.list_workflows(session, skip, limit, active_only)
        total = await crud_workflow.count_workflows(session, active_only)
        
        return WorkflowListResponse(
            workflows=workflows,
            total=total,
            page=skip // limit + 1,
            page_size=limit
        )
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get a workflow by ID"""
    workflow = await crud_workflow.get_workflow(session, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    workflow_update: WorkflowUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update a workflow"""
    try:
        updated_workflow = await crud_workflow.update_workflow(session, workflow_id, workflow_update)
        if not updated_workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        logger.info(f"Workflow updated: {workflow_id}")
        return updated_workflow
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(
    workflow_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Delete a workflow"""
    deleted = await crud_workflow.delete_workflow(session, workflow_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    logger.info(f"Workflow deleted: {workflow_id}")
    return None


@router.post("/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    execute_request: WorkflowExecuteRequest,
    session: AsyncSession = Depends(get_session)
):
    """Execute a workflow"""
    try:
        # Get workflow
        workflow = await crud_workflow.get_workflow(session, execute_request.workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        if not workflow.is_active:
            raise HTTPException(status_code=400, detail="Workflow is not active")
        
        # Execute workflow
        engine = WorkflowEngine()
        state = await engine.execute_workflow(workflow, execute_request.input_data)
        
        # Save execution log
        await crud_logs.create_execution_log(session, state)
        
        # Convert state to response
        response = WorkflowExecutionResponse(
            execution_id=state.execution_id,
            workflow_id=state.workflow_id,
            status=state.status.value,
            start_time=state.start_time,
            end_time=state.end_time,
            output=state.output_data,
            error=state.error,
            node_results=state.node_results
        )
        
        logger.info(f"Workflow executed: {execute_request.workflow_id}, status: {state.status.value}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}/executions")
async def list_workflow_executions(
    workflow_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session)
):
    """List execution logs for a workflow"""
    try:
        logs = await crud_logs.list_execution_logs(session, workflow_id, skip, limit)
        total = await crud_logs.count_execution_logs(session, workflow_id)
        
        return {
            "executions": [log.to_dict() for log in logs],
            "total": total,
            "page": skip // limit + 1,
            "page_size": limit
        }
    except Exception as e:
        logger.error(f"Error listing executions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executions/{execution_id}")
async def get_execution(
    execution_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get execution log by ID"""
    log = await crud_logs.get_execution_log(session, execution_id)
    if not log:
        raise HTTPException(status_code=404, detail="Execution not found")
    return log.to_dict()


@router.post("/generate", response_model=WorkflowResponse, status_code=201)
async def generate_workflow(
    generate_request: WorkflowGenerateRequest,
    session: AsyncSession = Depends(get_session)
):
    """Generate a workflow using AI from natural language description"""
    try:
        # Generate workflow using LLM
        generator = WorkflowGenerator()
        workflow_create = await generator.generate_workflow(
            generate_request.description,
            generate_request.context
        )
        
        # Validate generated workflow
        engine = WorkflowEngine()
        temp_workflow = WorkflowResponse(
            id="temp",
            name=workflow_create.name,
            description=workflow_create.description,
            nodes=workflow_create.nodes,
            start_node=workflow_create.start_node,
            trigger_config=workflow_create.trigger_config,
            is_active=True,
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00"
        )
        
        is_valid, error = engine.validate_workflow(temp_workflow)
        if not is_valid:
            raise HTTPException(
                status_code=500,
                detail=f"Generated workflow is invalid: {error}"
            )
        
        # Save workflow
        created_workflow = await crud_workflow.create_workflow(session, workflow_create)
        logger.info(f"AI-generated workflow created: {created_workflow.id}")
        return created_workflow
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate workflow: {str(e)}")

