import pytest
from backend.core.schema_parser import TableMetadata, ColumnMetadata
from backend.agents.adk.domain_agent_factory import create_domain_agent

def test_domain_agent_factory_initialization():
    tables = [
        TableMetadata(name="users", domain="Users", columns=[ColumnMetadata(name="id", type="int")]),
        TableMetadata(name="profiles", domain="Users", columns=[ColumnMetadata(name="user_id", type="int")])
    ]
    
    agent = create_domain_agent("gemini-1.5-flash", "Users", tables)
    
    # Agent should be a SequentialAgent
    assert agent.name == "SqlSequenceWorkflow_Users"
    
    # Check that the planner inside the sequence agent has constraints
    planner = agent.sub_agents[0]
    assert planner.name == "SqlPlanner_Users"
    assert "users, profiles" in planner.instruction
    assert "specialized agent for the 'Users' domain" in planner.instruction
