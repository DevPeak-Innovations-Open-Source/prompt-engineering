"""
Condition Node - Conditional branching in workflows
"""
from typing import Dict, Any, List
from .base import BaseNode, NodeExecutionContext
import logging

logger = logging.getLogger(__name__)


class ConditionNode(BaseNode):
    """Node for conditional branching"""
    
    async def execute(self, input_data: Dict[str, Any], context: NodeExecutionContext) -> Dict[str, Any]:
        """
        Execute condition evaluation
        
        Config parameters:
        - field: Field name to evaluate (supports nested with dot notation)
        - operator: Comparison operator (==, !=, >, <, >=, <=, contains, in)
        - value: Value to compare against
        - true_branch: Node ID to execute if true
        - false_branch: Node ID to execute if false
        """
        field = self.config.get("field")
        operator = self.config.get("operator")
        compare_value = self.config.get("value")
        true_branch = self.config.get("true_branch")
        false_branch = self.config.get("false_branch")
        
        if not field or not operator:
            raise ValueError("'field' and 'operator' are required for Condition node")
        
        # Get field value from input data (supports nested fields with dot notation)
        field_value = self._get_nested_field(input_data, field)
        
        # Evaluate condition
        result = self._evaluate_condition(field_value, operator, compare_value)
        
        logger.info(f"Condition evaluation: {field}={field_value} {operator} {compare_value} = {result}")
        
        # Update next nodes based on condition result
        if result and true_branch:
            self.next_nodes = [true_branch]
        elif not result and false_branch:
            self.next_nodes = [false_branch]
        else:
            self.next_nodes = []
        
        return {
            **input_data,
            "_condition_result": {
                "field": field,
                "field_value": field_value,
                "operator": operator,
                "compare_value": compare_value,
                "result": result,
                "next_branch": true_branch if result else false_branch
            }
        }
    
    def _get_nested_field(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get nested field value using dot notation"""
        keys = field_path.split(".")
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
                
        return value
    
    def _evaluate_condition(self, field_value: Any, operator: str, compare_value: Any) -> bool:
        """Evaluate the condition"""
        try:
            if operator == "==":
                return field_value == compare_value
            elif operator == "!=":
                return field_value != compare_value
            elif operator == ">":
                return field_value > compare_value
            elif operator == "<":
                return field_value < compare_value
            elif operator == ">=":
                return field_value >= compare_value
            elif operator == "<=":
                return field_value <= compare_value
            elif operator == "contains":
                return compare_value in field_value
            elif operator == "in":
                return field_value in compare_value
            else:
                raise ValueError(f"Unsupported operator: {operator}")
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False

