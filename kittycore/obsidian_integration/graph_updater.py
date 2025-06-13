"""
GraphUpdater - автоматическое обновление данных графа Obsidian в реальном времени
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from loguru import logger


@dataclass
class GraphNode:
    """Узел графа Obsidian"""
    id: str
    name: str
    type: str  # "agent", "task", "result", "report"
    size: int = 10
    color: str = "#3498db"
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class GraphEdge:
    """Связь в графе"""
    source: str
    target: str
    type: str  # "assigned", "created", "reviewed", "linked"
    weight: int = 1
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class GraphUpdater:
    """
    Автоматическое обновление данных графа связей в реальном времени
    
    Возможности:
    - Мониторинг изменений в vault
    - Автоматическое обновление узлов и связей
    - Экспорт данных для визуализации
    - Уведомления об изменениях
    """
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.last_update = time.time()
        self.update_interval = 5  # секунд
        self.is_monitoring = False
        
        logger.debug(f"📊 GraphUpdater инициализирован для: {vault_path}")
    
    async def start_monitoring(self):
        """Запуск мониторинга изменений"""
        self.is_monitoring = True
        logger.info("🔄 Запущен мониторинг графа в реальном времени")
        
        while self.is_monitoring:
            try:
                await self.update_graph()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"❌ Ошибка мониторинга графа: {e}")
                await asyncio.sleep(self.update_interval)
    
    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.is_monitoring = False
        logger.info("⏹️ Мониторинг графа остановлен")
    
    async def update_graph(self, force: bool = False):
        """Обновление данных графа"""
        try:
            # Сканирование изменений или принудительное обновление
            changes_detected = force or await self._scan_for_changes()
            
            if changes_detected:
                # Перестроение узлов
                await self._rebuild_nodes()
                
                # Перестроение связей
                await self._rebuild_edges()
                
                # Экспорт обновлённых данных
                await self._export_graph_data()
                
                self.last_update = time.time()
                logger.debug("📊 Граф обновлён")
        
        except Exception as e:
            logger.error(f"❌ Ошибка обновления графа: {e}")
    
    async def _scan_for_changes(self) -> bool:
        """Проверка изменений в vault"""
        try:
            current_time = time.time()
            
            # Проверяем файлы изменённые после последнего обновления
            for md_file in self.vault_path.rglob("*.md"):
                if md_file.stat().st_mtime > self.last_update:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка сканирования изменений: {e}")
            return False
    
    async def _rebuild_nodes(self):
        """Перестроение узлов графа"""
        new_nodes = {}
        
        try:
            for md_file in self.vault_path.rglob("*.md"):
                node_id = md_file.stem
                node_type = self._determine_node_type(md_file)
                node_size = self._calculate_node_size(md_file)
                node_color = self._get_node_color(node_type)
                
                node = GraphNode(
                    id=node_id,
                    name=node_id,
                    type=node_type,
                    size=node_size,
                    color=node_color,
                    metadata={
                        "file_path": str(md_file),
                        "modified": md_file.stat().st_mtime,
                        "size_bytes": md_file.stat().st_size
                    }
                )
                
                new_nodes[node_id] = node
            
            self.nodes = new_nodes
            logger.debug(f"📊 Обновлено узлов: {len(self.nodes)}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка перестроения узлов: {e}")
    
    async def _rebuild_edges(self):
        """Перестроение связей графа"""
        new_edges = []
        
        try:
            for md_file in self.vault_path.rglob("*.md"):
                source_id = md_file.stem
                
                # Поиск ссылок в файле
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Извлечение [[ссылок]]
                    import re
                    links = re.findall(r'\[\[([^\]]+)\]\]', content)
                    
                    for link in links:
                        # Определяем тип связи
                        edge_type = self._determine_edge_type(source_id, link, content)
                        
                        edge = GraphEdge(
                            source=source_id,
                            target=link,
                            type=edge_type,
                            weight=1,
                            metadata={"context": "obsidian_link"}
                        )
                        
                        new_edges.append(edge)
                        
                except Exception as e:
                    logger.debug(f"⚠️ Ошибка чтения {md_file}: {e}")
            
            self.edges = new_edges
            logger.debug(f"📊 Обновлено связей: {len(self.edges)}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка перестроения связей: {e}")
    
    def _determine_node_type(self, file_path: Path) -> str:
        """Определение типа узла по пути файла"""
        if "Agents" in str(file_path):
            return "agent"
        elif "Tasks" in str(file_path):
            return "task"
        elif "Results" in str(file_path):
            return "result"
        elif "Reports" in str(file_path):
            return "report"
        else:
            return "note"
    
    def _calculate_node_size(self, file_path: Path) -> int:
        """Расчёт размера узла на основе размера файла"""
        try:
            size_bytes = file_path.stat().st_size
            # Размер от 10 до 50 пикселей
            return min(50, max(10, size_bytes // 100))
        except:
            return 10
    
    def _get_node_color(self, node_type: str) -> str:
        """Цвет узла по типу"""
        colors = {
            "agent": "#e74c3c",      # красный
            "task": "#3498db",       # синий  
            "result": "#2ecc71",     # зелёный
            "report": "#f39c12",     # оранжевый
            "note": "#9b59b6"        # фиолетовый
        }
        return colors.get(node_type, "#95a5a6")
    
    def _determine_edge_type(self, source: str, target: str, content: str) -> str:
        """Определение типа связи"""
        if "назначен" in content.lower() or "assigned" in content.lower():
            return "assigned"
        elif "создан" in content.lower() or "created" in content.lower():
            return "created"
        elif "проверен" in content.lower() or "reviewed" in content.lower():
            return "reviewed"
        else:
            return "linked"
    
    async def _export_graph_data(self):
        """Экспорт данных графа для визуализации"""
        try:
            graph_data = {
                "nodes": [asdict(node) for node in self.nodes.values()],
                "edges": [asdict(edge) for edge in self.edges],
                "metadata": {
                    "updated_at": time.time(),
                    "nodes_count": len(self.nodes),
                    "edges_count": len(self.edges),
                    "vault_path": str(self.vault_path)
                }
            }
            
            # Сохраняем JSON для использования в веб-интерфейсе
            graph_file = self.vault_path / "graph_data.json"
            with open(graph_file, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"📊 Данные графа экспортированы: {graph_file}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка экспорта данных графа: {e}")
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Получение статистики графа"""
        node_types = {}
        edge_types = {}
        
        for node in self.nodes.values():
            node_types[node.type] = node_types.get(node.type, 0) + 1
        
        for edge in self.edges:
            edge_types[edge.type] = edge_types.get(edge.type, 0) + 1
        
        return {
            "nodes_total": len(self.nodes),
            "edges_total": len(self.edges),
            "node_types": node_types,
            "edge_types": edge_types,
            "last_update": self.last_update,
            "vault_path": str(self.vault_path)
        } 