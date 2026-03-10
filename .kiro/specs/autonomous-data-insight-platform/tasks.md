# Implementation Plan: Autonomous Data-to-Insight Platform

## Overview

This implementation plan breaks down the autonomous data-to-insight platform into discrete coding tasks. The system will be built using Python with LangGraph for orchestration, E2B for sandboxed execution, and MCP for data ingestion. All tasks build incrementally, with property-based tests integrated throughout to validate correctness properties early.

## Tasks

- [ ] 1. Project setup and core infrastructure
  - Create project directory structure (src/, tests/, config/)
  - Set up Python virtual environment and dependencies (langgraph, e2b, pandas, hypothesis, pytest)
  - Create configuration files (pyproject.toml, pytest.ini)
  - Initialize logging infrastructure
  - _Requirements: All (foundational)_

- [ ] 2. Define LangGraph state schema and data models
  - [ ] 2.1 Create core data models
    - Implement FileMetadata, ExecutionRecord, ErrorInfo, ValidationResult dataclasses
    - Implement ETLResult, VisualizationResult, QueryResult dataclasses
    - Add type hints and validation logic
    - _Requirements: 10.1, 10.2_
  
  - [ ] 2.2 Define PlatformState TypedDict for LangGraph
    - Create PlatformState with all required fields (user_query, uploaded_files, semantic_profile, etc.)
    - Add state transition helper functions
    - _Requirements: 10.1, 10.3, 10.4_
  
  - [ ]* 2.3 Write property test for state persistence
    - **Property 28: State Persistence Across Session Interactions**
    - **Validates: Requirements 10.4**

- [ ] 3. Implement E2B sandbox wrapper with retry loop
  - [ ] 3.1 Create E2BSandboxWrapper class
    - Implement execute_code() method with E2B SDK integration
    - Implement get_available_libraries() method
    - Add execution timeout and memory limit configuration
    - Handle artifact extraction (files, figures, data structures)
    - _Requirements: 1.1, 1.2, 1.4_
  
  - [ ]* 3.2 Write property test for successful execution
    - **Property 1: Successful Execution Returns Results and Artifacts**
    - **Validates: Requirements 1.2**
  
  - [ ]* 3.3 Write property test for error traceback capture
    - **Property 2: Failed Execution Captures Complete Traceback**
    - **Validates: Requirements 1.3**
  
  - [ ] 3.4 Implement RetryLoop class
    - Create execute_with_retry() method with configurable max_retries
    - Implement error feedback mechanism to agents
    - Add escalation logic when retries exhausted
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ]* 3.5 Write property test for retry loop bounded execution
    - **Property 3: Retry Loop Bounded Execution**
    - **Validates: Requirements 2.4, 2.5**
  
  - [ ]* 3.6 Write property test for retry loop error feedback
    - **Property 4: Retry Loop Error Feedback**
    - **Validates: Requirements 2.1, 2.2, 2.3**

- [ ] 4. Checkpoint - Ensure E2B integration works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement MCP integration stubs
  - [ ] 5.1 Create MCPFileParser class
    - Implement detect_format() with heuristics for CSV, JSON, Excel, Parquet, XML
    - Implement parse_file() returning pandas DataFrame
    - Add error handling for unsupported/corrupted files
    - _Requirements: 4.1, 4.3, 4.4, 4.5_
  
  - [ ]* 5.2 Write property test for format detection
    - **Property 6: File Format Detection Accuracy**
    - **Validates: Requirements 4.3**
  
  - [ ]* 5.3 Write property test for successful parsing
    - **Property 7: Successful Parsing Produces Structured Data**
    - **Validates: Requirements 4.4**
  
  - [ ]* 5.4 Write property test for parse error handling
    - **Property 8: Parse Failures Return Descriptive Errors**
    - **Validates: Requirements 4.5**
  
  - [ ] 5.5 Create MCPSQLInterface class
    - Implement connect() for database connections
    - Implement execute_query() routing through MCP
    - Implement get_schema() for database introspection
    - Add read-only access enforcement
    - _Requirements: 4.2, 9.1, 9.2_

- [ ] 6. Implement Planner Agent
  - [ ] 6.1 Create PlannerAgent class
    - Implement generate_semantic_profile() method
    - Generate column info, data types, statistics, sample values
    - _Requirements: 6.1_
  
  - [ ]* 6.2 Write property test for semantic profile completeness
    - **Property 12: Semantic Profile Generation Completeness**
    - **Validates: Requirements 6.1**
  
  - [ ] 6.3 Implement validate_query() method
    - Check column existence, operation compatibility, data sufficiency
    - Return ValidationResult with approval status and reason
    - _Requirements: 6.2, 6.3, 6.4_
  
  - [ ]* 6.4 Write property test for infeasible query rejection
    - **Property 14: Infeasible Query Rejection with Explanation**
    - **Validates: Requirements 6.3**
  
  - [ ]* 6.5 Write property test for feasible query approval
    - **Property 15: Feasible Query Approval**
    - **Validates: Requirements 6.4**
  
  - [ ]* 6.6 Write property test for validation before code generation
    - **Property 13: Query Validation Precedes Code Generation**
    - **Validates: Requirements 6.5**

- [ ] 7. Implement Data Agent
  - [ ] 7.1 Create DataAgent class
    - Implement create_working_copy() for immutable data handling
    - Implement generate_etl_code() for type enforcement and imputation
    - Integrate with E2B sandbox for code execution
    - _Requirements: 3.1, 3.2, 7.1, 7.2, 7.3_
  
  - [ ]* 7.2 Write property test for data immutability
    - **Property 5: Data Immutability Through Transformations**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
  
  - [ ]* 7.3 Write property test for ETL type enforcement code generation
    - **Property 16: ETL Code Generation for Type Enforcement**
    - **Validates: Requirements 7.1**
  
  - [ ]* 7.4 Write property test for ETL missing value imputation
    - **Property 17: ETL Code Generation for Missing Value Imputation**
    - **Validates: Requirements 7.2**
  
  - [ ] 7.5 Implement execute_etl() method
    - Execute ETL code in E2B sandbox with retry loop integration
    - Return ETLResult with transformed data and operations applied
    - _Requirements: 7.3, 7.4, 7.5_
  
  - [ ]* 7.6 Write property test for successful ETL return
    - **Property 19: Successful ETL Returns Cleaned Data**
    - **Validates: Requirements 7.4**
  
  - [ ]* 7.7 Write property test for failed operations triggering retry
    - **Property 20: Failed Operations Trigger Retry**
    - **Validates: Requirements 7.5, 8.4**

- [ ] 8. Implement Visualization Expert
  - [ ] 8.1 Create VisualizationExpert class
    - Implement generate_viz_code() for matplotlib, seaborn, plotly
    - Support line plots, scatter plots, bar charts, heatmaps, time series
    - _Requirements: 8.1_
  
  - [ ]* 8.2 Write property test for approved library usage
    - **Property 21: Visualization Code Uses Approved Libraries**
    - **Validates: Requirements 8.1**
  
  - [ ] 8.3 Implement execute_visualization() method
    - Execute visualization code in E2B sandbox
    - Extract chart artifacts (PNG, SVG, Plotly JSON)
    - Return VisualizationResult with chart data and metadata
    - _Requirements: 8.2, 8.3_
  
  - [ ]* 8.4 Write property test for chart extraction
    - **Property 22: Successful Visualization Extracts Chart**
    - **Validates: Requirements 8.3**
  
  - [ ]* 8.5 Write property test for output format validity
    - **Property 23: Visualization Output Format Validity**
    - **Validates: Requirements 8.5**

- [ ] 9. Implement SQL Agent
  - [ ] 9.1 Create SQLAgent class
    - Implement execute_query() routing through MCPSQLInterface
    - Implement validate_sql() for syntax checking
    - Add query timeout and result size limits
    - _Requirements: 9.1, 9.2_
  
  - [ ]* 9.2 Write property test for MCP routing
    - **Property 24: SQL Queries Route Through MCP**
    - **Validates: Requirements 9.1**
  
  - [ ]* 9.3 Write property test for successful query result
    - **Property 25: Successful SQL Query Returns Result Set**
    - **Validates: Requirements 9.3**
  
  - [ ]* 9.4 Write property test for failed query error message
    - **Property 26: Failed SQL Query Returns Error Message**
    - **Validates: Requirements 9.4**

- [ ] 10. Checkpoint - Ensure all agents work independently
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Implement Supervisor Agent and LangGraph orchestration
  - [ ] 11.1 Create SupervisorAgent class
    - Implement route_request() with routing logic (Planner → Data/Viz/SQL)
    - Implement update_state() for state transitions
    - Implement is_complete() for workflow completion detection
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ]* 11.2 Write property test for exactly-one-agent routing
    - **Property 9: Supervisor Routes to Exactly One Agent**
    - **Validates: Requirements 5.4**
  
  - [ ]* 11.3 Write property test for state updates on completion
    - **Property 10: State Updates on Agent Completion**
    - **Validates: Requirements 5.3, 10.2**
  
  - [ ]* 11.4 Write property test for workflow completion
    - **Property 11: Workflow Completion Returns Result**
    - **Validates: Requirements 5.5**
  
  - [ ] 11.5 Build LangGraph state machine
    - Define state nodes for each agent (planner, data, visualization, sql)
    - Define conditional edges based on routing logic
    - Add error handling and escalation paths
    - _Requirements: 10.1, 10.2, 10.3, 10.4_
  
  - [ ]* 11.6 Write property test for context provision
    - **Property 27: Context Provision on Agent Request**
    - **Validates: Requirements 10.3**

- [ ] 12. Implement error handling infrastructure
  - [ ] 12.1 Create ErrorRecoveryStrategy class
    - Implement handle_execution_error() with recovery action determination
    - Add strategies for syntax errors, resource constraints, data issues
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ] 12.2 Add error context preservation
    - Implement ErrorContext dataclass with full debugging information
    - Add logging for system monitoring
    - Store execution history for audit
    - _Requirements: 1.3, 2.1_
  
  - [ ] 12.3 Implement session cleanup
    - Add cleanup logic for temporary resources on session termination
    - Clean up E2B sandbox instances, working copies, transient state
    - _Requirements: 10.5_
  
  - [ ]* 12.4 Write property test for session cleanup
    - **Property 29: Session Cleanup on Termination**
    - **Validates: Requirements 10.5**

- [ ] 13. Implement agent code execution isolation property test
  - [ ]* 13.1 Write property test for execution isolation
    - **Property 18: Agent Code Execution Isolation**
    - **Validates: Requirements 7.3, 8.2**

- [ ] 14. Integration and end-to-end wiring
  - [ ] 14.1 Wire all components together
    - Connect Supervisor to all agents
    - Connect agents to E2B sandbox wrapper
    - Connect agents to MCP interfaces
    - Integrate retry loop with all code-generating agents
    - _Requirements: All_
  
  - [ ] 14.2 Create main entry point
    - Implement main workflow orchestration function
    - Add session management and initialization
    - Add configuration loading
    - _Requirements: 5.1, 10.1_
  
  - [ ]* 14.3 Write integration test for file upload → ETL workflow
    - Test: Upload CSV → Parse → Validate → ETL → Return cleaned data
    - _Requirements: 3.1, 3.2, 4.1, 6.1, 7.1, 7.4_
  
  - [ ]* 14.4 Write integration test for visualization workflow
    - Test: Upload file → Parse → Validate → Visualization → Return chart
    - _Requirements: 4.1, 6.1, 8.1, 8.3, 8.5_
  
  - [ ]* 14.5 Write integration test for SQL workflow
    - Test: Connect database → SQL query → Return results
    - _Requirements: 4.2, 9.1, 9.2, 9.3_
  
  - [ ]* 14.6 Write integration test for validation failure
    - Test: Upload file → Parse → Validation failure → Reject with explanation
    - _Requirements: 6.2, 6.3_
  
  - [ ]* 14.7 Write integration test for retry success
    - Test: Upload file → Parse → Validate → ETL failure → Retry → Success
    - _Requirements: 2.1, 2.2, 2.3, 7.5_
  
  - [ ]* 14.8 Write integration test for retry exhaustion
    - Test: Upload file → Parse → Validate → ETL failure → Retry exhaustion → Escalate
    - _Requirements: 2.4, 2.5_

- [ ] 15. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property-based tests use the `hypothesis` library with minimum 100 iterations
- All code execution happens in E2B sandboxes for security isolation
- Original data files remain immutable throughout all operations
- The retry loop provides automatic error recovery for transient failures
- Integration tests validate end-to-end workflows across multiple components
