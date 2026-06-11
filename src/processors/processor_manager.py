"""
处理器管理器
负责协调多个处理器的执行
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .base_processor import BaseProcessor, ProcessedWorkItem, ProcessorFactory


class ProcessorManager:
    """处理器管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("processor_manager")
        self.processors = {}
        self.execution_history = []
        
        # 初始化默认处理器
        self._initialize_default_processors()
    
    def _initialize_default_processors(self):
        """初始化默认处理器"""
        default_processors = [
            {
                "name": "data_cleaner",
                "processor_type": "data_cleaner",
                "config": {
                    "min_duration": 1,
                    "max_duration": 480,
                    "remove_duplicates": True,
                    "normalize_timestamps": True,
                    "fill_missing_fields": True
                },
                "enabled": True
            },
            {
                "name": "data_analyzer",
                "processor_type": "data_analyzer",
                "config": {
                    "time_bucket_size": 60,
                    "top_n_categories": 10,
                    "top_n_keywords": 20,
                    "min_insight_confidence": 0.7
                },
                "enabled": True
            }
        ]
        
        for proc_config in default_processors:
            if proc_config["enabled"]:
                self.add_processor(
                    name=proc_config["name"],
                    processor_type=proc_config["processor_type"],
                    config=proc_config["config"]
                )
    
    def add_processor(self, name: str, processor_type: str, config: Dict[str, Any] = None) -> bool:
        """添加处理器"""
        try:
            processor = ProcessorFactory.create(processor_type, config or {})
            self.processors[name] = processor
            self.logger.info(f"添加处理器: {name} ({processor_type})")
            return True
        except Exception as e:
            self.logger.error(f"添加处理器失败 {name} ({processor_type}): {e}")
            return False
    
    def remove_processor(self, name: str) -> bool:
        """移除处理器"""
        if name in self.processors:
            del self.processors[name]
            self.logger.info(f"移除处理器: {name}")
            return True
        else:
            self.logger.warning(f"处理器不存在: {name}")
            return False
    
    def get_processor(self, name: str) -> Optional[BaseProcessor]:
        """获取处理器"""
        return self.processors.get(name)
    
    def list_processors(self) -> List[Dict[str, Any]]:
        """列出所有处理器"""
        processors_info = []
        for name, processor in self.processors.items():
            processors_info.append({
                "name": name,
                "type": processor.__class__.__name__,
                "config": processor.config,
                "enabled": True
            })
        return processors_info
    
    def process_workflow(self, work_items: List[Dict[str, Any]], workflow: List[str] = None) -> Dict[str, Any]:
        """
        执行处理工作流
        
        Args:
            work_items: 原始工作项列表
            workflow: 处理器执行顺序，如果为None则使用默认顺序
            
        Returns:
            处理结果
        """
        start_time = datetime.now()
        self.logger.info(f"开始处理工作流，共 {len(work_items)} 个工作项")
        
        # 默认工作流：数据清洗 -> 数据分析
        if workflow is None:
            workflow = ["data_cleaner", "data_analyzer"]
        
        # 验证工作流
        valid_workflow = []
        for processor_name in workflow:
            if processor_name in self.processors:
                valid_workflow.append(processor_name)
            else:
                self.logger.warning(f"跳过不存在的处理器: {processor_name}")
        
        if not valid_workflow:
            self.logger.error("没有可用的处理器")
            return {
                "success": False,
                "error": "没有可用的处理器",
                "processed_items": [],
                "analysis_results": {},
                "execution_time_ms": 0
            }
        
        self.logger.info(f"执行工作流: {valid_workflow}")
        
        # 执行工作流
        current_items = work_items
        intermediate_results = {}
        processed_items_list = []
        
        for i, processor_name in enumerate(valid_workflow):
            processor = self.processors[processor_name]
            self.logger.info(f"执行处理器 [{i+1}/{len(valid_workflow)}]: {processor_name}")
            
            try:
                if processor_name == "data_cleaner":
                    # 数据清洗器返回ProcessedWorkItem列表
                    processed_items = processor.process(current_items)
                    processed_items_list = processed_items
                    intermediate_results[processor_name] = {
                        "type": "cleaning",
                        "input_count": len(current_items),
                        "output_count": len(processed_items),
                        "filtered_count": len(current_items) - len(processed_items)
                    }
                    
                    # 为下一个处理器准备数据
                    if i + 1 < len(valid_workflow):
                        next_processor_name = valid_workflow[i + 1]
                        if next_processor_name == "data_analyzer":
                            # 数据分析器需要ProcessedWorkItem列表
                            current_items = processed_items
                        else:
                            # 其他处理器可能需要不同的数据格式
                            current_items = [item.cleaned_item for item in processed_items]
                
                elif processor_name == "data_analyzer":
                    # 数据分析器返回分析报告
                    analysis_results = processor.process(current_items)
                    intermediate_results[processor_name] = {
                        "type": "analysis",
                        "input_count": len(current_items),
                        "analysis_type": "comprehensive"
                    }
                    
                    # 保存分析结果
                    intermediate_results[processor_name]["results"] = analysis_results
                
                else:
                    # 其他类型的处理器
                    results = processor.process(current_items)
                    intermediate_results[processor_name] = {
                        "type": "custom",
                        "input_count": len(current_items),
                        "output": results
                    }
                    
                    # 更新当前数据
                    if isinstance(results, list):
                        current_items = results
                    
                self.logger.info(f"处理器 {processor_name} 执行成功")
                
            except Exception as e:
                self.logger.error(f"处理器 {processor_name} 执行失败: {e}")
                intermediate_results[processor_name] = {
                    "type": "error",
                    "error": str(e),
                    "success": False
                }
                # 继续执行下一个处理器
        
        # 计算执行时间
        end_time = datetime.now()
        execution_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # 构建最终结果
        final_results = {
            "success": True,
            "workflow": valid_workflow,
            "execution_time_ms": execution_time_ms,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "processed_items": processed_items_list,
            "intermediate_results": intermediate_results,
            "summary": self._generate_summary(processed_items_list, intermediate_results)
        }
        
        # 记录执行历史
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "workflow": valid_workflow,
            "input_count": len(work_items),
            "output_count": len(processed_items_list) if processed_items_list else 0,
            "execution_time_ms": execution_time_ms,
            "success": True
        })
        
        self.logger.info(f"工作流执行完成，耗时 {execution_time_ms:.1f}ms")
        return final_results
    
    def _generate_summary(self, processed_items: List[ProcessedWorkItem], 
                         intermediate_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成处理摘要"""
        if not processed_items:
            return {"total_items": 0, "note": "没有处理任何工作项"}
        
        # 从中间结果中提取分析结果
        analysis_results = None
        for proc_name, results in intermediate_results.items():
            if proc_name == "data_analyzer" and "results" in results:
                analysis_results = results["results"]
                break
        
        summary = {
            "total_items": len(processed_items),
            "processing_stages": len(intermediate_results),
            "successful_stages": sum(1 for r in intermediate_results.values() if r.get("type") != "error"),
            "failed_stages": sum(1 for r in intermediate_results.values() if r.get("type") == "error")
        }
        
        # 如果有分析结果，添加摘要信息
        if analysis_results:
            metadata = analysis_results.get("metadata", {})
            summary_stats = analysis_results.get("summary_statistics", {})
            
            summary.update({
                "time_range": metadata.get("time_range", {}),
                "total_duration_hours": summary_stats.get("overall", {}).get("total_duration_hours", 0),
                "unique_tools": summary_stats.get("overall", {}).get("unique_tools", 0),
                "unique_categories": summary_stats.get("overall", {}).get("unique_categories", 0),
                "avg_duration_minutes": summary_stats.get("averages", {}).get("avg_duration_minutes", 0)
            })
        
        return summary
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.execution_history[-limit:] if self.execution_history else []
    
    def clear_execution_history(self):
        """清除执行历史"""
        self.execution_history = []
        self.logger.info("已清除执行历史")
    
    def export_results(self, results: Dict[str, Any], format: str = "json") -> str:
        """
        导出处理结果
        
        Args:
            results: 处理结果
            format: 导出格式 (json, yaml, text)
            
        Returns:
            导出的字符串
        """
        import json
        import yaml
        
        if format == "json":
            return json.dumps(results, ensure_ascii=False, indent=2)
        elif format == "yaml":
            return yaml.dump(results, allow_unicode=True, default_flow_style=False)
        elif format == "text":
            return self._format_results_as_text(results)
        else:
            raise ValueError(f"不支持的导出格式: {format}")
    
    def _format_results_as_text(self, results: Dict[str, Any]) -> str:
        """将结果格式化为文本"""
        lines = []
        lines.append("=" * 60)
        lines.append("工作流处理结果摘要")
        lines.append("=" * 60)
        
        # 基本信息
        lines.append(f"执行时间: {results.get('execution_time_ms', 0):.1f}ms")
        lines.append(f"工作流: {' -> '.join(results.get('workflow', []))}")
        
        # 处理摘要
        summary = results.get('summary', {})
        lines.append(f"处理工作项: {summary.get('total_items', 0)} 个")
        lines.append(f"处理阶段: {summary.get('successful_stages', 0)}/{summary.get('processing_stages', 0)} 成功")
        
        # 分析结果摘要
        for proc_name, proc_results in results.get('intermediate_results', {}).items():
            if proc_name == "data_analyzer" and "results" in proc_results:
                analysis = proc_results["results"]
                insights = analysis.get("insights", {})
                
                lines.append("\n" + "-" * 40)
                lines.append(f"分析洞察 ({proc_name}):")
                
                for category, insight_list in insights.items():
                    if insight_list:
                        lines.append(f"  {category}:")
                        for insight in insight_list[:3]:  # 最多显示3个
                            lines.append(f"    • {insight}")
        
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)


def create_default_processor_manager() -> ProcessorManager:
    """创建默认处理器管理器"""
    return ProcessorManager()