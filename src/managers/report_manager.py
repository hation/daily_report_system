"""
报告管理器
协调数据收集、处理、格式化、推送全流程
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import yaml
import os
import sys
from pathlib import Path

# 添加项目路径
project_root = str(Path(__file__).resolve().parents[2])
sys.path.insert(0, os.path.join(project_root, "src"))

from src.collectors import create_default_collector_manager
from src.processors.processor_manager import create_default_processor_manager
from src.formatters.simple_report_formatter import create_work_report_formatter
from src.pushers.feishu_pusher import create_feishu_pusher


class ReportManager:
    """报告管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("report_manager")
        
        # 初始化组件
        self.collector_manager = None
        self.processor_manager = None
        self.report_formatter = None
        self.feishu_pusher = None
        
        # 执行历史
        self.execution_history = []
        self.report_history = []
        
        # 默认配置
        self.default_config = {
            "report_types": {
                "daily": {
                    "enabled": True,
                    "format": "daily_work_summary",
                    "push_time": "19:00",
                    "target": {"receive_type": "chat", "chat_id": None}
                },
                "weekly": {
                    "enabled": False,
                    "format": "detailed_work_report",
                    "push_time": "18:00",
                    "target": {"receive_type": "chat", "chat_id": None}
                }
            },
            "data_sources": ["trae-cn", "openclaw", "hermes"],
            "processing_workflow": ["data_cleaner", "data_analyzer"],
            "max_report_history": 30,
            "enable_backup": True,
            "backup_path": "./data/reports/backup/"
        }
        
        # 合并配置
        if config:
            self.default_config.update(config)
        
        self.config = self.default_config
    
    def initialize(self) -> bool:
        """初始化所有组件"""
        self.logger.info("初始化报告管理器组件")
        
        try:
            # 初始化收集器管理器
            self.collector_manager = create_default_collector_manager()
            self.logger.info("✅ 收集器管理器初始化成功")
            
            # 初始化处理器管理器
            self.processor_manager = create_default_processor_manager()
            self.logger.info("✅ 处理器管理器初始化成功")
            
            # 初始化报告格式化器
            self.report_formatter = create_work_report_formatter()
            self.logger.info("✅ 报告格式化器初始化成功")
            
            # 初始化飞书推送器
            feishu_config = {
                "app_id": self.config.get("feishu_app_id", os.getenv("FEISHU_APP_ID", "")),
                "app_secret": self.config.get("feishu_app_secret", os.getenv("FEISHU_APP_SECRET", "")),
                "encrypt_key": self.config.get("feishu_encrypt_key", os.getenv("FEISHU_ENCRYPT_KEY", "")),
                "verification_token": self.config.get("feishu_verification_token", os.getenv("FEISHU_VERIFICATION_TOKEN", "")),
                "default_chat_id": self.config.get(
                    "feishu_default_chat_id",
                    os.getenv("FEISHU_DEFAULT_CHAT_ID") or os.getenv("FEISHU_DAILY_REPORT_CHAT_ID") or os.getenv("LARK_DEFAULT_CHAT_ID") or os.getenv("DAILY_REPORT_CHAT_ID", "")
                ),
                "test_mode": self.config.get("test_mode", False),
                "prefer_lark_cli": self.config.get("prefer_lark_cli", True),
                "lark_cli_timeout": self.config.get("lark_cli_timeout", 30)
            }
            
            self.feishu_pusher = create_feishu_pusher(feishu_config)
            self.logger.info("✅ 飞书推送器初始化成功")
            
            # 创建备份目录
            if self.config.get("enable_backup"):
                backup_path = self.config.get("backup_path", "./data/reports/backup/")
                os.makedirs(backup_path, exist_ok=True)
                self.logger.info(f"✅ 备份目录已创建: {backup_path}")
            
            self.logger.info("🎉 所有组件初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化失败: {e}")
            return False
    
    def generate_report(self, report_type: str = "daily", 
                       time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        生成工作报告
        
        Args:
            report_type: 报告类型
            time_range: 时间范围
            
        Returns:
            报告生成结果
        """
        start_time = datetime.now()
        self.logger.info(f"开始生成 {report_type} 工作报告")
        
        execution_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # 步骤1: 收集数据
            self.logger.info("步骤1: 收集工作数据")
            collection_result = self._collect_data(time_range)
            
            if not collection_result.get("success"):
                return self._handle_error(execution_id, "数据收集失败", collection_result.get("error"))
            
            # 步骤2: 处理数据
            self.logger.info("步骤2: 处理工作数据")
            processing_result = self._process_data(collection_result.get("work_items", []))
            
            if not processing_result.get("success"):
                return self._handle_error(execution_id, "数据处理失败", processing_result.get("error"))
            
            analysis_results = processing_result.get("analysis_results", {})
            if time_range:
                analysis_results["report_period"] = time_range
            collection_stats = collection_result.get("stats", {})
            analysis_results["system_health"] = {
                "status": "normal" if collection_stats.get("failed_collectors", 0) == 0 else "partial",
                "successful_collectors": collection_stats.get("successful_collectors", 0),
                "failed_collectors": collection_stats.get("failed_collectors", 0),
                "collection_time_ms": collection_stats.get("collection_time_ms", 0),
                "processing_success": True
            }
            processing_result["analysis_results"] = analysis_results
            
            # 步骤3: 格式化报告
            self.logger.info("步骤3: 格式化工作报告")
            formatting_result = self._format_report(
                processing_result.get("analysis_results", {}),
                report_type
            )
            
            if not formatting_result.get("success"):
                return self._handle_error(execution_id, "报告格式化失败", formatting_result.get("error"))
            
            # 步骤4: 保存报告
            self.logger.info("步骤4: 保存工作报告")
            save_result = self._save_report(
                formatting_result.get("report_content"),
                execution_id,
                report_type,
                time_range
            )
            
            # 构建最终结果
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            result = {
                "success": True,
                "execution_id": execution_id,
                "report_type": report_type,
                "execution_time_seconds": execution_time,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "collection_stats": collection_result.get("stats", {}),
                "processing_stats": processing_result.get("stats", {}),
                "formatting_stats": formatting_result.get("stats", {}),
                "save_result": save_result,
                "report_content": formatting_result.get("report_content"),
                "analysis_results": processing_result.get("analysis_results", {}),
                "report_summary": self._generate_report_summary(
                    collection_result, processing_result, formatting_result
                )
            }
            
            # 记录执行历史
            self._record_execution(execution_id, result)
            
            self.logger.info(f"✅ 工作报告生成成功，执行ID: {execution_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"报告生成过程中出现异常: {e}")
            return self._handle_error(execution_id, "报告生成异常", str(e))
    
    def _collect_data(self, time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """收集数据"""
        if not self.collector_manager:
            return {"success": False, "error": "收集器管理器未初始化"}
        
        try:
            # 设置时间范围
            if not time_range:
                # 默认收集最近24小时的数据
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=24)
                time_range = {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat()
                }
            
            # 执行数据收集：兼容不同收集器管理器的方法名与返回结构
            if hasattr(self.collector_manager, "collect_all"):
                collection_result = self.collector_manager.collect_all(time_range)
            elif hasattr(self.collector_manager, "collect_work_items"):
                start_time = time_range.get("start_time")
                end_time = time_range.get("end_time")
                if isinstance(start_time, str):
                    start_time = datetime.fromisoformat(start_time)
                if isinstance(end_time, str):
                    end_time = datetime.fromisoformat(end_time)
                work_items = self.collector_manager.collect_work_items(start_time, end_time)
                collection_result = {
                    "work_items": work_items,
                    "collector_results": {
                        "default": {"success": True, "items_count": len(work_items)}
                    },
                    "collection_time_ms": 0
                }
            else:
                return {"success": False, "error": "收集器管理器缺少 collect_all 或 collect_work_items 方法"}
            
            # 兼容返回值为列表的情况，并将 WorkItem/dataclass/对象统一转换为字典
            if isinstance(collection_result, list):
                collection_result = {
                    "work_items": collection_result,
                    "collector_results": {
                        "default": {"success": True, "items_count": len(collection_result)}
                    },
                    "collection_time_ms": 0
                }
            
            raw_work_items = collection_result.get("work_items", [])
            normalized_work_items = []
            for item in raw_work_items:
                if isinstance(item, dict):
                    normalized_work_items.append(item)
                elif hasattr(item, "to_dict"):
                    normalized_work_items.append(item.to_dict())
                elif hasattr(item, "__dict__"):
                    item_dict = {}
                    for key, value in item.__dict__.items():
                        item_dict[key] = value.isoformat() if isinstance(value, datetime) else value
                    normalized_work_items.append(item_dict)
                else:
                    normalized_work_items.append({"value": str(item)})
            
            collection_result["work_items"] = normalized_work_items
            
            # 构建统计信息
            stats = {
                "total_items": len(collection_result.get("work_items", [])),
                "successful_collectors": len([c for c in collection_result.get("collector_results", {}).values() 
                                            if c.get("success")]),
                "failed_collectors": len([c for c in collection_result.get("collector_results", {}).values() 
                                         if not c.get("success")]),
                "collection_time_ms": collection_result.get("collection_time_ms", 0)
            }
            
            return {
                "success": True,
                "work_items": collection_result.get("work_items", []),
                "collector_results": collection_result.get("collector_results", {}),
                "stats": stats
            }
            
        except Exception as e:
            self.logger.error(f"数据收集失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _process_data(self, work_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """处理数据"""
        if not self.processor_manager:
            return {"success": False, "error": "处理器管理器未初始化"}
        
        if not work_items:
            self.logger.info("没有工作项数据，生成空分析报告")
            analysis_results = {
                "metadata": {
                    "analyzed_at": datetime.now().isoformat(),
                    "total_items": 0,
                    "analyzer": "data_analyzer",
                    "note": "没有数据可分析"
                },
                "overview": {
                    "total_work_items": 0,
                    "total_duration_hours": 0,
                    "unique_tools": 0,
                    "unique_categories": 0,
                    "average_duration_minutes": 0,
                    "completion_rate_percent": 0
                },
                "time_analysis": {"hourly": {}, "daily": {}, "weekly": {}},
                "tool_analysis": {"tools": {}, "total_by_tool": {}},
                "category_analysis": {},
                "key_insights": [],
                "content_summary": {"daily_summary": "今日没有收集到可分析的具体工作内容。", "human_summary_items": [], "activity_groups": [], "key_outputs": [], "blockers_or_notes": []},
                "insights": {"general": []},
                "summary_statistics": {"overall": {}, "averages": {}, "totals": {}},
                "priority_analysis": {},
                "duration_analysis": {},
                "keyword_analysis": {}
            }
            return {
                "success": True,
                "processed_items": [],
                "analysis_results": analysis_results,
                "processing_summary": {"total_items": 0},
                "stats": {
                    "input_items": 0,
                    "processed_items": 0,
                    "workflow_stages": 0,
                    "execution_time_ms": 0,
                    "analysis_sections": 0
                }
            }
        
        try:
            # 获取处理工作流
            workflow = self.config.get("processing_workflow", ["data_cleaner", "data_analyzer"])
            
            # 执行数据处理
            processing_result = self.processor_manager.process_workflow(work_items, workflow)
            
            if not processing_result.get("success"):
                return {"success": False, "error": processing_result.get("error", "数据处理失败")}
            
            # 提取分析结果
            analysis_results = None
            intermediate_results = processing_result.get("intermediate_results", {})
            
            for proc_name, results in intermediate_results.items():
                if proc_name == "data_analyzer" and "results" in results:
                    analysis_results = results["results"]
                    break
            
            if not analysis_results:
                return {"success": False, "error": "未生成分析结果"}
            
            analysis_results = self._normalize_analysis_results(analysis_results)
            analysis_results["system_health"] = {
                "status": "normal" if processing_result.get("success") else "error",
                "successful_collectors": 0,
                "failed_collectors": 0,
                "processing_success": True
            }
            
            # 构建统计信息
            stats = {
                "input_items": len(work_items),
                "processed_items": len(processing_result.get("processed_items", [])),
                "workflow_stages": len(workflow),
                "execution_time_ms": processing_result.get("execution_time_ms", 0),
                "analysis_sections": len(analysis_results) if analysis_results else 0
            }
            
            return {
                "success": True,
                "processed_items": processing_result.get("processed_items", []),
                "analysis_results": analysis_results,
                "processing_summary": processing_result.get("summary", {}),
                "stats": stats
            }
            
        except Exception as e:
            self.logger.error(f"数据处理失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _normalize_analysis_results(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """规范化分析结果，适配报告格式化器"""
        summary_stats = analysis_results.get("summary_statistics", {})
        overall = summary_stats.get("overall", {})
        averages = summary_stats.get("averages", {})
        if "overview" not in analysis_results:
            analysis_results["overview"] = {
                "total_work_items": overall.get("total_work_items", analysis_results.get("metadata", {}).get("total_items", 0)),
                "total_duration_hours": overall.get("total_duration_hours", 0),
                "unique_tools": overall.get("unique_tools", 0),
                "unique_categories": overall.get("unique_categories", 0),
                "average_duration_minutes": averages.get("avg_duration_minutes", 0),
                "completion_rate_percent": overall.get("completion_rate_percent", 0)
            }
        if "key_insights" not in analysis_results:
            insights = analysis_results.get("insights", [])
            key_insights = []
            if isinstance(insights, dict):
                for values in insights.values():
                    if isinstance(values, list):
                        key_insights.extend(values)
            elif isinstance(insights, list):
                key_insights = insights
            analysis_results["key_insights"] = key_insights
        return analysis_results
    
    def _format_report(self, analysis_results: Dict[str, Any], 
                      report_type: str) -> Dict[str, Any]:
        """格式化报告"""
        if not self.report_formatter:
            return {"success": False, "error": "报告格式化器未初始化"}
        
        try:
            # 映射报告类型到格式名称
            format_mapping = {
                "daily": "daily_work_summary",
                "detailed": "detailed_work_report",
                "executive": "executive_work_summary"
            }
            
            format_name = format_mapping.get(report_type, "daily_work_summary")
            
            # 格式化报告
            if hasattr(self.report_formatter, "format_report"):
                report_content = self.report_formatter.format_report(analysis_results, format_name)
            else:
                report_content = self.report_formatter.format(analysis_results, format_name)
            
            report_format = self.report_formatter.report_formats.get(format_name)
            sections = getattr(report_format, "sections", []) if report_format else []
            
            # 构建统计信息
            stats = {
                "report_type": report_type,
                "format_name": format_name,
                "content_length": len(report_content),
                "sections_count": len(sections),
                "generated_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "report_content": report_content,
                "format_name": format_name,
                "stats": stats
            }
            
        except Exception as e:
            self.logger.error(f"报告格式化失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _build_report_filename(self, report_type: str, time_range: Dict[str, Any] = None) -> str:
        if not time_range:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"{report_type}_report_{timestamp}.md"

        start_time = datetime.fromisoformat(time_range["start_time"])
        end_time = datetime.fromisoformat(time_range["end_time"])
        if start_time.time() == datetime.min.time() and end_time.time().strftime("%H:%M:%S") == "23:59:59":
            return f"{report_type}_report_{start_time.strftime('%Y%m%d')}_{end_time.strftime('%Y%m%d')}.md"
        return f"{report_type}_report_{start_time.strftime('%Y%m%d_%H%M%S')}_{end_time.strftime('%Y%m%d_%H%M%S')}.md"

    def _save_report(self, report_content: str, execution_id: str, 
                    report_type: str, time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """保存报告"""
        try:
            # 生成文件名
            filename = self._build_report_filename(report_type, time_range)
            
            # 保存路径
            reports_dir = "./data/reports/"
            os.makedirs(reports_dir, exist_ok=True)
            
            filepath = os.path.join(reports_dir, filename)
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            # 备份
            if self.config.get("enable_backup"):
                backup_dir = self.config.get("backup_path", "./data/reports/backup/")
                os.makedirs(backup_dir, exist_ok=True)
                
                backup_filepath = os.path.join(backup_dir, filename)
                with open(backup_filepath, 'w', encoding='utf-8') as f:
                    f.write(report_content)
            
            # 记录报告历史
            report_record = {
                "execution_id": execution_id,
                "report_type": report_type,
                "filename": filename,
                "filepath": filepath,
                "content_length": len(report_content),
                "saved_at": datetime.now().isoformat()
            }
            
            self.report_history.append(report_record)
            
            # 限制历史记录数量
            max_history = self.config.get("max_report_history", 30)
            if len(self.report_history) > max_history:
                self.report_history = self.report_history[-max_history:]
            
            return {
                "success": True,
                "filename": filename,
                "filepath": filepath,
                "saved_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"保存报告失败: {e}")
            return {"success": False, "error": str(e)}
    
    def push_report(self, execution_id: str, target: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        推送报告到飞书
        
        Args:
            execution_id: 执行ID
            target: 推送目标
            
        Returns:
            推送结果
        """
        if not self.feishu_pusher:
            return {"success": False, "error": "飞书推送器未初始化"}
        
        self.logger.info(f"推送报告到飞书，执行ID: {execution_id}")
        
        # 查找报告
        report_record = None
        for record in self.report_history:
            if record.get("execution_id") == execution_id:
                report_record = record
                break
        
        if not report_record:
            return {"success": False, "error": f"未找到执行ID为 {execution_id} 的报告"}
        
        # 读取报告内容
        try:
            with open(report_record["filepath"], 'r', encoding='utf-8') as f:
                report_content = f.read()
        except Exception as e:
            return {"success": False, "error": f"读取报告文件失败: {e}"}
        
        # 确定推送目标
        if not target:
            report_type = report_record.get("report_type", "daily")
            report_config = self.config.get("report_types", {}).get(report_type, {})
            target = report_config.get("target", {})
        
        # 推送报告
        message_type = "daily_work_report" if report_record.get("report_type", "daily") == "daily" else "work_report"
        if hasattr(self.feishu_pusher, "send_work_report"):
            push_result = self.feishu_pusher.send_work_report(
                report_content=report_content,
                report_type=report_record.get("report_type", "daily"),
                target=target
            )
        else:
            push_result = self.feishu_pusher.send_message(
                content=report_content,
                message_type=message_type,
                target=target
            )
        
        # 记录推送结果
        push_record = {
            "execution_id": execution_id,
            "push_time": datetime.now().isoformat(),
            "target": target,
            "result": push_result
        }
        
        # 更新报告记录
        report_record["push_records"] = report_record.get("push_records", [])
        report_record["push_records"].append(push_record)
        
        return push_result
    def _handle_error(self, execution_id: str, error_type: str, 
                     error_details: Any) -> Dict[str, Any]:
        """处理错误"""
        error_record = {
            "execution_id": execution_id,
            "error_type": error_type,
            "error_details": str(error_details),
            "occurred_at": datetime.now().isoformat(),
            "component": "report_manager"
        }
        
        self.logger.error(f"{error_type}: {error_details}")
        
        # 保存错误记录
        error_dir = "./data/errors/"
        os.makedirs(error_dir, exist_ok=True)
        
        error_filename = f"error_{execution_id}.json"
        error_filepath = os.path.join(error_dir, error_filename)
        
        try:
            with open(error_filepath, 'w', encoding='utf-8') as f:
                json.dump(error_record, f, ensure_ascii=False, indent=2)
        except:
            pass
        
        return {
            "success": False,
            "execution_id": execution_id,
            "error_type": error_type,
            "error_details": str(error_details),
            "error_file": error_filepath,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_report_summary(self, collection_result: Dict[str, Any],
                                processing_result: Dict[str, Any],
                                formatting_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成报告摘要"""
        collection_stats = collection_result.get("stats", {})
        processing_stats = processing_result.get("stats", {})
        formatting_stats = formatting_result.get("stats", {})
        
        analysis_results = processing_result.get("analysis_results", {})
        metadata = analysis_results.get("metadata", {})
        summary_stats = analysis_results.get("summary_statistics", {})
        
        return {
            "data_collection": {
                "total_work_items": collection_stats.get("total_items", 0),
                "successful_collectors": collection_stats.get("successful_collectors", 0),
                "failed_collectors": collection_stats.get("failed_collectors", 0),
                "collection_time_ms": collection_stats.get("collection_time_ms", 0)
            },
            "data_processing": {
                "input_items": processing_stats.get("input_items", 0),
                "processed_items": processing_stats.get("processed_items", 0),
                "workflow_stages": processing_stats.get("workflow_stages", 0),
                "processing_time_ms": processing_stats.get("execution_time_ms", 0),
                "analysis_sections": processing_stats.get("analysis_sections", 0)
            },
            "report_formatting": {
                "report_type": formatting_stats.get("report_type", "unknown"),
                "format_name": formatting_stats.get("format_name", "unknown"),
                "content_length": formatting_stats.get("content_length", 0),
                "generated_at": formatting_stats.get("generated_at", "")
            },
            "work_analysis": {
                "total_items_analyzed": metadata.get("total_items", 0),
                "time_range_days": metadata.get("time_range", {}).get("days", 0),
                "total_duration_hours": summary_stats.get("overall", {}).get("total_duration_hours", 0),
                "unique_tools": summary_stats.get("overall", {}).get("unique_tools", 0),
                "unique_categories": summary_stats.get("overall", {}).get("unique_categories", 0)
            }
        }
    
    def _record_execution(self, execution_id: str, result: Dict[str, Any]) -> None:
        """记录执行历史"""
        execution_record = {
            "execution_id": execution_id,
            "report_type": result.get("report_type"),
            "success": result.get("success", False),
            "execution_time_seconds": result.get("execution_time_seconds", 0),
            "start_time": result.get("start_time"),
            "end_time": result.get("end_time"),
            "work_items_count": result.get("collection_stats", {}).get("total_items", 0),
            "recorded_at": datetime.now().isoformat()
        }
        
        self.execution_history.append(execution_record)
        
        # 限制历史记录数量
        max_history = self.config.get("max_execution_history", 100)
        if len(self.execution_history) > max_history:
            self.execution_history = self.execution_history[-max_history:]
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.execution_history[-limit:] if self.execution_history else []
    
    def get_report_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取报告历史"""
        return self.report_history[-limit:] if self.report_history else []
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        components_status = {
            "collector_manager": bool(self.collector_manager),
            "processor_manager": bool(self.processor_manager),
            "report_formatter": bool(self.report_formatter),
            "feishu_pusher": bool(self.feishu_pusher)
        }
        
        # 测试飞书连接
        feishu_status = "unknown"
        if self.feishu_pusher:
            try:
                test_result = self.feishu_pusher.test_connection()
                feishu_status = "connected" if test_result.get("success") else "disconnected"
            except:
                feishu_status = "error"
        
        return {
            "system": "统一工作记录系统",
            "version": "1.0.0",
            "status": "operational" if all(components_status.values()) else "partial",
            "components": components_status,
            "feishu_connection": feishu_status,
            "execution_history_count": len(self.execution_history),
            "report_history_count": len(self.report_history),
            "last_execution": self.execution_history[-1] if self.execution_history else None,
            "last_report": self.report_history[-1] if self.report_history else None,
            "checked_at": datetime.now().isoformat()
        }
    
    def run_daily_report(self, time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """运行每日报告"""
        self.logger.info("开始运行每日工作报告")
        
        # 生成报告
        report_result = self.generate_report("daily", time_range)
        
        if not report_result.get("success"):
            self.logger.error(f"每日报告生成失败: {report_result.get('error_details')}")
            return report_result
        
        # 推送报告
        execution_id = report_result.get("execution_id")
        push_result = self.push_report(execution_id)
        
        # 合并结果
        final_result = {
            "success": report_result.get("success") and push_result.get("success"),
            "execution_id": execution_id,
            "report_type": "daily",
            "time_range": time_range,
            "report_generation": report_result,
            "report_push": push_result,
            "analysis_results": report_result.get("analysis_results", {}),
            "collection_stats": report_result.get("collection_stats", {}),
            "processing_stats": report_result.get("processing_stats", {}),
            "save_result": report_result.get("save_result", {}),
            "summary": {
                "work_items_analyzed": report_result.get("collection_stats", {}).get("total_items", 0),
                "report_content_length": len(report_result.get("report_content", "")),
                "push_success": push_result.get("success", False),
                "total_execution_time": report_result.get("execution_time_seconds", 0),
                "completed_at": datetime.now().isoformat()
            }
        }
        
        if final_result["success"]:
            self.logger.info("✅ 每日工作报告运行成功")
        else:
            self.logger.error("❌ 每日工作报告运行失败")
        
        return final_result
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """清理旧数据"""
        self.logger.info(f"清理 {days_to_keep} 天前的旧数据")
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cutoff_timestamp = cutoff_date.timestamp()
            
            # 清理报告文件
            reports_dir = "./data/reports/"
            backup_dir = "./data/reports/backup/"
            
            cleaned_files = []
            error_files = []
            
            for directory in [reports_dir, backup_dir]:
                if os.path.exists(directory):
                    for filename in os.listdir(directory):
                        filepath = os.path.join(directory, filename)
                        
                        # 检查文件修改时间
                        try:
                            file_mtime = os.path.getmtime(filepath)
                            
                            if file_mtime < cutoff_timestamp:
                                os.remove(filepath)
                                cleaned_files.append(filepath)
                        except Exception as e:
                            error_files.append({"file": filepath, "error": str(e)})
            
            # 清理错误文件
            error_dir = "./data/errors/"
            if os.path.exists(error_dir):
                for filename in os.listdir(error_dir):
                    filepath = os.path.join(error_dir, filename)
                    
                    try:
                        file_mtime = os.path.getmtime(filepath)
                        
                        if file_mtime < cutoff_timestamp:
                            os.remove(filepath)
                            cleaned_files.append(filepath)
                    except Exception as e:
                        error_files.append({"file": filepath, "error": str(e)})
            
            return {
                "success": True,
                "cutoff_date": cutoff_date.isoformat(),
                "cleaned_files_count": len(cleaned_files),
                "cleaned_files": cleaned_files[:20],  # 只显示前20个
                "error_files_count": len(error_files),
                "error_files": error_files,
                "cleaned_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"数据清理失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "cleaned_at": datetime.now().isoformat()
            }
    
    def export_config(self) -> Dict[str, Any]:
        """导出当前配置"""
        return {
            "system_config": self.config,
            "feishu_config": {
                "app_id": self.feishu_pusher.app_id if self.feishu_pusher else None,
                "default_chat_id": self.feishu_pusher.config.get("default_chat_id") if self.feishu_pusher else None
            },
            "data_sources": self.config.get("data_sources", []),
            "processing_workflow": self.config.get("processing_workflow", []),
            "report_types": self.config.get("report_types", {}),
            "exported_at": datetime.now().isoformat()
        }


def create_report_manager(config: Dict[str, Any] = None) -> ReportManager:
    """创建报告管理器"""
    return ReportManager(config)
