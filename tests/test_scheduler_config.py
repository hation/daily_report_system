import plistlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def render_launch_agent_template():
    template_path = PROJECT_ROOT / "config" / "com.xingan.daily_report_system.plist.template"
    content = template_path.read_text(encoding="utf-8")
    content = content.replace("{{PROJECT_ROOT}}", str(PROJECT_ROOT))
    content = content.replace("{{LAUNCHD_PATH}}", "/usr/local/bin:/usr/bin:/bin")
    return plistlib.loads(content.encode("utf-8"))


def test_launch_agent_template_runs_daily_at_19():
    data = render_launch_agent_template()

    assert data["Label"] == "com.xingan.daily_report_system"
    assert data["ProgramArguments"] == [str(PROJECT_ROOT / "scripts" / "run_daily_report.sh")]
    assert data["WorkingDirectory"] == str(PROJECT_ROOT)
    assert data["StartCalendarInterval"] == [{"Hour": 19, "Minute": 0}]


def test_launch_agent_template_uses_placeholders():
    template_path = PROJECT_ROOT / "config" / "com.xingan.daily_report_system.plist.template"
    content = template_path.read_text(encoding="utf-8")

    assert "{{PROJECT_ROOT}}" in content
    assert "{{LAUNCHD_PATH}}" in content
    assert "/Users/" not in content


def test_daily_script_sources_local_env_and_exports_path():
    script = (PROJECT_ROOT / "scripts" / "run_daily_report.sh").read_text(encoding="utf-8")

    assert "config/local.env" in script
    assert "source \"$LOCAL_ENV_FILE\"" in script
    assert "FEISHU_DEFAULT_CHAT_ID" not in script
    assert "/Users/" not in script
    assert "python3 src/main.py --run-daily --env production" in script
