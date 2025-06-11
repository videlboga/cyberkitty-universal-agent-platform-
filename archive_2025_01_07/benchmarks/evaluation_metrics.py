"""
Evaluation Metrics for KittyCore Benchmarking

Inspired by metrics from:
- MultiAgentBench: milestone-based KPIs, collaboration quality
- Galileo Agent Leaderboard: real-world business scenarios
- BenchMARL: multi-agent coordination protocols
- MARL-eval: statistical rigor
"""

import time
import psutil
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import traceback


@dataclass
class TaskCompletionMetric:
    """Task completion rate and success metrics"""
    total_tasks: int
    completed_tasks: int 
    success_rate: float
    avg_completion_time: float
    failure_reasons: List[str]


@dataclass
class PerformanceMetric:
    """Performance and efficiency metrics"""
    execution_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    tokens_per_second: Optional[float] = None
    cost_per_task: Optional[float] = None


@dataclass
class QualityMetric:
    """Output quality and correctness metrics"""
    output_correctness: float  # 0-1 scale
    coherence_score: float     # 0-1 scale  
    relevance_score: float     # 0-1 scale
    hallucination_rate: float  # 0-1 scale (lower is better)
    semantic_similarity: Optional[float] = None


@dataclass
class CollaborationMetric:
    """Multi-agent collaboration metrics"""
    communication_efficiency: float
    coordination_success_rate: float
    conflict_resolution_rate: float
    agent_specialization_score: float
    emergent_behavior_detected: bool


@dataclass
class ScalabilityMetric:
    """Scalability and robustness metrics"""
    max_agents_handled: int
    performance_degradation: float  # percentage drop per agent
    error_recovery_time: float
    fault_tolerance_score: float


@dataclass
class BenchmarkResult:
    """Complete benchmark result"""
    benchmark_name: str
    timestamp: datetime
    task_completion: TaskCompletionMetric
    performance: PerformanceMetric
    quality: QualityMetric
    collaboration: Optional[CollaborationMetric] = None
    scalability: Optional[ScalabilityMetric] = None
    metadata: Optional[Dict[str, Any]] = None


class EvaluationMetrics:
    """Comprehensive evaluation metrics system"""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.start_time: Optional[float] = None
        self.process = psutil.Process()
        
    def start_measurement(self):
        """Start measuring performance metrics"""
        self.start_time = time.time()
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024
        
    def measure_task_completion(
        self, 
        total_tasks: int,
        completed_tasks: int,
        completion_times: List[float],
        failures: List[str]
    ) -> TaskCompletionMetric:
        """Measure task completion metrics"""
        success_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
        avg_time = np.mean(completion_times) if completion_times else 0
        
        return TaskCompletionMetric(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            success_rate=success_rate,
            avg_completion_time=avg_time,
            failure_reasons=failures
        )
    
    def measure_performance(self, tokens_used: Optional[int] = None) -> PerformanceMetric:
        """Measure performance metrics"""
        if self.start_time is None:
            raise ValueError("Must call start_measurement() first")
            
        execution_time = time.time() - self.start_time
        current_memory = self.process.memory_info().rss / 1024 / 1024
        memory_usage = max(0, current_memory - self.initial_memory)
        cpu_usage = self.process.cpu_percent()
        
        tokens_per_second = None
        if tokens_used and execution_time > 0:
            tokens_per_second = tokens_used / execution_time
            
        return PerformanceMetric(
            execution_time=execution_time,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            tokens_per_second=tokens_per_second
        )
    
    def measure_quality(
        self,
        expected_outputs: List[str],
        actual_outputs: List[str],
        human_ratings: Optional[List[float]] = None
    ) -> QualityMetric:
        """Measure output quality metrics"""
        if not actual_outputs:
            return QualityMetric(0, 0, 0, 1.0)
            
        # Simple quality metrics (can be enhanced with LLM-as-a-judge)
        correctness = self._calculate_correctness(expected_outputs, actual_outputs)
        coherence = self._calculate_coherence(actual_outputs)
        relevance = self._calculate_relevance(expected_outputs, actual_outputs)
        hallucination = self._detect_hallucinations(actual_outputs)
        
        return QualityMetric(
            output_correctness=correctness,
            coherence_score=coherence,
            relevance_score=relevance,
            hallucination_rate=hallucination
        )
    
    def measure_collaboration(
        self,
        agent_interactions: List[Dict[str, Any]],
        coordination_attempts: int,
        successful_coordinations: int
    ) -> CollaborationMetric:
        """Measure multi-agent collaboration metrics"""
        communication_eff = self._calculate_communication_efficiency(agent_interactions)
        coordination_rate = successful_coordinations / coordination_attempts if coordination_attempts > 0 else 0
        
        return CollaborationMetric(
            communication_efficiency=communication_eff,
            coordination_success_rate=coordination_rate,
            conflict_resolution_rate=0.8,  # Placeholder
            agent_specialization_score=0.7,  # Placeholder  
            emergent_behavior_detected=False  # Placeholder
        )
    
    def measure_scalability(
        self,
        agent_counts: List[int],
        performance_scores: List[float]
    ) -> ScalabilityMetric:
        """Measure scalability metrics"""
        max_agents = max(agent_counts) if agent_counts else 0
        
        # Calculate performance degradation
        degradation = 0.0
        if len(performance_scores) > 1:
            initial_perf = performance_scores[0] 
            final_perf = performance_scores[-1]
            degradation = max(0, (initial_perf - final_perf) / initial_perf * 100)
        
        return ScalabilityMetric(
            max_agents_handled=max_agents,
            performance_degradation=degradation,
            error_recovery_time=1.0,  # Placeholder
            fault_tolerance_score=0.8  # Placeholder
        )
    
    def _calculate_correctness(self, expected: List[str], actual: List[str]) -> float:
        """Calculate output correctness score"""
        if not expected or not actual:
            return 0.0
        
        # Simple string matching (can be enhanced)
        matches = sum(1 for e, a in zip(expected, actual) if e.lower().strip() in a.lower())
        return matches / len(expected)
    
    def _calculate_coherence(self, outputs: List[str]) -> float:
        """Calculate output coherence score"""
        if not outputs:
            return 0.0
        
        # Simple coherence check based on length and structure
        valid_outputs = sum(1 for output in outputs if len(output.strip()) > 10)
        return valid_outputs / len(outputs)
    
    def _calculate_relevance(self, expected: List[str], actual: List[str]) -> float:
        """Calculate output relevance score"""
        if not expected or not actual:
            return 0.0
        
        # Simple keyword overlap (can be enhanced with embeddings)
        total_relevance = 0
        for e, a in zip(expected, actual):
            e_words = set(e.lower().split())
            a_words = set(a.lower().split())
            if e_words:
                overlap = len(e_words.intersection(a_words)) / len(e_words)
                total_relevance += overlap
        
        return total_relevance / len(expected)
    
    def _detect_hallucinations(self, outputs: List[str]) -> float:
        """Detect hallucination rate"""
        if not outputs:
            return 0.0
        
        # Simple hallucination detection (can be enhanced)
        suspicious_patterns = ["I don't know", "cannot", "unable", "error"]
        hallucinations = 0
        
        for output in outputs:
            output_lower = output.lower()
            if any(pattern in output_lower for pattern in suspicious_patterns):
                continue  # These are honest admissions, not hallucinations
            # Additional hallucination detection logic can be added here
            
        return hallucinations / len(outputs)
    
    def _calculate_communication_efficiency(self, interactions: List[Dict[str, Any]]) -> float:
        """Calculate communication efficiency between agents"""
        if not interactions:
            return 0.0
        
        # Simple efficiency metric based on interaction success
        successful = sum(1 for i in interactions if i.get('success', False))
        return successful / len(interactions)
    
    def save_results(self, filepath: str):
        """Save benchmark results to JSON file"""
        results_data = []
        for result in self.results:
            result_dict = asdict(result)
            result_dict['timestamp'] = result.timestamp.isoformat()
            results_data.append(result_dict)
        
        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2)
    
    def load_results(self, filepath: str):
        """Load benchmark results from JSON file"""
        with open(filepath, 'r') as f:
            results_data = json.load(f)
        
        self.results = []
        for data in results_data:
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
            # Convert back to dataclass instances
            result = BenchmarkResult(**data)
            self.results.append(result)
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics across all benchmark results"""
        if not self.results:
            return {"message": "No benchmark results available"}
        
        return {
            "total_benchmarks": len(self.results),
            "avg_success_rate": np.mean([r.task_completion.success_rate for r in self.results]),
            "avg_execution_time": np.mean([r.performance.execution_time for r in self.results]),
            "avg_memory_usage": np.mean([r.performance.memory_usage_mb for r in self.results]),
            "avg_quality_score": np.mean([r.quality.output_correctness for r in self.results]),
            "benchmarks_by_name": {
                name: sum(1 for r in self.results if r.benchmark_name == name)
                for name in set(r.benchmark_name for r in self.results)
            }
        } 