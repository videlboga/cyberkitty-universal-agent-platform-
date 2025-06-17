"""
ImageGenerationTool для KittyCore 3.0
Поддержка топовых моделей генерации изображений через Replicate API 2025
"""

import asyncio
import base64
import json
import os
import tempfile
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import httpx
import time

from .base_tool import BaseTool


@dataclass
class ImageGenerationRequest:
    """Запрос на генерацию изображения"""
    prompt: str
    model: Optional[str] = "flux-schnell"  # Дефолт - самая дешёвая модель
    width: Optional[int] = 1024
    height: Optional[int] = 1024
    num_images: Optional[int] = 1
    seed: Optional[int] = None
    style: Optional[str] = None
    negative_prompt: Optional[str] = None
    quality: Optional[str] = "standard"  # standard, high, ultra
    speed: Optional[str] = "balanced"    # fast, balanced, quality
    output_format: Optional[str] = "png"


@dataclass
class ImageGenerationResult:
    """Результат генерации изображения"""
    success: bool
    images: List[str]  # URLs или base64
    model_used: str
    cost_estimate: float
    generation_time: float
    metadata: Dict[str, Any]
    error: Optional[str] = None


@dataclass
class ModelInfo:
    """Информация о модели генерации"""
    name: str
    replicate_id: str
    cost_per_image: float
    max_resolution: int
    supports_batch: bool
    speed_rating: int  # 1-5, где 5 - самая быстрая
    quality_rating: int  # 1-5, где 5 - лучшее качество
    description: str
    features: List[str]


class ImageGenerationTool(BaseTool):
    """
    Универсальный инструмент генерации изображений через Replicate API
    
    Поддерживает топовые модели 2025 года:
    - FLUX семейство (Schnell, Dev, Pro)
    - Google Imagen 4
    - Recraft V3
    - Ideogram V3
    - И многие другие
    """
    
    name = "image_generation"
    description = "Генерация изображений через AI модели (FLUX, Imagen, Ideogram, etc.)"
    
    # Топовые модели 2025 года
    MODELS = {
        # FLUX семейство - лучший баланс цены/качества
        "flux-schnell": ModelInfo(
            name="FLUX Schnell",
            replicate_id="black-forest-labs/flux-schnell",
            cost_per_image=0.003,  # $3/1000 images
            max_resolution=2048,
            supports_batch=True,
            speed_rating=5,
            quality_rating=4,
            description="Самая быстрая и дешёвая модель FLUX",
            features=["ultra_fast", "batch_generation", "cost_effective"]
        ),
        
        "flux-dev": ModelInfo(
            name="FLUX Dev",
            replicate_id="black-forest-labs/flux-dev",
            cost_per_image=0.025,
            max_resolution=2048,
            supports_batch=True,
            speed_rating=4,
            quality_rating=4,
            description="Баланс скорости и качества FLUX",
            features=["high_quality", "prompt_adherence", "creative"]
        ),
        
        "flux-pro": ModelInfo(
            name="FLUX 1.1 Pro",
            replicate_id="black-forest-labs/flux-1.1-pro",
            cost_per_image=0.04,
            max_resolution=4096,
            supports_batch=True,
            speed_rating=3,
            quality_rating=5,
            description="Топовое качество FLUX с улучшенным следованием промптам",
            features=["sota_quality", "excellent_prompts", "high_res", "output_diversity"]
        ),
        
        # Google Imagen 4 - новинка 2025
        "imagen-4": ModelInfo(
            name="Google Imagen 4",
            replicate_id="google/imagen-4",
            cost_per_image=0.08,  # Примерная цена
            max_resolution=2048,
            supports_batch=False,
            speed_rating=3,
            quality_rating=5,
            description="Флагманская модель Google 2025",
            features=["google_quality", "photorealism", "fine_details"]
        ),
        
        "imagen-4-fast": ModelInfo(
            name="Google Imagen 4 Fast",
            replicate_id="google/imagen-4-fast",
            cost_per_image=0.04,
            max_resolution=2048,
            supports_batch=False,
            speed_rating=4,
            quality_rating=4,
            description="Быстрая версия Imagen 4",
            features=["google_fast", "good_quality", "speed_optimized"]
        ),
        
        # Ideogram V3 - лучший для текста в изображениях
        "ideogram-v3": ModelInfo(
            name="Ideogram V3 Quality",
            replicate_id="ideogram-ai/ideogram-v3-quality",
            cost_per_image=0.09,
            max_resolution=2048,
            supports_batch=False,
            speed_rating=3,
            quality_rating=5,
            description="Лучший для генерации текста в изображениях",
            features=["text_rendering", "creative_designs", "consistent_styles", "realism"]
        ),
        
        "ideogram-v3-turbo": ModelInfo(
            name="Ideogram V3 Turbo",
            replicate_id="ideogram-ai/ideogram-v3-turbo",
            cost_per_image=0.04,
            max_resolution=2048,
            supports_batch=False,
            speed_rating=5,
            quality_rating=4,
            description="Быстрая версия Ideogram V3",
            features=["text_rendering", "fast_generation", "cost_effective"]
        ),
        
        # Recraft V3 - SOTA качество
        "recraft-v3": ModelInfo(
            name="Recraft V3",
            replicate_id="recraft-ai/recraft-v3",
            cost_per_image=0.04,
            max_resolution=2048,
            supports_batch=False,
            speed_rating=3,
            quality_rating=5,
            description="SOTA качество по Artificial Analysis benchmark",
            features=["sota_benchmark", "long_texts", "wide_styles", "design_focused"]
        ),
        
        # Stable Diffusion XL - классика
        "sdxl": ModelInfo(
            name="Stable Diffusion XL",
            replicate_id="stability-ai/sdxl",
            cost_per_image=0.02,
            max_resolution=1024,
            supports_batch=True,
            speed_rating=4,
            quality_rating=3,
            description="Проверенная временем модель",
            features=["open_source", "customizable", "community_support"]
        )
    }
    
    def __init__(self, replicate_api_token: Optional[str] = None):
        super().__init__()
        self.api_token = replicate_api_token or os.getenv("REPLICATE_API_TOKEN")
        self.base_url = "https://api.replicate.com/v1"
        self.client = httpx.AsyncClient()
        
        if not self.api_token:
            self.logger.warning("⚠️ REPLICATE_API_TOKEN не найден - будет использован демо режим")
    
    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Выполнение действия генерации изображений"""
        try:
            if action == "generate_image":
                return await self._generate_image(**kwargs)
            elif action == "list_models":
                return await self._list_models(**kwargs)
            elif action == "get_model_info":
                return await self._get_model_info(**kwargs)
            elif action == "estimate_cost":
                return await self._estimate_cost(**kwargs)
            elif action == "batch_generate":
                return await self._batch_generate(**kwargs)
            elif action == "auto_select_model":
                return await self._auto_select_model(**kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Неизвестное действие: {action}",
                    "available_actions": [
                        "generate_image", "list_models", "get_model_info", 
                        "estimate_cost", "batch_generate", "auto_select_model"
                    ]
                }
        except Exception as e:
            self.logger.error(f"❌ Ошибка в ImageGenerationTool.{action}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_image(
        self, 
        prompt: str,
        model: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        num_images: int = 1,
        seed: Optional[int] = None,
        style: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        quality: str = "standard",
        speed: str = "balanced",
        output_format: str = "png",
        save_path: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Генерация изображения через выбранную модель"""
        
        start_time = time.time()
        
        # Автовыбор модели если не указана
        if not model:
            model = await self._smart_model_selection(prompt, quality, speed)
        
        # Валидация модели
        if model not in self.MODELS:
            return {
                "success": False,
                "error": f"Модель '{model}' не поддерживается",
                "available_models": list(self.MODELS.keys())
            }
        
        model_info = self.MODELS[model]
        
        # Демо режим без API токена
        if not self.api_token:
            return await self._demo_mode_response(prompt, model, model_info)
        
        try:
            # Подготовка запроса
            request_data = await self._prepare_request(
                model_info, prompt, width, height, num_images, 
                seed, style, negative_prompt, output_format, **kwargs
            )
            
            # Отправка запроса к Replicate
            result = await self._call_replicate_api(request_data)
            
            generation_time = time.time() - start_time
            
            # Обработка результата
            if result["success"]:
                # Сохранение изображений если указан путь
                if save_path:
                    saved_paths = await self._save_images(result["images"], save_path, output_format)
                    result["saved_paths"] = saved_paths
                
                result.update({
                    "model_used": model,
                    "model_info": asdict(model_info),
                    "generation_time": generation_time,
                    "cost_estimate": model_info.cost_per_image * num_images,
                    "prompt_used": prompt
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка генерации изображения: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": model,
                "generation_time": time.time() - start_time
            }
    
    async def _smart_model_selection(
        self, 
        prompt: str, 
        quality: str, 
        speed: str
    ) -> str:
        """Умный выбор модели на основе требований"""
        
        # Анализ промпта на ключевые слова
        prompt_lower = prompt.lower()
        
        # Если нужен текст в изображении - Ideogram
        if any(word in prompt_lower for word in ["text", "sign", "logo", "writing", "letter", "word"]):
            return "ideogram-v3-turbo" if speed == "fast" else "ideogram-v3"
        
        # Если нужна максимальная скорость
        if speed == "fast":
            return "flux-schnell"
        
        # Если нужно максимальное качество
        if quality == "ultra":
            return "flux-pro"
        
        # Если нужен фотореализм
        if any(word in prompt_lower for word in ["photo", "realistic", "portrait", "person", "face"]):
            return "imagen-4-fast" if speed == "fast" else "imagen-4"
        
        # Дефолт - лучший баланс
        return "flux-dev"
    
    async def _prepare_request(
        self, 
        model_info: ModelInfo, 
        prompt: str, 
        width: int, 
        height: int, 
        num_images: int,
        seed: Optional[int],
        style: Optional[str],
        negative_prompt: Optional[str],
        output_format: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Подготовка запроса для конкретной модели"""
        
        # Базовые параметры
        inputs = {
            "prompt": prompt,
            "width": min(width, model_info.max_resolution),
            "height": min(height, model_info.max_resolution),
            "output_format": output_format.lower()
        }
        
        # Seed для воспроизводимости
        if seed is not None:
            inputs["seed"] = seed
        
        # Negative prompt для лучшего контроля
        if negative_prompt:
            inputs["negative_prompt"] = negative_prompt
        
        # Количество изображений (если модель поддерживает)
        if model_info.supports_batch and num_images > 1:
            inputs["num_outputs"] = min(num_images, 4)  # Максимум 4 изображения
        
        # Специфичные параметры для FLUX моделей
        if "flux" in model_info.replicate_id:
            inputs.update({
                "guidance_scale": kwargs.get("guidance_scale", 3.5),
                "num_inference_steps": kwargs.get("steps", 28),
                "max_sequence_length": kwargs.get("max_sequence_length", 512)
            })
        
        # Специфичные параметры для Ideogram
        elif "ideogram" in model_info.replicate_id:
            inputs.update({
                "style_type": style or "AUTO",
                "magic_prompt_option": kwargs.get("magic_prompt", "AUTO")
            })
        
        # Специфичные параметры для Imagen
        elif "imagen" in model_info.replicate_id:
            inputs.update({
                "aspect_ratio": f"{width}:{height}",
                "safety_tolerance": kwargs.get("safety_tolerance", 2)
            })
        
        return {
            "version": model_info.replicate_id,
            "input": inputs
        }
    
    async def _call_replicate_api(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Вызов Replicate API"""
        
        headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # Создание prediction
        response = await self.client.post(
            f"{self.base_url}/predictions",
            headers=headers,
            json=request_data,
            timeout=30.0
        )
        
        if response.status_code != 201:
            return {
                "success": False,
                "error": f"API error: {response.status_code} - {response.text}"
            }
        
        prediction = response.json()
        prediction_id = prediction["id"]
        
        # Ожидание завершения
        max_wait = 300  # 5 минут максимум
        wait_time = 0
        
        while wait_time < max_wait:
            # Проверка статуса
            status_response = await self.client.get(
                f"{self.base_url}/predictions/{prediction_id}",
                headers=headers,
                timeout=10.0
            )
            
            if status_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Status check error: {status_response.status_code}"
                }
            
            status_data = status_response.json()
            status = status_data["status"]
            
            if status == "succeeded":
                return {
                    "success": True,
                    "images": status_data["output"] if isinstance(status_data["output"], list) else [status_data["output"]],
                    "metadata": {
                        "prediction_id": prediction_id,
                        "processing_time": status_data.get("metrics", {}).get("predict_time"),
                        "model_version": status_data.get("version")
                    }
                }
            
            elif status == "failed":
                return {
                    "success": False,
                    "error": f"Generation failed: {status_data.get('error', 'Unknown error')}"
                }
            
            # Ожидание перед следующей проверкой
            await asyncio.sleep(2)
            wait_time += 2
        
        return {
            "success": False,
            "error": "Generation timeout - превышено время ожидания"
        }
    
    async def _demo_mode_response(
        self, 
        prompt: str, 
        model: str, 
        model_info: ModelInfo
    ) -> Dict[str, Any]:
        """Демо режим без реального API"""
        
        # Имитация времени генерации
        await asyncio.sleep(2)
        
        return {
            "success": True,
            "images": [
                "https://picsum.photos/1024/1024?random=1",  # Placeholder изображение
                "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            ],
            "model_used": model,
            "model_info": asdict(model_info),
            "generation_time": 2.0,
            "cost_estimate": model_info.cost_per_image,
            "prompt_used": prompt,
            "demo_mode": True,
            "message": "🎭 ДЕМО РЕЖИМ: Реальная генерация требует REPLICATE_API_TOKEN",
            "metadata": {
                "demo": True,
                "placeholder_used": True
            }
        }
    
    async def _save_images(
        self, 
        image_urls: List[str], 
        save_path: str, 
        output_format: str
    ) -> List[str]:
        """Сохранение изображений на диск"""
        
        saved_paths = []
        save_dir = Path(save_path)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        for i, url in enumerate(image_urls):
            try:
                # Определение имени файла
                timestamp = int(time.time())
                filename = f"generated_image_{timestamp}_{i}.{output_format}"
                file_path = save_dir / filename
                
                # Скачивание изображения
                if url.startswith("data:"):
                    # Base64 изображение
                    header, data = url.split(",", 1)
                    image_data = base64.b64decode(data)
                    file_path.write_bytes(image_data)
                else:
                    # URL изображение
                    response = await self.client.get(url, timeout=30.0)
                    if response.status_code == 200:
                        file_path.write_bytes(response.content)
                    else:
                        continue
                
                saved_paths.append(str(file_path))
                self.logger.info(f"💾 Изображение сохранено: {file_path}")
                
            except Exception as e:
                self.logger.error(f"❌ Ошибка сохранения изображения {i}: {e}")
        
        return saved_paths
    
    async def _list_models(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Список доступных моделей"""
        
        models = {}
        
        for model_id, model_info in self.MODELS.items():
            # Фильтрация по категории
            if category:
                if category.lower() == "fast" and model_info.speed_rating < 4:
                    continue
                elif category.lower() == "quality" and model_info.quality_rating < 4:
                    continue
                elif category.lower() == "cheap" and model_info.cost_per_image > 0.03:
                    continue
            
            models[model_id] = {
                "name": model_info.name,
                "description": model_info.description,
                "cost_per_image": model_info.cost_per_image,
                "speed_rating": model_info.speed_rating,
                "quality_rating": model_info.quality_rating,
                "max_resolution": model_info.max_resolution,
                "supports_batch": model_info.supports_batch,
                "features": model_info.features
            }
        
        return {
            "success": True,
            "models": models,
            "total_models": len(models),
            "categories": ["fast", "quality", "cheap"],
            "recommendations": {
                "cheapest": "flux-schnell",
                "fastest": "flux-schnell",
                "best_quality": "flux-pro",
                "best_text": "ideogram-v3",
                "balanced": "flux-dev"
            }
        }
    
    async def _get_model_info(self, model: str) -> Dict[str, Any]:
        """Подробная информация о модели"""
        
        if model not in self.MODELS:
            return {
                "success": False,
                "error": f"Модель '{model}' не найдена",
                "available_models": list(self.MODELS.keys())
            }
        
        model_info = self.MODELS[model]
        
        return {
            "success": True,
            "model": model,
            "info": asdict(model_info),
            "pricing": {
                "cost_per_image": model_info.cost_per_image,
                "cost_for_10": model_info.cost_per_image * 10,
                "cost_for_100": model_info.cost_per_image * 100,
                "monthly_estimate_100_images": model_info.cost_per_image * 100
            },
            "capabilities": {
                "max_batch_size": 4 if model_info.supports_batch else 1,
                "estimated_time_per_image": 30 / model_info.speed_rating,  # секунд
                "recommended_for": model_info.features
            }
        }
    
    async def _estimate_cost(
        self, 
        model: str, 
        num_images: int = 1, 
        monthly_usage: Optional[int] = None
    ) -> Dict[str, Any]:
        """Оценка стоимости генерации"""
        
        if model not in self.MODELS:
            return {
                "success": False,
                "error": f"Модель '{model}' не найдена"
            }
        
        model_info = self.MODELS[model]
        
        single_cost = model_info.cost_per_image
        batch_cost = single_cost * num_images
        
        estimates = {
            "single_image": single_cost,
            "current_batch": batch_cost,
            "daily_10_images": single_cost * 10,
            "weekly_50_images": single_cost * 50,
            "monthly_200_images": single_cost * 200
        }
        
        if monthly_usage:
            estimates["monthly_custom"] = single_cost * monthly_usage
        
        return {
            "success": True,
            "model": model,
            "cost_per_image": single_cost,
            "estimates": estimates,
            "currency": "USD",
            "comparison": {
                "vs_midjourney": f"{(batch_cost / 0.05):.1f}x cheaper" if batch_cost < 0.05 else f"{(0.05 / batch_cost):.1f}x more expensive",
                "vs_dalle3": f"{(batch_cost / 0.08):.1f}x cheaper" if batch_cost < 0.08 else f"{(0.08 / batch_cost):.1f}x more expensive"
            }
        }
    
    async def _batch_generate(
        self, 
        prompts: List[str],
        model: Optional[str] = None,
        **common_params
    ) -> Dict[str, Any]:
        """Батчевая генерация изображений"""
        
        if not prompts:
            return {
                "success": False,
                "error": "Список промптов пуст"
            }
        
        if len(prompts) > 10:
            return {
                "success": False,
                "error": "Максимум 10 промптов в одном батче"
            }
        
        results = []
        total_cost = 0
        total_time = 0
        
        for i, prompt in enumerate(prompts):
            self.logger.info(f"🎨 Генерация {i+1}/{len(prompts)}: {prompt[:50]}...")
            
            result = await self._generate_image(
                prompt=prompt,
                model=model,
                **common_params
            )
            
            results.append(result)
            
            if result["success"]:
                total_cost += result.get("cost_estimate", 0)
                total_time += result.get("generation_time", 0)
        
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        
        return {
            "success": len(successful) > 0,
            "results": results,
            "summary": {
                "total_prompts": len(prompts),
                "successful": len(successful),
                "failed": len(failed),
                "total_cost": total_cost,
                "total_time": total_time,
                "average_time_per_image": total_time / max(len(successful), 1)
            },
            "all_images": [img for result in successful for img in result.get("images", [])],
            "errors": [r["error"] for r in failed]
        }
    
    async def _auto_select_model(
        self, 
        prompt: str,
        budget: Optional[float] = None,
        priority: str = "balanced"  # "speed", "quality", "cost", "balanced"
    ) -> Dict[str, Any]:
        """Автоматический выбор оптимальной модели"""
        
        # Анализ промпта
        prompt_analysis = await self._analyze_prompt(prompt)
        
        # Фильтрация моделей по бюджету
        available_models = self.MODELS
        if budget:
            available_models = {
                k: v for k, v in self.MODELS.items() 
                if v.cost_per_image <= budget
            }
        
        if not available_models:
            return {
                "success": False,
                "error": f"Нет моделей в бюджете ${budget}",
                "cheapest_model": min(self.MODELS.values(), key=lambda x: x.cost_per_image).name
            }
        
        # Выбор модели по приоритету
        if priority == "speed":
            best_model = max(available_models.items(), key=lambda x: x[1].speed_rating)
        elif priority == "quality":
            best_model = max(available_models.items(), key=lambda x: x[1].quality_rating)
        elif priority == "cost":
            best_model = min(available_models.items(), key=lambda x: x[1].cost_per_image)
        else:  # balanced
            best_model = max(
                available_models.items(), 
                key=lambda x: (x[1].speed_rating + x[1].quality_rating) / x[1].cost_per_image
            )
        
        model_id, model_info = best_model
        
        return {
            "success": True,
            "recommended_model": model_id,
            "model_info": asdict(model_info),
            "reasoning": {
                "priority": priority,
                "budget_constraint": budget,
                "prompt_analysis": prompt_analysis,
                "why_selected": self._explain_selection(model_info, priority, prompt_analysis)
            },
            "alternatives": [
                {"model": k, "score": v.speed_rating + v.quality_rating, "cost": v.cost_per_image}
                for k, v in list(available_models.items())[:3]
            ]
        }
    
    async def _analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Анализ промпта для выбора оптимальной модели"""
        
        prompt_lower = prompt.lower()
        
        analysis = {
            "needs_text_rendering": any(word in prompt_lower for word in ["text", "sign", "logo", "writing", "letter"]),
            "is_photorealistic": any(word in prompt_lower for word in ["photo", "realistic", "portrait", "person"]),
            "is_artistic": any(word in prompt_lower for word in ["art", "painting", "drawing", "illustration"]),
            "is_technical": any(word in prompt_lower for word in ["diagram", "schematic", "technical", "blueprint"]),
            "complexity": "high" if len(prompt.split()) > 20 else "medium" if len(prompt.split()) > 10 else "simple"
        }
        
        return analysis
    
    def _explain_selection(
        self, 
        model_info: ModelInfo, 
        priority: str, 
        analysis: Dict[str, Any]
    ) -> str:
        """Объяснение выбора модели"""
        
        reasons = []
        
        if analysis["needs_text_rendering"] and "text_rendering" in model_info.features:
            reasons.append("оптимизирована для генерации текста")
        
        if analysis["is_photorealistic"] and "photorealism" in model_info.features:
            reasons.append("отлично подходит для фотореализма")
        
        if priority == "speed" and model_info.speed_rating >= 4:
            reasons.append("высокая скорость генерации")
        
        if priority == "quality" and model_info.quality_rating >= 4:
            reasons.append("превосходное качество")
        
        if priority == "cost" and model_info.cost_per_image <= 0.03:
            reasons.append("очень низкая стоимость")
        
        if not reasons:
            reasons.append("лучший баланс характеристик")
        
        return ", ".join(reasons)
    
    async def cleanup(self):
        """Очистка ресурсов"""
        if hasattr(self, 'client'):
            await self.client.aclose()
    
    def get_json_schema(self) -> Dict[str, Any]:
        """JSON Schema для валидации параметров"""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "generate_image", "list_models", "get_model_info", 
                        "estimate_cost", "batch_generate", "auto_select_model"
                    ],
                    "description": "Действие для выполнения"
                },
                "prompt": {
                    "type": "string",
                    "description": "Описание изображения для генерации",
                    "minLength": 1,
                    "maxLength": 1000
                },
                "model": {
                    "type": "string",
                    "enum": list(MODELS.keys()),
                    "description": "Модель для генерации"
                },
                "width": {
                    "type": "integer",
                    "minimum": 256,
                    "maximum": 4096,
                    "default": 1024
                },
                "height": {
                    "type": "integer", 
                    "minimum": 256,
                    "maximum": 4096,
                    "default": 1024
                },
                "num_images": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 4,
                    "default": 1
                },
                "quality": {
                    "type": "string",
                    "enum": ["standard", "high", "ultra"],
                    "default": "standard"
                },
                "speed": {
                    "type": "string",
                    "enum": ["fast", "balanced", "quality"],
                    "default": "balanced"
                }
            },
            "required": ["action"],
            "additionalProperties": True
        }


# Экспорт для использования в агентах
__all__ = ["ImageGenerationTool", "ImageGenerationRequest", "ImageGenerationResult", "ModelInfo"]