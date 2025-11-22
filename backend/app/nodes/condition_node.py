"""
Condition Node - Handles conditional branching in a workflow.

Purpose:
---------
This node decides which path (true or false) a workflow should take next
based on evaluating a specific condition defined in the workflow configuration.

Example use case:
-----------------
If a workflow receives an API response and you want to check if the
status code == 200, then:
- If true → continue to success branch
- If false → go to error handler branch
"""

import logging
from typing import Dict, Any
from .base import BaseNode, NodeExecutionContext
from app.schemas.node import ConditionNodeConfig  # for schema validation

# Initialize logger for better debugging and monitoring
logger = logging.getLogger(__name__)


class ConditionNode(BaseNode):
    """
    A workflow node that performs conditional evaluation.
    
    This class inherits from BaseNode which provides:
    - Core execution control (timing, error handling, etc.)
    - Shared context support between nodes
    """

    def __init__(self, node_id: str, name: str, config: Dict[str, Any]):
        """
        Constructor that sets up and validates the node configuration.

        Args:
            node_id (str): Unique identifier for the node.
            name (str): Human-readable name of the node.
            config (dict): Configuration parameters for the condition node.

        On initialization:
            - Calls parent constructor.
            - Validates configuration using Pydantic schema.
              This ensures required keys like 'field' and 'operator' exist.
        """
        # Initialize the parent BaseNode
        super().__init__(node_id, name, config)

        # Validate config using Pydantic schema (ConditionNodeConfig)
        # This ensures proper keys and value types (like operator, field, etc.)
        ConditionNodeConfig(**config)

    async def execute(self, input_data: Dict[str, Any], context: NodeExecutionContext) -> Dict[str, Any]:
        """
        Executes the condition logic and decides which branch to follow.

        Args:
            input_data (dict): The data passed from the previous node.
            context (NodeExecutionContext): Execution context shared across workflow.

        Config Parameters (defined in node config):
            - field (str): Key or nested path to check (e.g., 'user.age').
            - operator (str): Comparison operator (==, !=, >, <, >=, <=, contains, in).
            - value (Any): Value to compare against.
            - true_branch (str): Next node ID if condition is True.
            - false_branch (str): Next node ID if condition is False.

        Returns:
            dict: Input data + condition evaluation metadata (_condition_result).
        """
        # Extract configuration values
        field = self.config.get("field")
        operator = self.config.get("operator")
        compare_value = self.config.get("value")
        true_branch = self.config.get("true_branch")
        false_branch = self.config.get("false_branch")

        # Basic validation check for required parameters
        if not field or not operator:
            raise ValueError("'field' and 'operator' are required for Condition node")

        # Extract the field value from input_data (supports nested access like 'user.profile.age')
        field_value = self._get_nested_field(input_data, field)

        # Perform condition evaluation
        result = self._evaluate_condition(field_value, operator, compare_value)

        # Log condition details for debugging
        logger.info(
            f"[Workflow: {context.workflow_id} | Node: {self.node_id}] "
            f"Evaluating condition → {field}={field_value} {operator} {compare_value} → Result: {result}"
        )

        # Based on evaluation result, set which node(s) to execute next
        if result and true_branch:
            self.next_nodes = [true_branch]
        elif not result and false_branch:
            self.next_nodes = [false_branch]
        else:
            self.next_nodes = []  # End of branch if no match

        # Return input data along with evaluation metadata
        return {
            **input_data,
            "_condition_result": {
                "field": field,
                "field_value": field_value,
                "operator": operator,
                "compare_value": compare_value,
                "result": result,
                "next_branch": true_branch if result else false_branch,
                "node_id": self.node_id
            }
        }

    def _get_nested_field(self, data: Dict[str, Any], field_path: str) -> Any:
        """
        Helper function to access nested fields from input data using dot notation.

        Example:
            field_path = "user.profile.age"
            data = {"user": {"profile": {"age": 25}}}
            → returns 25

        If any level of the field path doesn’t exist, it returns None.
        """
        keys = field_path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None  # Stop traversal if the structure breaks
        return value

    def _evaluate_condition(self, field_value: Any, operator: str, compare_value: Any) -> bool:
        """
        Core logic for evaluating the condition based on the operator.

        Supported operators:
        ---------------------
        - Equality: ==, !=
        - Numeric comparisons: >, <, >=, <=
        - Collection checks: contains, in

        Args:
            field_value: The actual value extracted from input data.
            operator: Comparison operator as string.
            compare_value: Value to compare against.

        Returns:
            bool: True if the condition passes, False otherwise.
        """
        try:
            # Define all supported operations as inline lambdas
            operations = {
                "==": lambda a, b: a == b,
                "!=": lambda a, b: a != b,
                ">": lambda a, b: a > b,
                "<": lambda a, b: a < b,
                ">=": lambda a, b: a >= b,
                "<=": lambda a, b: a <= b,
                "contains": lambda a, b: b in a if isinstance(a, (list, str, dict)) else False,
                "in": lambda a, b: a in b if isinstance(b, (list, str, dict)) else False,
            }

            # Validate the operator
            if operator not in operations:
                raise ValueError(f"Unsupported operator: {operator}")

            # Evaluate the condition
            return operations[operator](field_value, compare_value)

        except Exception as e:
            # Log detailed error for better debugging
            logger.error(
                f"[Node: {self.node_id}] Error evaluating condition → "
                f"({field_value} {operator} {compare_value}): {e}"
            )
            # Default to False to ensure workflow stability
            return False
