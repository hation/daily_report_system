"""
收集器管理器
统一管理所有数据收集器，协调数据收集工作
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import yaml

from .base_collector import BaseCollector, WorkItem


class CollectorManager:
    """收集器管理器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化收集器管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.logger = logging.getLogger("collector_manager")
        self.collectors: Dict[str, BaseCollector] = {}
        self.config = {}
        
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str):
        """加载配置文件"""
        config_file = Path(config_path).expanduser()
        if not config_file.exists():
            self.logger.warning(f"配置文件不存在: {config_path}")
            return
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.suffix in ['.yaml', '.yml']:
                    self.config = yaml.safe_load(f)
                elif config_file.suffix == '.json':
                    self.config = json.load(f)
                else:
                    self.logger.error(f"不支持的配置文件格式: {config_file.suffix}")
                    return
            
            self.logger.info(f"从 {config_path} 加载配置成功")
            
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
    
    def register_collector(self, name: str, collector: BaseCollector):
        """注册收集器"""
        self.collectors[name] = collector
        self.logger.info(f"注册收集器: {name}")
    
    def create_collector(self, name: str, collector_config: Dict[str, Any]) -> bool:
        """创建并注册收集器"""
        try:
            from . import CollectorFactory
            collector = CollectorFactory.create(name, collector_config)
            self.register_collector(name, collector)
            return True
        except Exception as e:
            self.logger.error(f"创建收集器 {name} 失败: {e}")
            return False
    
    def create_collectors_from_config(self, config_section: str = 'collectors'):
        """从配置创建所有收集器"""
        if config_section not in self.config:
            self.logger.warning(f"配置中缺少 {config_section} 部分")
            return
        
        collectors_config = self.config[config_section]
        
        for collector_name, collector_config in collectors_config.items():
            if not self.create_collector(collector_name, collector_config):
                self.logger.warning(f"跳过收集器: {collector_name}")
    
    def test_all_connections(self) -> Dict[str, bool]:
        """测试所有收集器连接"""
        results = {}
        
        for name, collector in self.collectors.items():
            self.logger.info(f"测试收集器连接: {name}")
            try:
                success = collector.test_connection()
                results[name] = success
                
                if success:
                    self.logger.info(f"✓ {name}: 连接成功")
                else:
                    self.logger.warning(f"✗ {name}: 连接失败")
                    
            except Exception as e:
                self.logger.error(f"测试 {name} 连接时出错: {e}")
                results[name] = False
        
        return results
    
    def collect_all(self, 
                    start_time: datetime = None, 
                    end_time: datetime = None,
                    collector_names: List[str] = None) -> Dict[str, Any]:
        """
        收集所有收集器的工作项
        
        Args:
            start_time: 开始时间，默认为今天0点
            end_time: 结束时间，默认为现在
            collector_names: 要收集的收集器名称列表，None表示所有
            
        Returns:
            标准收集结果，包含合并后的工作项和各收集器结果
        """
        collection_start = datetime.now()
        
        if isinstance(start_time, dict):
            time_range = start_time
            start_time = time_range.get("start_time")
            end_time = time_range.get("end_time")
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time)
        
        if end_time is None:
            end_time = datetime.now()
        
        if start_time is None:
            start_time = end_time.replace(hour=0, minute=0, second=0, microsecond=0)
        
        self.logger.info(f"收集工作项: {start_time} - {end_time}")
        
        collector_results = {}
        all_work_items = []
        
        collectors_to_collect = self.collectors
        if collector_names:
            collectors_to_collect = {
                name: collector 
                for name, collector in self.collectors.items() 
                if name in collector_names
            }
        
        for name, collector in collectors_to_collect.items():
            self.logger.info(f"开始收集: {name}")
            try:
                work_items = collector.collect(start_time, end_time)
                stats = collector.get_statistics(work_items)
                all_work_items.extend(work_items)
                collector_results[name] = {
                    "success": True,
                    "items": work_items,
                    "stats": stats,
                    "error": None
                }
                
                self.logger.info(
                    f"✓ {name}: 收集到 {len(work_items)} 个工作项，"
                    f"总时长 {stats.get('total_duration_hours', 0):.1f} 小时"
                )
                
                if work_items:
                    self.logger.debug(f"{name} 统计: {json.dumps(stats, ensure_ascii=False, indent=2)}")
                    
            except Exception as e:
                self.logger.error(f"收集 {name} 时出错: {e}")
                collector_results[name] = {
                    "success": False,
                    "items": [],
                    "stats": {},
                    "error": str(e)
                }
        
        collection_time_ms = (datetime.now() - collection_start).total_seconds() * 1000
        return {
            "success": True,
            "work_items": all_work_items,
            "collector_results": collector_results,
            "collection_time_ms": collection_time_ms,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
    
    def get_combined_statistics(self, all_results: Dict[str, List[WorkItem]]) -> Dict[str, Any]:
        """获取所有收集器的合并统计信息"""
        total_items = 0
        total_duration_minutes = 0
        all_items = []
        
        for collector_name, items in all_results.items():
            total_items += len(items)
            total_duration_minutes += sum(item.duration_minutes for item in items)
            all_items.extend(items)
        
        # 按工具统计
        tool_stats = {}
        for item in all_items:
            tool_stats[item.tool] = tool_stats.get(item.tool, 0) + 1
        
        # 按分类统计
        category_stats = {}
        for item in all_items:
            category_stats[item.category] = category_stats.get(item.category, 0) + 1
        
        # 按状态统计
        status_stats = {}
        for item in all_items:
            status_stats[item.status] = status_stats.get(item.status, 0) + 1
        
        # 按优先级统计
        priority_stats = {}
        for item in all_items:
            priority_stats[item.priority] = priority_stats.get(item.priority, 0) + 1
        
        return {
            "total_collectors": len(self.collectors),
            "total_items": total_items,
            "total_duration_minutes": total_duration_minutes,
            "total_duration_hours": round(total_duration_minutes / 60, 2),
            "average_duration_minutes": round(total_duration_minutes / total_items, 2) if total_items > 0 else 0,
            "tools": tool_stats,
            "categories": category_stats,
            "statuses": status_stats,
            "priorities": priority_stats,
            "collector_summary": {
                name: {
                    "items": len(items),
                    "duration_minutes": sum(item.duration_minutes for item in items)
                }
                for name, items in all_results.items()
            }
        }
    
    def export_results(self, 
                      all_results: Dict[str, List[WorkItem]], 
                      output_dir: str,
                      format: str = 'json') -> List[str]:
        """
        导出收集结果
        
        Args:
            all_results: 收集结果
            output_dir: 输出目录
            format: 输出格式 (json, csv, yaml)
            
        Returns:
            导出的文件路径列表
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        exported_files = []
        
        # 导出每个收集器的结果
        for collector_name, items in all_results.items():
            if not items:
                continue
            
            # 转换为字典列表
            items_dict = [item.to_dict() for item in items]
            
            # 构建文件名
            filename = f"{collector_name}_{timestamp}.{format}"
            filepath = output_path / filename
            
            try:
                if format == 'json':
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(items_dict, f, ensure_ascii=False, indent=2, default=str)
                
                elif format == 'yaml':
                    with open(filepath, 'w', encoding='utf-8') as f:
                        yaml.dump(items_dict, f, allow_unicode=True, default_flow_style=False)
                
                elif format == 'csv':
                    # 简化CSV导出
                    import csv
                    if items_dict:
                        fieldnames = items_dict[0].keys()
                        with open(filepath, 'w', encoding='utf-8', newline='') as f:
                            writer = csv.DictWriter(f, fieldnames=fieldnames)
                            writer.writeheader()
                            writer.writerows(items_dict)
                
                self.logger.info(f"导出 {collector_name} 结果到: {filepath}")
                exported_files.append(str(filepath))
                
            except Exception as e:
                self.logger.error(f"导出 {collector_name} 结果失败: {e}")
        
        # 导出合并统计信息
        stats = self.get_combined_statistics(all_results)
        stats_file = output_path / f"summary_{timestamp}.json"
        
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
            
            self.logger.info(f"导出统计信息到: {stats_file}")
            exported_files.append(str(stats_file))
            
        except Exception as e:
            self.logger.error(f"导出统计信息失败: {e}")
        
        return exported_files
    
    def cleanup(self):
        """清理所有收集器资源"""
        for name, collector in self.collectors.items():
            try:
                collector.cleanup()
                self.logger.info(f"清理收集器: {name}")
            except Exception as e:
                self.logger.error(f"清理收集器 {name} 失败: {e}")
        
        self.collectors.clear()
    
    def list_collectors(self) -> List[str]:
        """列出所有已注册的收集器"""
        return list(self.collectors.keys())
    
    def get_collector_info(self, name: str) -> Dict[str, Any]:
        """获取收集器信息"""
        if name not in self.collectors:
            return {"error": f"收集器 {name} 未找到"}
        
        collector = self.collectors[name]
        return {
            "name": collector.name,
            "config": collector.config,
            "required_config_keys": collector.get_required_config_keys()
        }
    
    def collect(self, start_time: datetime = None, end_time: datetime = None) -> List[WorkItem]:
        """
        收集工作项（简化接口）
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            工作项列表
        """
        results = self.collect_all(start_time, end_time)
        return results.get("work_items", [])


def create_default_collector_manager() -> CollectorManager:
    """创建默认收集器管理器"""
    manager = CollectorManager()
    
    # 默认配置
    default_config = {
        'trae-cn': {
            'data_path': '~/.trae-cn/memory/projects/'
        },
        'trae-work-cn': {
            'history_path': '~/Library/Application Support/TRAE SOLO CN/User/History/'
        },
        'codex': {
            'db_path': '~/.codex/state_5.sqlite'
        },
        'pilotdeck': {
            'root_path': '~/.pilotdeck'
        },
        'openclaw': {
            'db_path': '~/.openclaw/lcm.db'
        },
        'hermes': {
            'sessions_path': '~/.hermes/sessions/',
            'memory_path': '~/.hermes/memory_evaluation/'
        }
    }
    
    # 创建默认收集器
    for name, config in default_config.items():
        manager.create_collector(name, config)
    
    return manager