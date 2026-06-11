import json
from types import SimpleNamespace

from src.pushers.feishu_pusher import FeishuPusher


def test_feishu_pusher_uses_lark_cli_first(monkeypatch):
    calls = []

    def fake_run(command, capture_output, text, timeout):
        calls.append(command)
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps({"data": {"message_id": "om_test"}}),
            stderr="",
        )

    monkeypatch.setattr("src.pushers.feishu_pusher.shutil.which", lambda name: "/usr/local/bin/lark-cli")
    monkeypatch.setattr("src.pushers.feishu_pusher.subprocess.run", fake_run)

    pusher = FeishuPusher(config={"test_mode": False, "default_chat_id": "oc_test", "prefer_lark_cli": True})
    result = pusher.send_message("日报内容", target={"chat_id": "oc_test"})

    assert result["success"] is True
    assert result["message_id"] == "om_test"
    assert result["channel"] == "lark-cli"
    assert calls[0][:3] == ["lark-cli", "im", "+messages-send"]
    assert "--chat-id" in calls[0]
    assert "oc_test" in calls[0]


def test_feishu_pusher_reports_missing_chat_id_in_real_mode(monkeypatch):
    monkeypatch.setattr("src.pushers.feishu_pusher.shutil.which", lambda name: "/usr/local/bin/lark-cli")

    pusher = FeishuPusher(config={"test_mode": False, "prefer_lark_cli": True})
    result = pusher.send_message("日报内容", target={})

    assert result["success"] is False
    assert result["error"] == "未指定聊天ID"


def test_feishu_pusher_returns_cli_error_without_openapi_credentials(monkeypatch):
    def fake_run(command, capture_output, text, timeout):
        return SimpleNamespace(returncode=1, stdout="", stderr=json.dumps({"error": {"message": "chat not found"}}))

    monkeypatch.setattr("src.pushers.feishu_pusher.shutil.which", lambda name: "/usr/local/bin/lark-cli")
    monkeypatch.setattr("src.pushers.feishu_pusher.subprocess.run", fake_run)

    pusher = FeishuPusher(config={"test_mode": False, "default_chat_id": "oc_bad", "prefer_lark_cli": True})
    result = pusher.send_message("日报内容", target={"chat_id": "oc_bad"})

    assert result["success"] is False
    assert result["error"] == "chat not found"
    assert result["channel"] == "lark-cli"
