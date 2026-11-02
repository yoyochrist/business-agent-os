"""Local browser prototype using official authenticated CLI executables; no provider SDK."""
import json
import secrets
import hmac
import sys
import os
import shutil
import sqlite3
import subprocess
import threading
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
DATA_ROOT = Path.home() / ".business-agent-os"
DB = DATA_ROOT / "tasks.db"
ROLES = ("business", "pm", "hr", "accountant", "finance", "sales", "marketing", "knowledge", "approvals")
MAX_PROMPT = 12000
SESSION_TOKEN = secrets.token_urlsafe(32)

def init_db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB) as db:
        db.execute("CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, role TEXT NOT NULL, provider TEXT NOT NULL, prompt TEXT NOT NULL, status TEXT NOT NULL, result TEXT NOT NULL)")

def update_task(task_id, status, result):
    with sqlite3.connect(DB) as db:
        db.execute("UPDATE tasks SET status=?, result=? WHERE id=?", (status, result, task_id))

def execute_task(task_id, role, provider, prompt):
    skill = (ROOT / ".agents" / "skills" / role / "SKILL.md").read_text(encoding="utf-8")
    instruction = (
        "Perform a draft-only business task. Do not send messages, execute payments, "
        "publish, or change external files. Do not inspect credential stores.\n"
        + skill + "\nUser task:\n" + prompt
    )
    try:
        if provider == "codex":
            argv = ["codex", "exec", "--skip-git-repo-check", "-"]
        elif provider == "claude":
            argv = ["claude", "-p"]
        else:
            raise ValueError("Unsupported provider")
        result = subprocess.run(
            argv, cwd=ROOT, input=instruction, capture_output=True, text=True, timeout=180,
            env={**os.environ, "NO_COLOR": "1"}, check=False
        )
        output = result.stdout if result.returncode == 0 else "CLI error: " + (result.stderr or result.stdout)
        update_task(task_id, "completed" if result.returncode == 0 else "failed", (output or "(empty output)")[-60000:])
    except Exception as exc:
        update_task(task_id, "failed", type(exc).__name__ + ": " + str(exc))

HTML = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Business Agent OS</title><style>
body{font:16px system-ui;background:#f5f7fa;color:#17223b;padding:30px 15px}
main{max-width:820px;margin:auto;background:white;padding:30px;border-radius:18px;box-shadow:0 6px 28px #1112}
select,textarea{box-sizing:border-box;width:100%;padding:12px;border:1px solid #bec8d3;border-radius:8px;font:inherit;margin:8px 0 16px}
textarea{height:140px}label{font-weight:600;display:block}button{background:#175bcc;color:white;border:0;border-radius:9px;padding:12px 20px;cursor:pointer}
pre{white-space:pre-wrap;overflow-wrap:anywhere;padding:18px;background:#f5f7fa;border-radius:10px}
small{color:#657289}
</style></head><body><main><h1>Business Agent OS</h1>
<p>Run business-agent draft tasks through your existing signed-in Codex or Claude Code CLI.</p>
<small>Prototype only: no Graphify, network A2A, email sending, or Antigravity backend yet.</small>
<label>Provider</label><select id="provider"><option value="codex">Codex (local CLI sign-in)</option><option value="claude">Claude Code (local CLI sign-in)</option></select>
<label>Agent</label><select id="role"></select>
<label>Task</label><textarea id="prompt" placeholder="Prepare a delivery plan for this customer..."></textarea>
<button id="run">Run draft task</button><h2>Result</h2><pre id="result">No task yet.</pre>
</main><script>
const token=window.location.hash.startsWith("#token=") ? decodeURIComponent(window.location.hash.slice(7)) : sessionStorage.getItem("business-agent-token");
if(token) {sessionStorage.setItem("business-agent-token",token);history.replaceState(null,"",location.pathname);}
else {document.getElementById("result").textContent="Unauthorized session. Open the URL launched by Business Agent OS.";}
for(const role of ["business","pm","hr","accountant","finance","sales","marketing","knowledge","approvals"]){
const opt=document.createElement("option");opt.value=role;opt.textContent=role;document.getElementById("role").appendChild(opt)}
document.getElementById("run").addEventListener("click",async()=>{
const out=document.getElementById("result");if(!token){out.textContent="Missing session token. Relaunch the app.";return;}out.textContent="Starting...";
try{
const r=await fetch("/tasks",{method:"POST",headers:{"Content-Type":"application/json","X-Session-Token":token},body:JSON.stringify({
provider:document.getElementById("provider").value,role:document.getElementById("role").value,prompt:document.getElementById("prompt").value})});
const data=await r.json();if(!r.ok){out.textContent=data.error;return}
const poll=async()=>{const res=await fetch("/tasks/"+data.id,{headers:{"X-Session-Token":token}});const task=await res.json();
out.textContent=task.status==="running"?"Agent running...":task.result;
if(task.status==="running")setTimeout(poll,1500)};poll()
}catch(e){out.textContent=String(e)}
});
</script></body></html>"""

class Handler(BaseHTTPRequestHandler):
    def reply(self, code, data, content_type="application/json"):
        body = data.encode("utf-8") if isinstance(data, str) else json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def authorized(self):
        supplied = self.headers.get("X-Session-Token", "")
        return hmac.compare_digest(supplied, SESSION_TOKEN)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            return self.reply(200, HTML, "text/html; charset=utf-8")
        if path.startswith("/tasks/"):
            if not self.authorized():
                return self.reply(401, {"error": "Unauthorized"})
            with sqlite3.connect(DB) as db:
                db.row_factory = sqlite3.Row
                row = db.execute("SELECT id,role,provider,status,result FROM tasks WHERE id=?", (path.rsplit("/", 1)[-1],)).fetchone()
            return self.reply(200, dict(row)) if row else self.reply(404, {"error": "Not found"})
        return self.reply(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/tasks":
            return self.reply(404, {"error": "Not found"})
        if not self.authorized():
            return self.reply(401, {"error": "Unauthorized"})
        origin = self.headers.get("Origin")
        if origin not in (None, "http://127.0.0.1:8765", "http://localhost:8765"):
            return self.reply(403, {"error": "Invalid origin"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size < 1 or size > 16000:
                return self.reply(413, {"error": "Invalid payload size"})
            data = json.loads(self.rfile.read(size))
        except (ValueError, json.JSONDecodeError):
            return self.reply(400, {"error": "Invalid JSON"})
        role, provider, prompt = data.get("role"), data.get("provider"), data.get("prompt")
        if role not in ROLES or provider not in ("codex", "claude") or not isinstance(prompt, str) or not (1 <= len(prompt) <= MAX_PROMPT):
            return self.reply(400, {"error": "Invalid request"})
        if not shutil.which(provider):
            return self.reply(400, {"error": f"{provider} CLI not installed. Install it and sign in first."})
        task_id = str(uuid.uuid4())
        with sqlite3.connect(DB) as db:
            db.execute("INSERT INTO tasks VALUES(?,?,?,?,?,?)", (task_id, role, provider, prompt, "running", ""))
        threading.Thread(target=execute_task, args=(task_id, role, provider, prompt), daemon=True).start()
        return self.reply(201, {"id": task_id})

if __name__ == "__main__":
    init_db()
    print("Business Agent OS: http://127.0.0.1:8765")
    threading.Timer(0.8, lambda: webbrowser.open("http://127.0.0.1:8765/#token=" + SESSION_TOKEN)).start()
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
