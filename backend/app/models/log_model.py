"""
Execution log database model
"""
from sqlalchemy import Column, String, Text, DateTime, Float
from sqlalchemy.sql import func
from ..storage.db import Base
import json


class ExecutionLogModel(Base):
    """Execution log database model"""
    
    __tablename__ = "execution_logs"
    
    id = Column(String, primary_key=True)  # execution_id
    workflow_id = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    input_data = Column(Text, nullable=True)  # JSON string
    output_data = Column(Text, nullable=True)  # JSON string
    error = Column(Text, nullable=True)
    node_results = Column(Text, nullable=True)  # JSON string
    execution_time = Column(Float, nullable=True)  # seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<ExecutionLog(id={self.id}, workflow_id={self.workflow_id}, status={self.status})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "execution_id": self.id,
            "workflow_id": self.workflow_id,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "input_data": json.loads(self.input_data) if self.input_data else None,
            "output_data": json.loads(self.output_data) if self.output_data else None,
            "error": self.error,
            "node_results": json.loads(self.node_results) if self.node_results else [],
            "execution_time": self.execution_time,
            "created_at": self.created_at
        }

