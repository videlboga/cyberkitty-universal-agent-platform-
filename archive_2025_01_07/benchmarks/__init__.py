"""
KittyCore Benchmarking Suite

Comprehensive evaluation framework for multi-agent systems inspired by:
- MultiAgentBench (comprehensive evaluation)
- BenchMARL (MARL-specific benchmarks)  
- MARL-eval (statistical evaluation)
- Galileo Agent Leaderboard (real-world business scenarios)
"""

from .functional_benchmarks import FunctionalBenchmarks
from .performance_benchmarks import PerformanceBenchmarks
from .quality_benchmarks import QualityBenchmarks
from .comparative_benchmarks import ComparativeBenchmarks
from .benchmark_runner import BenchmarkRunner
from .evaluation_metrics import EvaluationMetrics

__all__ = [
    'FunctionalBenchmarks',
    'PerformanceBenchmarks', 
    'QualityBenchmarks',
    'ComparativeBenchmarks',
    'BenchmarkRunner',
    'EvaluationMetrics'
]

__version__ = "1.0.0" 