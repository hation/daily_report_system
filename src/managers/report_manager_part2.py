if False:
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
    
    def run_daily_report(self) -> Dict[str, Any]:
        """运行每日报告"""
        self.logger.info("开始运行每日工作报告")
        
        # 生成报告
        report_result = self.generate_report("daily")
        
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
            "report_generation": report_result,
            "report_push": push_result,
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