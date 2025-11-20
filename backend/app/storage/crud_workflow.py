"""
CRUD operations for workflows
"""
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.workflow_model import WorkflowModel
from ..schemas.workflow import WorkflowCreate, WorkflowUpdate, WorkflowResponse
from ..schemas.node import NodeSchema
from typing import List, Optional
import json
import uuid
import logging

logger = logging.getLogger(__name__)


async def create_workflow(session: AsyncSession, workflow: WorkflowCreate) -> WorkflowResponse:
    """Create a new workflow"""
    workflow_id = str(uuid.uuid4())
    
    # Convert nodes to JSON
    nodes_json = json.dumps([node.model_dump() for node in workflow.nodes])
    trigger_config_json = json.dumps(workflow.trigger_config) if workflow.trigger_config else None
    
    db_workflow = WorkflowModel(
        id=workflow_id,
        name=workflow.name,
        description=workflow.description,
        nodes=nodes_json,
        start_node=workflow.start_node,
        trigger_config=trigger_config_json,
        is_active=True
    )
    
    session.add(db_workflow)
    await session.commit()
    await session.refresh(db_workflow)
    
    logger.info(f"Created workflow: {workflow_id}")
    return _model_to_response(db_workflow)


async def get_workflow(session: AsyncSession, workflow_id: str) -> Optional[WorkflowResponse]:
    """Get a workflow by ID"""
    result = await session.execute(
        select(WorkflowModel).where(WorkflowModel.id == workflow_id)
    )
    db_workflow = result.scalar_one_or_none()
    
    if db_workflow:
        return _model_to_response(db_workflow)
    return None


async def list_workflows(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False
) -> List[WorkflowResponse]:
    """List workflows with pagination"""
    query = select(WorkflowModel)
    
    if active_only:
        query = query.where(WorkflowModel.is_active == True)
    
    query = query.offset(skip).limit(limit).order_by(WorkflowModel.created_at.desc())
    
    result = await session.execute(query)
    db_workflows = result.scalars().all()
    
    return [_model_to_response(wf) for wf in db_workflows]


async def update_workflow(
    session: AsyncSession,
    workflow_id: str,
    workflow_update: WorkflowUpdate
) -> Optional[WorkflowResponse]:
    """Update a workflow"""
    # Get existing workflow
    result = await session.execute(
        select(WorkflowModel).where(WorkflowModel.id == workflow_id)
    )
    db_workflow = result.scalar_one_or_none()
    
    if not db_workflow:
        return None
    
    # Update fields
    update_data = workflow_update.model_dump(exclude_unset=True)
    
    if "nodes" in update_data:
        update_data["nodes"] = json.dumps([node.model_dump() for node in update_data["nodes"]])
    
    if "trigger_config" in update_data and update_data["trigger_config"]:
        update_data["trigger_config"] = json.dumps(update_data["trigger_config"])
    
    for key, value in update_data.items():
        setattr(db_workflow, key, value)
    
    await session.commit()
    await session.refresh(db_workflow)
    
    logger.info(f"Updated workflow: {workflow_id}")
    return _model_to_response(db_workflow)


async def delete_workflow(session: AsyncSession, workflow_id: str) -> bool:
    """Delete a workflow"""
    result = await session.execute(
        delete(WorkflowModel).where(WorkflowModel.id == workflow_id)
    )
    await session.commit()
    
    deleted = result.rowcount > 0
    if deleted:
        logger.info(f"Deleted workflow: {workflow_id}")
    
    return deleted


async def count_workflows(session: AsyncSession, active_only: bool = False) -> int:
    """Count workflows"""
    from sqlalchemy import func
    
    query = select(func.count(WorkflowModel.id))
    
    if active_only:
        query = query.where(WorkflowModel.is_active == True)
    
    result = await session.execute(query)
    return result.scalar()


def _model_to_response(db_workflow: WorkflowModel) -> WorkflowResponse:
    """Convert database model to response schema"""
    nodes_data = json.loads(db_workflow.nodes)
    nodes = [NodeSchema(**node) for node in nodes_data]
    
    trigger_config = None
    if db_workflow.trigger_config:
        trigger_config = json.loads(db_workflow.trigger_config)
    
    return WorkflowResponse(
        id=db_workflow.id,
        name=db_workflow.name,
        description=db_workflow.description,
        nodes=nodes,
        start_node=db_workflow.start_node,
        trigger_config=trigger_config,
        is_active=db_workflow.is_active,
        created_at=db_workflow.created_at,
        updated_at=db_workflow.updated_at
    )

