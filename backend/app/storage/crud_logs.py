"""
CRUD operations for execution logs
"""
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.log_model import ExecutionLogModel
from ..orchestrator.state import WorkflowExecutionState
from typing import List, Optional
import json
import logging

logger = logging.getLogger(__name__)


async def create_execution_log(session: AsyncSession, state: WorkflowExecutionState) -> ExecutionLogModel:
    """Create execution log from workflow state"""
    execution_time = None
    if state.start_time and state.end_time:
        execution_time = (state.end_time - state.start_time).total_seconds()
    
    db_log = ExecutionLogModel(
        id=state.execution_id,
        workflow_id=state.workflow_id,
        status=state.status.value,
        start_time=state.start_time,
        end_time=state.end_time,
        input_data=json.dumps(state.input_data) if state.input_data else None,
        output_data=json.dumps(state.output_data) if state.output_data else None,
        error=state.error,
        node_results=json.dumps(state.node_results) if state.node_results else None,
        execution_time=execution_time
    )
    
    session.add(db_log)
    await session.commit()
    await session.refresh(db_log)
    
    logger.info(f"Created execution log: {state.execution_id}")
    return db_log


async def get_execution_log(session: AsyncSession, execution_id: str) -> Optional[ExecutionLogModel]:
    """Get execution log by ID"""
    result = await session.execute(
        select(ExecutionLogModel).where(ExecutionLogModel.id == execution_id)
    )
    return result.scalar_one_or_none()


async def list_execution_logs(
    session: AsyncSession,
    workflow_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[ExecutionLogModel]:
    """List execution logs with optional workflow filter"""
    query = select(ExecutionLogModel)
    
    if workflow_id:
        query = query.where(ExecutionLogModel.workflow_id == workflow_id)
    
    query = query.offset(skip).limit(limit).order_by(ExecutionLogModel.created_at.desc())
    
    result = await session.execute(query)
    return list(result.scalars().all())


async def delete_execution_logs(
    session: AsyncSession,
    workflow_id: Optional[str] = None,
    older_than_days: Optional[int] = None
) -> int:
    """Delete execution logs with optional filters"""
    query = delete(ExecutionLogModel)
    
    if workflow_id:
        query = query.where(ExecutionLogModel.workflow_id == workflow_id)
    
    if older_than_days:
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
        query = query.where(ExecutionLogModel.created_at < cutoff_date)
    
    result = await session.execute(query)
    await session.commit()
    
    deleted_count = result.rowcount
    logger.info(f"Deleted {deleted_count} execution logs")
    return deleted_count


async def count_execution_logs(
    session: AsyncSession,
    workflow_id: Optional[str] = None
) -> int:
    """Count execution logs"""
    from sqlalchemy import func
    
    query = select(func.count(ExecutionLogModel.id))
    
    if workflow_id:
        query = query.where(ExecutionLogModel.workflow_id == workflow_id)
    
    result = await session.execute(query)
    return result.scalar()

