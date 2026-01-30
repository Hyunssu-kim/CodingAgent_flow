const runBtn = document.getElementById("runBtn");
const result = document.getElementById("result");
const llmOutput = document.getElementById("llmOutput");
const memorySnapshot = document.getElementById("memorySnapshot");
const retrievedContext = document.getElementById("retrievedContext");
const qualityReport = document.getElementById("qualityReport");
const loading = document.getElementById("loading");
const errorBox = document.getElementById("errorBox");
const projectIdInput = document.getElementById("projectId");
const historyList = document.getElementById("historyList");
const projectHistory = document.getElementById("projectHistory");
const copyAllBtn = document.getElementById("copyAllBtn");
const copyCodeBtn = document.getElementById("copyCodeBtn");
const clearHistoryBtn = document.getElementById("clearHistoryBtn");
const darkToggle = document.getElementById("darkToggle");

const HISTORY_KEY = "daicp_history";

function setError(message) {
  if (!message) {
    errorBox.classList.add("hidden");
    errorBox.textContent = "";
    return;
  }
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

function clearResult() {
  llmOutput.textContent = "";
  memorySnapshot.textContent = "";
  retrievedContext.innerHTML = "";
  qualityReport.innerHTML = "";
  result.textContent = "";
  setError("");
}

function renderContext(items) {
  retrievedContext.innerHTML = "";
  if (!items || items.length === 0) {
    const li = document.createElement("li");
    li.textContent = "(none)";
    retrievedContext.appendChild(li);
    return;
  }
  items.forEach((text) => {
    const li = document.createElement("li");
    li.textContent = text;
    retrievedContext.appendChild(li);
  });
}

function renderQuality(report) {
  qualityReport.innerHTML = "";
  const tools = ["lint", "test", "coverage"];
  tools.forEach((tool) => {
    const data = report?.[tool] || { status: "unknown", detail: {} };
    const card = document.createElement("div");
    card.className = "report-card";

    const title = document.createElement("div");
    title.textContent = tool.toUpperCase();

    const badge = document.createElement("span");
    const status = data.status || "unknown";
    badge.className = `status ${status}`;
    const icon = document.createElement("span");
    icon.className = "icon";
    icon.textContent = status === "ok" || status === "passed" ? "✓" : status === "error" || status === "failed" || status === "violations" ? "✕" : "•";
    badge.appendChild(icon);
    badge.appendChild(document.createTextNode(status));
    title.appendChild(badge);

    const detail = document.createElement("pre");
    detail.textContent = JSON.stringify(data.detail || {}, null, 2);

    card.appendChild(title);
    card.appendChild(detail);
    qualityReport.appendChild(card);
  });
}

function highlightPython(code) {
  let html = code
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  html = html.replace(/(#.*)$/gm, '<span class="com">$1</span>');
  html = html.replace(/(\"[^\"]*\"|\'[^\']*\')/g, '<span class="str">$1</span>');
  html = html.replace(/\b(\d+)\b/g, '<span class="num">$1</span>');
  html = html.replace(/\b(def|class|return|import|from|if|elif|else|for|while|try|except|with|as|lambda|yield|raise|True|False|None)\b/g, '<span class="kw">$1</span>');
  return html;
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function renderCodeBlocks(text) {
  if (!text) return;
  const fence = /```python([\s\S]*?)```/g;
  if (!fence.test(text)) {
    llmOutput.textContent = text;
    return;
  }

  let lastIndex = 0;
  let html = "";
  let match;
  fence.lastIndex = 0;
  while ((match = fence.exec(text)) !== null) {
    const before = text.slice(lastIndex, match.index);
    html += escapeHtml(before);
    html += `\n<code>${highlightPython(match[1].trim())}</code>\n`;
    lastIndex = fence.lastIndex;
  }
  html += escapeHtml(text.slice(lastIndex));
  llmOutput.innerHTML = html;
}

function getHistory() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
  } catch {
    return [];
  }
}

function saveHistory(entry) {
  const history = getHistory();
  history.unshift(entry);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(0, 20)));
  renderHistory();
}

function renderHistory() {
  const history = getHistory();
  historyList.innerHTML = "";
  projectHistory.innerHTML = "";

  const projects = new Set();
  history.forEach((h) => projects.add(h.project_id));
  projects.forEach((p) => {
    const opt = document.createElement("option");
    opt.value = p;
    projectHistory.appendChild(opt);
  });

  if (history.length === 0) {
    const empty = document.createElement("div");
    empty.className = "history-meta";
    empty.textContent = "No history yet.";
    historyList.appendChild(empty);
    return;
  }

  history.forEach((h) => {
    const item = document.createElement("div");
    item.className = "history-item";

    const left = document.createElement("div");
    left.textContent = h.user_input.slice(0, 80) || "(empty)";
    const meta = document.createElement("div");
    meta.className = "history-meta";
    meta.textContent = `${h.task_type} • ${h.project_id} • ${new Date(h.ts).toLocaleString()}`;
    left.appendChild(meta);

    const btn = document.createElement("button");
    btn.className = "ghost";
    btn.textContent = "Load";
    btn.addEventListener("click", () => {
      document.getElementById("taskType").value = h.task_type;
      projectIdInput.value = h.project_id;
      document.getElementById("userInput").value = h.user_input;
    });

    item.appendChild(left);
    item.appendChild(btn);
    historyList.appendChild(item);
  });
}

function validateRequest(taskType, userInput) {
  if (!taskType) return "Task type is required.";
  if (!userInput || userInput.trim().length < 3) return "User input must be at least 3 characters.";
  return "";
}

function validateResponse(data) {
  if (!data || typeof data !== "object") return "Invalid response format.";
  if (!("llm_output" in data)) return "Missing llm_output in response.";
  return "";
}

copyAllBtn.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(result.textContent || "");
  } catch (err) {
    setError(`Copy failed: ${err}`);
  }
});

copyCodeBtn.addEventListener("click", async () => {
  try {
    const text = llmOutput.textContent || "";
    await navigator.clipboard.writeText(text);
  } catch (err) {
    setError(`Copy failed: ${err}`);
  }
});

clearHistoryBtn.addEventListener("click", () => {
  localStorage.removeItem(HISTORY_KEY);
  renderHistory();
});

darkToggle.addEventListener("change", (e) => {
  document.body.classList.toggle("dark", e.target.checked);
  localStorage.setItem("daicp_dark", e.target.checked ? "1" : "0");
});

runBtn.addEventListener("click", async () => {
  const taskType = document.getElementById("taskType").value;
  const userInput = document.getElementById("userInput").value;
  const projectId = projectIdInput.value || "default";

  const err = validateRequest(taskType, userInput);
  if (err) {
    setError(err);
    return;
  }

  const payload = {
    task_type: taskType,
    user_input: userInput,
    project_id: projectId
  };

  clearResult();
  loading.classList.remove("hidden");

  try {
    const res = await fetch("/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    const data = await res.json();
    const respErr = validateResponse(data);
    if (respErr) {
      throw new Error(respErr);
    }
    renderCodeBlocks(data.llm_output || "");
    memorySnapshot.textContent = data.memory_snapshot || "";
    renderContext(data.retrieved_context || []);
    renderQuality(data.quality_report || {});
    result.textContent = JSON.stringify(data, null, 2);
    saveHistory({
      task_type: taskType,
      project_id: projectId,
      user_input: userInput,
      ts: Date.now()
    });
  } catch (err) {
    clearResult();
    setError(`Error: ${err}`);
  } finally {
    loading.classList.add("hidden");
  }
});

function init() {
  renderHistory();
  const dark = localStorage.getItem("daicp_dark") === "1";
  darkToggle.checked = dark;
  document.body.classList.toggle("dark", dark);
}

init();
