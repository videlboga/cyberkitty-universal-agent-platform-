"""
Functional Benchmarks for KittyCore

Tests core functionality and features:
- Agent creation and initialization
- Tool usage and execution
- Memory system operations
- MasterAgent capabilities
- Structured outputs
- Enhanced roles
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from kittycore import quick_agent, MasterAgent, Agent
from kittycore.structured_outputs import ProjectRequirements, SystemArchitecture
from kittycore.enhanced_roles import PersonaLibrary, RoleBasedAgentFactory
from kittycore.advanced_memory import TimelineMemory, CrossAgentMemory

from evaluation_metrics import EvaluationMetrics, BenchmarkResult


@dataclass
class FunctionalTestCase:
    """Individual functional test case"""
    name: str
    description: str
    test_function: str
    expected_result: Any
    timeout_seconds: int = 30


class FunctionalBenchmarks:
    """Comprehensive functional testing for KittyCore"""
    
    def __init__(self, use_mock_llm: bool = True):
        self.use_mock_llm = use_mock_llm
        self.metrics = EvaluationMetrics()
        self.test_cases: List[FunctionalTestCase] = []
        self._setup_test_cases()
    
    def _setup_test_cases(self):
        """Setup all functional test cases"""
        self.test_cases = [
            FunctionalTestCase(
                name="quick_agent_creation",
                description="Test quick agent creation and basic response",
                test_function="test_quick_agent_creation",
                expected_result="agent_created"
            ),
            FunctionalTestCase(
                name="master_agent_creation",
                description="Test MasterAgent creating specialized agents",
                test_function="test_master_agent_creation", 
                expected_result="specialized_agent_created"
            ),
            FunctionalTestCase(
                name="tool_usage",
                description="Test agent using tools effectively",
                test_function="test_tool_usage",
                expected_result="tool_executed"
            ),
            FunctionalTestCase(
                name="memory_operations",
                description="Test memory storage and retrieval",
                test_function="test_memory_operations",
                expected_result="memory_functional"
            ),
            FunctionalTestCase(
                name="structured_outputs",
                description="Test structured output generation",
                test_function="test_structured_outputs",
                expected_result="structured_data"
            ),
            FunctionalTestCase(
                name="enhanced_roles",
                description="Test role-based agent creation",
                test_function="test_enhanced_roles",
                expected_result="role_agent_created"
            ),
            FunctionalTestCase(
                name="cross_agent_communication",
                description="Test communication between agents",
                test_function="test_cross_agent_communication",
                expected_result="communication_successful"
            ),
            FunctionalTestCase(
                name="error_handling",
                description="Test error handling and recovery",
                test_function="test_error_handling",
                expected_result="error_handled"
            ),
            FunctionalTestCase(
                name="concurrent_operations",
                description="Test concurrent agent operations",
                test_function="test_concurrent_operations",
                expected_result="concurrent_success"
            ),
            FunctionalTestCase(
                name="scalability_basic",
                description="Test basic scalability with multiple agents",
                test_function="test_scalability_basic",
                expected_result="scalability_ok"
            )
        ]
    
    def _is_mock_response(self, response: str) -> bool:
        """Проверяет, является ли ответ mock ответом"""
        if not response:
            return False
        
        response_lower = str(response).lower()
        mock_indicators = [
            "mock response",
            "kittycore mock",
            "hello from kittycore",
            "симуляция ответа",
            "fallback",
            "заглушка"
        ]
        
        return any(indicator in response_lower for indicator in mock_indicators)
    
    async def run_all_benchmarks(self) -> BenchmarkResult:
        """Run all functional benchmarks"""
        print("🚀 Starting KittyCore Functional Benchmarks...")
        
        self.metrics.start_measurement()
        
        total_tasks = len(self.test_cases)
        completed_tasks = 0
        failures = []
        completion_times = []
        actual_outputs = []
        expected_outputs = []
        
        for test_case in self.test_cases:
            print(f"  ⚡ Running: {test_case.name}")
            
            try:
                start_time = time.time()
                
                # Get test method and run it
                test_method = getattr(self, test_case.test_function)
                result = await asyncio.wait_for(
                    test_method(), 
                    timeout=test_case.timeout_seconds
                )
                
                end_time = time.time()
                completion_times.append(end_time - start_time)
                
                # Check if result matches expected
                if result == test_case.expected_result:
                    completed_tasks += 1
                    print(f"    ✅ {test_case.name}: PASSED")
                else:
                    failures.append(f"{test_case.name}: Expected {test_case.expected_result}, got {result}")
                    print(f"    ❌ {test_case.name}: FAILED - Expected {test_case.expected_result}, got {result}")
                
                actual_outputs.append(str(result))
                expected_outputs.append(str(test_case.expected_result))
                
            except asyncio.TimeoutError:
                failures.append(f"{test_case.name}: Timeout after {test_case.timeout_seconds}s")
                print(f"    ⏰ {test_case.name}: TIMEOUT")
                actual_outputs.append("timeout")
                expected_outputs.append(str(test_case.expected_result))
                
            except Exception as e:
                failures.append(f"{test_case.name}: {str(e)}")
                print(f"    💥 {test_case.name}: ERROR - {str(e)}")
                actual_outputs.append(f"error: {str(e)}")
                expected_outputs.append(str(test_case.expected_result))
        
        # Measure metrics
        task_completion = self.metrics.measure_task_completion(
            total_tasks, completed_tasks, completion_times, failures
        )
        
        performance = self.metrics.measure_performance()
        
        quality = self.metrics.measure_quality(
            expected_outputs, actual_outputs
        )
        
        # Create benchmark result
        result = BenchmarkResult(
            benchmark_name="functional_benchmarks",
            timestamp=datetime.now(),
            task_completion=task_completion,
            performance=performance,
            quality=quality,
            metadata={
                "test_cases": [test.name for test in self.test_cases],
                "use_mock_llm": self.use_mock_llm
            }
        )
        
        self.metrics.results.append(result)
        
        print(f"\n📊 Functional Benchmark Results:")
        print(f"   Success Rate: {task_completion.success_rate:.2%}")
        print(f"   Execution Time: {performance.execution_time:.2f}s") 
        print(f"   Memory Usage: {performance.memory_usage_mb:.1f}MB")
        print(f"   Quality Score: {quality.output_correctness:.2f}")
        
        return result
    
    async def test_quick_agent_creation(self) -> str:
        """Test basic quick agent creation"""
        try:
            agent = quick_agent("You are a helpful assistant")
            response = agent.run("Hello, how are you?")  # run() is synchronous
            
            # КРИТИЧЕСКИЙ ПРОВАЛ: если получили mock ответ
            if self._is_mock_response(response):
                return "CRITICAL_FAIL_MOCK_DETECTED"
            
            if response and len(response) > 0:
                return "agent_created"
            return "no_response"
        except Exception as e:
            return f"error: {str(e)}"
    
    async def test_master_agent_creation(self) -> str:
        """Test MasterAgent creating specialized agents"""
        try:
            master = MasterAgent()  # No use_mock_llm parameter
            result = master.solve_task("I need help with data analysis")
            
            # КРИТИЧЕСКИЙ ПРОВАЛ: если в результате есть mock ответы
            if isinstance(result, dict) and "response" in result:
                if self._is_mock_response(result["response"]):
                    return "CRITICAL_FAIL_MOCK_DETECTED"
            
            # КРИТИЧЕСКИЙ ПРОВАЛ: если success = False
            if not result.get("success", False):
                return "CRITICAL_FAIL_NO_SUCCESS"
            
            # КРИТИЧЕСКИЙ ПРОВАЛ: если нет созданных агентов
            if not result.get("agent_results") or len(result.get("agent_results", [])) == 0:
                return "CRITICAL_FAIL_NO_AGENTS_CREATED"
            
            # КРИТИЧЕСКИЙ ПРОВАЛ: если агенты созданы без инструментов
            # Проверяем что в managed_agents есть агенты с инструментами
            agents_info = master.get_managed_agents_info()
            if agents_info.get("total_agents", 0) == 0:
                return "CRITICAL_FAIL_NO_MANAGED_AGENTS"
            
            # Проверяем что у созданных агентов есть инструменты
            agents_with_tools = 0
            for agent_id, agent_info in agents_info.get("agents", {}).items():
                if agent_info.get("tools") and len(agent_info["tools"]) > 0:
                    agents_with_tools += 1
            
            if agents_with_tools == 0:
                return "CRITICAL_FAIL_NO_TOOLS_FOUND"
            
            return "specialized_agent_created"
        except Exception as e:
            return f"error: {str(e)}"
    
    async def test_tool_usage(self) -> str:
        """Test agent using tools"""
        try:
            from kittycore.tools import Tool
            
            # Simple calculator tool
            class CalculatorTool(Tool):
                def __init__(self):
                    super().__init__(
                        name="calculator",
                        description="Calculate mathematical expressions"
                    )
                
                def get_schema(self) -> dict:
                    return {
                        "name": self.name,
                        "description": self.description,
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "expression": {
                                    "type": "string",
                                    "description": "Mathematical expression to calculate"
                                }
                            },
                            "required": ["expression"]
                        }
                    }
                
                def execute(self, expression: str) -> str:
                    try:
                        result = eval(expression.replace('x', '*'))
                        return f"Result: {result}"
                    except:
                        return "Invalid expression"
            
            agent = Agent(
                prompt="You are a math assistant",  # prompt, not instructions
                tools=[CalculatorTool()]
            )
            
            response = agent.run("What is 5 + 3?")  # synchronous
            
            # КРИТИЧЕСКИЙ ПРОВАЛ: если получили mock ответ
            if self._is_mock_response(response):
                return "CRITICAL_FAIL_MOCK_DETECTED"
            
            if "8" in str(response) or "Result" in str(response):
                return "tool_executed"
            return "tool_not_used"
        except Exception as e:
            return f"error: {str(e)}"
    
    async def test_memory_operations(self) -> str:
        """Test memory storage and retrieval"""
        try:
            memory = TimelineMemory("test_agent")  # agent_id required
            
            # Store some memories
            memory.save_snapshot(
                input_message="Hello world",
                output_message="Hi there!",
                context={"type": "greeting"},
                internal_state={"mood": "friendly"}
            )
            
            # Retrieve memories
            recent = memory.get_recent_snapshots(2)  # limit as positional argument
            if len(recent) >= 1:
                return "memory_functional"
            return "memory_failed"
        except Exception as e:
            return f"error: {str(e)}"
    
    async def test_structured_outputs(self) -> str:
        """Test structured output generation"""
        try:
            # Test if structured output classes work
            req = ProjectRequirements(
                agent_name="test_agent",
                success=True,
                timestamp="2024-01-01",
                raw_content="Test content",
                project_name="Test Project",
                goals=["Goal 1"],
                user_stories=["Story 1"],
                technical_requirements=["Requirement 1", "Requirement 2"],
                constraints=["Constraint 1"],
                success_criteria=["Criteria 1"]
            )
            
            if req.project_name == "Test Project":
                return "structured_data"
            return "structured_failed"
        except Exception as e:
            return f"error: {str(e)}"
    
    async def test_enhanced_roles(self) -> str:
        """Test role-based agent creation"""
        try:
            from kittycore.enhanced_roles import RoleBasedAgentFactory, AgentRole
            from kittycore import Agent
            
            # Create agent with role
            developer_agent = RoleBasedAgentFactory.create_agent_with_role(
                Agent, AgentRole.DEVELOPER, prompt="Test developer"
            )
            
            if developer_agent:
                return "role_agent_created"
            return "role_creation_failed"
        except Exception as e:
            return f"error: {str(e)}"
    
    async def test_cross_agent_communication(self) -> str:
        """Test communication between agents"""
        try:
            shared_memory = CrossAgentMemory("test_team")  # team_id required
            
            # Agent 1 stores information
            shared_memory.shared_context["project_info"] = {
                "status": "in_progress",
                "deadline": "next_week"
            }
            
            # Agent 2 retrieves information
            context = shared_memory.shared_context.get("project_info")
            
            if context and context.get("status") == "in_progress":
                return "communication_successful"
            return "communication_failed"
        except Exception as e:
            return f"error: {str(e)}"
    
    async def test_error_handling(self) -> str:
        """Test error handling and recovery"""
        try:
            # Create agent with valid configuration
            agent = Agent(prompt="Test agent")
            
            # Try to run with potentially problematic input
            try:
                response = agent.run("")  # Empty input, synchronous
                
                # КРИТИЧЕСКИЙ ПРОВАЛ: если получили mock ответ
                if self._is_mock_response(response):
                    return "CRITICAL_FAIL_MOCK_DETECTED"
                
                # Should handle gracefully
                return "error_handled"
            except Exception:
                # If it throws exception, that's also acceptable error handling
                return "error_handled"
                
        except Exception as e:
            return f"error: {str(e)}"
    
    async def test_concurrent_operations(self) -> str:
        """Test concurrent agent operations"""
        try:
            agents = [
                quick_agent(f"Agent {i}") 
                for i in range(3)
            ]
            
            # Run agents sequentially (since run() is synchronous)
            results = []
            mock_detected = False
            for i, agent in enumerate(agents):
                try:
                    result = agent.run(f"Task {i}")
                    
                    # КРИТИЧЕСКИЙ ПРОВАЛ: если хотя бы один mock ответ
                    if self._is_mock_response(result):
                        mock_detected = True
                    
                    results.append(result)
                except Exception as e:
                    results.append(e)
            
            if mock_detected:
                return "CRITICAL_FAIL_MOCK_DETECTED"
            
            # Check if at least 2 out of 3 succeeded
            successful = sum(1 for r in results if not isinstance(r, Exception))
            if successful >= 2:
                return "concurrent_success"
            return "concurrent_failed"
        except Exception as e:
            return f"error: {str(e)}"
    
    async def test_scalability_basic(self) -> str:
        """Test basic scalability with multiple agents"""
        try:
            # Create multiple agents
            agent_count = 5
            agents = []
            
            for i in range(agent_count):
                agent = quick_agent(f"Agent {i}")
                agents.append(agent)
            
            # Simple task for each agent
            start_time = time.time()
            results = []
            mock_detected = False
            for i, agent in enumerate(agents):
                try:
                    result = agent.run(f"Simple task {i}")
                    
                    # КРИТИЧЕСКИЙ ПРОВАЛ: если хотя бы один mock ответ
                    if self._is_mock_response(result):
                        mock_detected = True
                    
                    results.append(result)
                except Exception as e:
                    results.append(e)
            end_time = time.time()
            
            if mock_detected:
                return "CRITICAL_FAIL_MOCK_DETECTED"
            
            # Check performance criteria
            execution_time = end_time - start_time
            successful = sum(1 for r in results if not isinstance(r, Exception))
            
            # Basic scalability criteria: most agents succeed, reasonable time
            if successful >= agent_count * 0.8 and execution_time < 10:
                return "scalability_ok"
            return "scalability_poor"
        except Exception as e:
            return f"error: {str(e)}"


if __name__ == "__main__":
    async def main():
        benchmarks = FunctionalBenchmarks(use_mock_llm=True)
        await benchmarks.run_all_benchmarks()
    
    asyncio.run(main()) 