#!/usr/bin/env python3
"""
简单 lark-cli 飞书推送器
使用 lark-cli 命令行工具发送飞书消息
"""

import subprocess
import json
import logging
import time
import os
from datetime import datetime
from typing import Dict, Any, List


class LarkCliPusher:
    """使用 lark-cli 的飞书推送器"""
    
    def __init__(self, name: str = "lark_cli_pusher", config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"pusher.{name}")
        
        # 飞书配置
        self.app_id = config.get("app_id", "")
        self.app_secret = config.get("app_secret", "")
        self.default_chat_id = config.get("default_chat_id", "")
        self.test_mode = config.get("test_mode", True)  # 默认测试模式
        
        # 检查 lark-cli
        self._check_lark_cli()
        
        self.logger.info(f"lark-cli 推送器初始化完成")
    
    def _check_lark_cli(self):
        """检查 lark-cli 是否可用"""
        try:
            result = subprocess.run(['lark-cli', '--version'], 
                                  capture_output=True, text=True, shell=False)
            if result.returncode == 0:
                self.logger.info(f"✅ lark-cli 可用: {result.stdout.strip()}")
                return True
            else:
                self.logger.error(f"❌ lark-cli 不可用: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"❌ 检查 lark-cli 失败: {e}")
            return False
    
    def send_via_lark_cli(self, content: str, chat_id: str = None) -> Dict[str, Any]:
        """使用 lark-cli 发送消息"""
        chat_id = chat_id or self.default_chat_id
        if not chat_id:
            return {"success": False, "error": "未指定聊天ID"}
        
        if self.test_mode:
            self.logger.info(f"[测试模式] 模拟发送消息到 {chat_id}")
            self.logger.info(f"[测试模式] 消息长度: {len(content)} 字符")
            return {
                "success": True,
                "message_id": f"test_{int(time.time())}",
                "chat_id": chat_id,
                "content_length": len(content),
                "test_mode": True
            }
        
        try:
            # 构建 lark-cli 命令
            message_data = {
                "receive_id": chat_id,
                "msg_type": "text",
                "content": json.dumps({"text": content}, ensure_ascii=False)
            }
            
            command = [
                'lark-cli', 'api', 'post', '/open-apis/im/v1/messages',
                '--params', json.dumps({"receive_id_type": "chat_id"}),
                '--data', json.dumps(message_data)
            ]
            
            self.logger.debug(f"执行命令: {' '.join(command[:6])} ...")
            
            # 执行命令
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout)
                    if response.get("code") == 0:
                        message_id = response.get("data", {}).get("message_id")
                        self.logger.info(f"✅ 消息发送成功，消息ID: {message_id}")
                        return {
                            "success": True,
                            "message_id": message_id,
                            "chat_id": chat_id,
                            "content_length": len(content),
                            "response": response
                        }
                    else:
                        error_msg = response.get("msg", "未知错误")
                        self.logger.error(f"❌ 飞书API返回错误: {error_msg}")
                        return {"success": False, "error": error_msg, "response": response}
                except json.JSONDecodeError:
                    self.logger.error(f"❌ 响应不是有效的JSON: {result.stdout[:200]}")
                    return {"success": False, "error": "无效的JSON响应", "output": result.stdout[:200]}
            else:
                self.logger.error(f"❌ lark-cli 执行失败: {result.stderr}")
                return {"success": False, "error": result.stderr, "returncode": result.returncode}
                
        except subprocess.TimeoutExpired:
            self.logger.error("❌ lark-cli 执行超时")
            return {"success": False, "error": "执行超时"}
        except Exception as e:
            self.logger.error(f"❌ 发送消息异常: {e}")
            return {"success": False, "error": str(e)}
    
    def send_message(self, content: str, message_type: str = "daily_work_report", 
                    target: Dict[str, Any] = None) -> Dict[str, Any]:
        """发送消息（主接口）"""
        if not target:
            target = {
                "chat_id": self.default_chat_id,
                "description": "默认目标"
            }
        
        chat_id = target.get("chat_id")
        
        # 如果消息太长，自动拆分
        if len(content) > 4000:
            self.logger.info(f"消息过长({len(content)}字符)，自动拆分")
            return self._send_split_message(content, chat_id)
        else:
            self.logger.info(f"发送单条消息({len(content)}字符)")
            return self.send_via_lark_cli(content, chat_id)
    
    def _send_split_message(self, content: str, chat_id: str) -> Dict[str, Any]:
        """发送拆分的消息"""
        # 简单拆分逻辑
        chunks = []
        current_chunk = ""
        lines = content.split('\n')
        
        for line in lines:
            if len(current_chunk) + len(line) + 1 > 4000:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
            
            if current_chunk:
                current_chunk += "\n" + line
            else:
                current_chunk = line
        
        if current_chunk:
            chunks.append(current_chunk)
        
        self.logger.info(f"消息拆分为 {len(chunks)} 个块")
        
        results = []
        for i, chunk in enumerate(chunks):
            progress = f"📄 第 {i+1}/{len(chunks)} 部分\n"
            chunk_with_progress = progress + chunk
            
            result = self.send_via_lark_cli(chunk_with_progress, chat_id)
            results.append(result)
            
            if result.get("success"):
                self.logger.info(f"✅ 发送第 {i+1}/{len(chunks)} 部分成功")
            else:
                self.logger.error(f"❌ 发送第 {i+1}/{len(chunks)} 部分失败")
            
            # 延迟
            if i < len(chunks) - 1:
                time.sleep(1.0)
        
        success_count = sum(1 for r in results if r.get("success"))
        return {
            "success": success_count > 0,
            "total_chunks": len(chunks),
            "chunks_sent": success_count,
            "results": results
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """测试连接"""
        self.logger.info("测试 lark-cli 连接")
        
        test_content = (
            "🔧 飞书连接测试\n\n"
            "✅ 统一工作记录系统连接测试成功！\n\n"
            f"系统状态: 正常\n"
            f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"工具: lark-cli\n"
            f"测试模式: {'是' if self.test_mode else '否'}"
        )
        
        return self.send_message(test_content, "test_report", {
            "chat_id": self.default_chat_id,
            "description": "测试连接"
        })


def create_lark_cli_pusher(config: Dict[str, Any]) -> LarkCliPusher:
    """创建 lark-cli 推送器实例"""
    return LarkCliPusher("lark_cli_pusher", config)


if __name__ == "__main__":
    # 测试代码
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 lark-cli 飞书推送器测试")
    print("=" * 60)
    
    # 使用你提供的配置
    config = {
        "app_id": "${FEISHU_APP_ID}",
        "app_secret": "${FEISHU_APP_SECRET}",
        "default_chat_id": "${FEISHU_DEFAULT_CHAT_ID}",
        "test_mode": True  # 先测试模式
    }
    
    pusher = create_lark_cli_pusher(config)
    
    print(f"✅ 推送器创建成功")
    print(f"   应用ID: {config['app_id']}")
    print(f"   目标群聊: {config['default_chat_id']}")
    print(f"   测试模式: {config['test_mode']}")
    
    # 测试连接
    print("\n🔗 测试连接...")
    test_result = pusher.test_connection()
    
    if test_result.get("success"):
        print("✅ 连接测试成功")
        print(f"   消息ID: {test_result.get('message_id', 'N/A')}")
        print(f"   测试模式: {test_result.get('test_mode', False)}")
    else:
        print(f"❌ 连接测试失败: {test_result.get('error')}")
    
    print("\n" + "=" * 60)
    print("📋 使用说明:")
    print("1. 设置 test_mode: False 启用实际发送")
    print("2. 确保 lark-cli 已配置应用凭证")
    print("3. 长消息会自动拆分发送")