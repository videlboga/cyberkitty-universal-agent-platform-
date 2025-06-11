"""
Main Benchmark Runner for KittyCore

Orchestrates all benchmark types and generates comprehensive reports.
Inspired by industry-standard evaluation frameworks.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from .functional_benchmarks import FunctionalBenchmarks
from .evaluation_metrics import EvaluationMetrics, BenchmarkResult


class BenchmarkRunner:
    """Main benchmark orchestrator for KittyCore"""
    
    def __init__(self, 
                 use_mock_llm: bool = True,
                 output_dir: str = "benchmark_results"):
        self.use_mock_llm = use_mock_llm
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize benchmark components
        self.functional_benchmarks = FunctionalBenchmarks(use_mock_llm)
        self.metrics = EvaluationMetrics()
        
        # Results storage
        self.results: Dict[str, BenchmarkResult] = {}
    
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
        
    async def run_comprehensive_benchmarks(self) -> Dict[str, Any]:
        """Run all benchmark suites and generate comprehensive report"""
        print("=" * 60)
        print("🎯 KittyCore Comprehensive Benchmark Suite")
        print("=" * 60)
        print(f"📅 Started at: {datetime.now().isoformat()}")
        print(f"🤖 Using Mock LLM: {self.use_mock_llm}")
        print()
        
        start_time = time.time()
        
        # 1. Functional Benchmarks
        print("1️⃣ Running Functional Benchmarks...")
        functional_result = await self.functional_benchmarks.run_all_benchmarks()
        self.results["functional"] = functional_result
        print()
        
        # 2. Basic Performance Benchmarks (simplified for demo)
        print("2️⃣ Running Performance Benchmarks...")
        performance_result = await self._run_performance_benchmarks()
        self.results["performance"] = performance_result
        print()
        
        # 3. Quality Benchmarks (simplified for demo)
        print("3️⃣ Running Quality Benchmarks...")
        quality_result = await self._run_quality_benchmarks()
        self.results["quality"] = quality_result
        print()
        
        total_time = time.time() - start_time
        
        # Generate comprehensive report
        report = self._generate_comprehensive_report(total_time)
        
        # Save results
        self._save_results()
        
        print("=" * 60)
        print("🏁 Benchmark Suite Complete!")
        print(f"⏱️  Total Time: {total_time:.2f}s")
        print(f"📄 Results saved to: {self.output_dir}")
        print("=" * 60)
        
        return report
    
    async def _run_performance_benchmarks(self) -> BenchmarkResult:
        """Run performance-focused benchmarks"""
        self.metrics.start_measurement()
        
        # Test agent creation speed
        start_time = time.time()
        
        try:
            from kittycore import quick_agent
            
            # Create multiple agents quickly
            agents = []
            creation_times = []
            
            for i in range(10):
                agent_start = time.time()
                agent = quick_agent(f"Performance test agent {i}")
                agent_end = time.time()
                creation_times.append(agent_end - agent_start)
                agents.append(agent)
            
            # Run simple tasks (synchronously since run() is not async)
            results = []
            mock_detected = False
            for i, agent in enumerate(agents):
                try:
                    result = agent.run(f"Simple task {i}")
                    
                    # КРИТИЧЕСКИЙ ПРОВАЛ: если обнаружен mock ответ
                    if self._is_mock_response(str(result)):
                        mock_detected = True
                    
                    results.append(result)
                except Exception as e:
                    results.append(e)
            
            if mock_detected:
                print(f"   🚨 CRITICAL FAIL: Mock responses detected in performance test!")
                successful = 0  # Все провалы если есть mock
            else:
                successful = sum(1 for r in results if not isinstance(r, Exception))
            
            task_completion = self.metrics.measure_task_completion(
                total_tasks=10,
                completed_tasks=successful,
                completion_times=creation_times,
                failures=[]
            )
            
            performance = self.metrics.measure_performance()
            
            quality = self.metrics.measure_quality(
                expected_outputs=["success"] * 10,
                actual_outputs=[str(r) for r in results]
            )
            
            result = BenchmarkResult(
                benchmark_name="performance_benchmarks",
                timestamp=datetime.now(),
                task_completion=task_completion,
                performance=performance,
                quality=quality,
                metadata={
                    "agent_creation_times": creation_times,
                    "avg_creation_time": sum(creation_times) / len(creation_times)
                }
            )
            
            print(f"   ✅ Created {len(agents)} agents")
            print(f"   ⚡ Avg creation time: {sum(creation_times)/len(creation_times):.3f}s")
            print(f"   📊 Success rate: {successful}/{len(agents)}")
            
            return result
            
        except Exception as e:
            print(f"   ❌ Performance benchmark failed: {e}")
            # Return minimal result
            return BenchmarkResult(
                benchmark_name="performance_benchmarks",
                timestamp=datetime.now(),
                task_completion=self.metrics.measure_task_completion(0, 0, [], [str(e)]),
                performance=self.metrics.measure_performance(),
                quality=self.metrics.measure_quality([], [])
            )
    
    async def _run_quality_benchmarks(self) -> BenchmarkResult:
        """Run quality-focused benchmarks"""
        self.metrics.start_measurement()
        
        try:
            from kittycore import Agent
            
            # Test response quality with different scenarios
            test_cases = [
                {
                    "prompt": "Explain what artificial intelligence is in simple terms",
                    "expected_keywords": ["ai", "artificial", "intelligence", "computer", "machine"]
                },
                {
                    "prompt": "List 3 benefits of renewable energy",
                    "expected_keywords": ["renewable", "energy", "environment", "clean", "sustainable"]
                },
                {
                    "prompt": "What is the capital of France?",
                    "expected_keywords": ["paris", "france", "capital"]
                }
            ]
            
            agent = Agent(
                prompt="You are a helpful and accurate assistant. Provide clear, factual answers."
            )
            
            results = []
            successful = 0
            
            for i, test_case in enumerate(test_cases):
                try:
                    response = agent.run(test_case["prompt"])  # synchronous call
                    results.append(response)
                    
                    # КРИТИЧЕСКИЙ ПРОВАЛ: если обнаружен mock ответ
                    if self._is_mock_response(str(response)):
                        print(f"   🚨 CRITICAL FAIL: Mock response detected in quality test!")
                        continue  # Пропускаем дальнейшую проверку
                    
                    # Simple quality check
                    response_lower = str(response).lower()
                    keyword_matches = sum(1 for keyword in test_case["expected_keywords"] 
                                        if keyword in response_lower)
                    
                    if keyword_matches > 0:
                        successful += 1
                        
                except Exception as e:
                    results.append(f"error: {e}")
            
            task_completion = self.metrics.measure_task_completion(
                total_tasks=len(test_cases),
                completed_tasks=successful,
                completion_times=[1.0] * len(test_cases),  # Placeholder
                failures=[]
            )
            
            performance = self.metrics.measure_performance()
            
            quality = self.metrics.measure_quality(
                expected_outputs=[tc["prompt"] for tc in test_cases],
                actual_outputs=[str(r) for r in results]
            )
            
            result = BenchmarkResult(
                benchmark_name="quality_benchmarks", 
                timestamp=datetime.now(),
                task_completion=task_completion,
                performance=performance,
                quality=quality,
                metadata={
                    "test_cases": len(test_cases),
                    "quality_score": successful / len(test_cases)
                }
            )
            
            print(f"   ✅ Tested {len(test_cases)} quality scenarios")
            print(f"   🎯 Quality score: {successful}/{len(test_cases)}")
            print(f"   📝 Response coherence: {quality.coherence_score:.2f}")
            
            return result
            
        except Exception as e:
            print(f"   ❌ Quality benchmark failed: {e}")
            return BenchmarkResult(
                benchmark_name="quality_benchmarks",
                timestamp=datetime.now(),
                task_completion=self.metrics.measure_task_completion(0, 0, [], [str(e)]),
                performance=self.metrics.measure_performance(),
                quality=self.metrics.measure_quality([], [])
            )
    
    def _generate_comprehensive_report(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive benchmark report"""
        report = {
            "meta": {
                "timestamp": datetime.now().isoformat(),
                "total_execution_time": total_time,
                "kittycore_version": "2.1",
                "use_mock_llm": self.use_mock_llm
            },
            "summary": {
                "total_benchmarks": len(self.results),
                "overall_success_rate": 0.0,
                "overall_performance_score": 0.0,
                "overall_quality_score": 0.0
            },
            "details": {},
            "recommendations": []
        }
        
        # Calculate overall metrics
        success_rates = []
        performance_scores = []
        quality_scores = []
        
        for name, result in self.results.items():
            report["details"][name] = {
                "success_rate": result.task_completion.success_rate,
                "execution_time": result.performance.execution_time,
                "memory_usage_mb": result.performance.memory_usage_mb,
                "quality_score": result.quality.output_correctness,
                "coherence_score": result.quality.coherence_score,
                "failures": result.task_completion.failure_reasons
            }
            
            success_rates.append(result.task_completion.success_rate)
            performance_scores.append(1.0 / (result.performance.execution_time + 0.1))  # Inverse time
            quality_scores.append(result.quality.output_correctness)
        
        if success_rates:
            report["summary"]["overall_success_rate"] = sum(success_rates) / len(success_rates)
            report["summary"]["overall_performance_score"] = sum(performance_scores) / len(performance_scores) 
            report["summary"]["overall_quality_score"] = sum(quality_scores) / len(quality_scores)
        
        # Generate recommendations
        recommendations = []
        
        if report["summary"]["overall_success_rate"] < 0.8:
            recommendations.append("Consider improving error handling and robustness")
            
        if report["summary"]["overall_performance_score"] < 0.5:
            recommendations.append("Performance optimization needed - consider async improvements")
            
        if report["summary"]["overall_quality_score"] < 0.7:
            recommendations.append("Quality improvements needed - enhance LLM prompting or add validation")
        
        if not recommendations:
            recommendations.append("Excellent performance across all metrics! 🎉")
            
        report["recommendations"] = recommendations
        
        return report
    
    def _save_results(self):
        """Save all benchmark results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save individual results
        for name, result in self.results.items():
            filename = f"benchmark_{name}_{timestamp}.json"
            filepath = self.output_dir / filename
            
            # Convert to dict for JSON serialization
            result_dict = {
                "benchmark_name": result.benchmark_name,
                "timestamp": result.timestamp.isoformat(),
                "task_completion": {
                    "total_tasks": result.task_completion.total_tasks,
                    "completed_tasks": result.task_completion.completed_tasks,
                    "success_rate": result.task_completion.success_rate,
                    "avg_completion_time": result.task_completion.avg_completion_time,
                    "failure_reasons": result.task_completion.failure_reasons
                },
                "performance": {
                    "execution_time": result.performance.execution_time,
                    "memory_usage_mb": result.performance.memory_usage_mb,
                    "cpu_usage_percent": result.performance.cpu_usage_percent,
                    "tokens_per_second": result.performance.tokens_per_second
                },
                "quality": {
                    "output_correctness": result.quality.output_correctness,
                    "coherence_score": result.quality.coherence_score,
                    "relevance_score": result.quality.relevance_score,
                    "hallucination_rate": result.quality.hallucination_rate
                },
                "metadata": result.metadata
            }
            
            with open(filepath, 'w') as f:
                json.dump(result_dict, f, indent=2)
        
        # Save comprehensive report
        report = self._generate_comprehensive_report(0)  # Time already calculated
        report_filename = f"comprehensive_report_{timestamp}.json"
        report_filepath = self.output_dir / report_filename
        
        with open(report_filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save summary markdown report
        self._save_markdown_report(report, timestamp)
    
    def _save_markdown_report(self, report: Dict[str, Any], timestamp: str):
        """Save a readable markdown report"""
        md_content = f"""# KittyCore Benchmark Report

**Generated:** {report['meta']['timestamp']}  
**Version:** KittyCore {report['meta']['kittycore_version']}  
**Mock LLM:** {report['meta']['use_mock_llm']}  
**Total Time:** {report['meta']['total_execution_time']:.2f}s  

## 📊 Summary

- **Overall Success Rate:** {report['summary']['overall_success_rate']:.1%}
- **Performance Score:** {report['summary']['overall_performance_score']:.2f}
- **Quality Score:** {report['summary']['overall_quality_score']:.2f}

## 📋 Detailed Results

"""
        
        for name, details in report['details'].items():
            md_content += f"""### {name.title()} Benchmarks

- **Success Rate:** {details['success_rate']:.1%}
- **Execution Time:** {details['execution_time']:.2f}s
- **Memory Usage:** {details['memory_usage_mb']:.1f}MB
- **Quality Score:** {details['quality_score']:.2f}
- **Coherence Score:** {details['coherence_score']:.2f}

"""
            if details['failures']:
                md_content += "**Failures:**\n"
                for failure in details['failures']:
                    md_content += f"- {failure}\n"
                md_content += "\n"
        
        md_content += "## 💡 Recommendations\n\n"
        for rec in report['recommendations']:
            md_content += f"- {rec}\n"
        
        md_filename = f"benchmark_report_{timestamp}.md"
        md_filepath = self.output_dir / md_filename
        
        with open(md_filepath, 'w') as f:
            f.write(md_content)


# Quick benchmark launcher
async def run_quick_benchmark(use_mock_llm: bool = True):
    """Quick benchmark launcher for testing"""
    runner = BenchmarkRunner(use_mock_llm=use_mock_llm)
    return await runner.run_comprehensive_benchmarks()


if __name__ == "__main__":
    async def main():
        await run_quick_benchmark(use_mock_llm=True)
    
    asyncio.run(main()) 