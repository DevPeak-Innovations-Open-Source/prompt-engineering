"""
Workflow database model
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer
from sqlalchemy.sql import func
from ..storage.db import Base
import json


class WorkflowModel(Base):
    """Workflow database model"""
    
    __tablename__ = "workflows"
    
    id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    nodes = Column(Text, nullable=False)  # JSON string
    start_node = Column(String(255), nullable=False)
    trigger_config = Column(Text, nullable=True)  # JSON string
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Workflow(id={self.id}, name={self.name})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "nodes": json.loads(self.nodes) if self.nodes else [],
            "start_node": self.start_node,
            "trigger_config": json.loads(self.trigger_config) if self.trigger_config else None,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

