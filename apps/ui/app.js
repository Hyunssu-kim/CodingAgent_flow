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
const copyTestBtn = document.getElementById("copyTestBtn");
const testOutput = document.getElementById("testOutput");
const clearHistoryBtn = document.getElementById("clearHistoryBtn");
const darkToggle = document.getElementById("darkToggle");

const HISTORY_KEY = "daicp_history";
const REQUEST_TIMEOUT_MS = 30000;

function setError(message) {
  if (!message) {
    errorBox.classList.add("hidden");
    errorBox.textContent = "";
    return;
  }
  errorBox.textContent = `❌ ${message}`;
  errorBox.classList.remove("hidden");
}

function clearResult() {
  llmOutput.textContent = "결과가 여기에 표시됩니다.";
  testOutput.textContent = "테스트 케이스가 여기에 표시됩니다.";
  memorySnapshot.textContent = "설계 컨텍스트가 여기에 표시됩니다.";
  retrievedContext.innerHTML = "<li>검색된 문서가 여기에 표시됩니다.</li>";
  qualityReport.innerHTML = "<p style='color: var(--text-secondary); font-size: 14px;'>품질 검사 결과가 여기에 표시됩니다.</p>";
  result.textContent = "";
  setError("");
}

function setLoading(isLoading) {
  if (isLoading) {
    loading.classList.remove("hidden");
    runBtn.disabled = true;
  } else {
    loading.classList.add("hidden");
    runBtn.disabled = false;
  }
}

function renderContext(items) {
  retrievedContext.innerHTML = "";
  if (!items || items.length === 0) {
    const li = document.createElement("li");
    li.textContent = "(검색된 문서가 없습니다)";
    li.style.color = "var(--text-secondary)";
    retrievedContext.appendChild(li);
    return;
  }
  items.forEach((text) => {
    const li = document.createElement("li");
    li.textContent = text;
    retrievedContext.appendChild(li);
  });
}

function getStatusIcon(status) {
  if (status === "ok" || status === "passed") return "✓";
  if (status === "error" || status === "failed") return "✕";
  if (status === "violations") return "⚠";
  return "•";
}

function getStatusText(status) {
  const mapping = {
    ok: "통과",
    passed: "통과",
    error: "오류",
    failed: "실패",
    violations: "위반",
    skipped: "건너뜀",
    unknown: "알 수 없음",
  };
  return mapping[status] || status;
}

function formatDetail(tool, detail) {
  if (tool === "lint") {
    const count = detail.count || 0;
    if (count === 0) return "코드 스타일 문제 없음";
    return `${count}개의 스타일 문제 발견`;
  }
  if (tool === "test") {
    const summary = detail.summary || {};
    const passed = summary.passed || 0;
    const failed = summary.failed || 0;
    if (passed === 0 && failed === 0) return "테스트 없음";
    return `${passed}개 통과, ${failed}개 실패`;
  }
  if (tool === "coverage") {
    const pct = detail.coverage_percent;
    if (pct === null || pct === undefined) return "커버리지 정보 없음";
    return `코드 커버리지: ${pct}%`;
  }
  return JSON.stringify(detail);
}

function renderQuality(report) {
  qualityReport.innerHTML = "";
  const tools = [
    { key: "lint", label: "린트 검사", icon: "📝" },
    { key: "test", label: "테스트", icon: "🧪" },
    { key: "coverage", label: "커버리지", icon: "📊" },
  ];

  tools.forEach(({ key, label, icon }) => {
    const data = report?.[key] || { status: "unknown", detail: {} };
    const card = document.createElement("div");
    card.className = "report-card";

    const header = document.createElement("div");
    header.innerHTML = `${icon} ${label}`;

    const badge = document.createElement("span");
    const status = data.status || "unknown";
    badge.className = `status ${status}`;
    const statusIcon = document.createElement("span");
    statusIcon.className = "icon";
    statusIcon.textContent = getStatusIcon(status);
    badge.appendChild(statusIcon);
    badge.appendChild(document.createTextNode(getStatusText(status)));
    header.appendChild(badge);

    const detailText = document.createElement("div");
    detailText.style.fontSize = "13px";
    detailText.style.color = "var(--text-secondary)";
    detailText.style.marginTop = "8px";
    detailText.textContent = formatDetail(key, data.detail);

    card.appendChild(header);
    card.appendChild(detailText);

    // 상세 정보 (접을 수 있게)
    if (Object.keys(data.detail).length > 0) {
      const details = document.createElement("details");
      details.style.marginTop = "8px";
      const summary = document.createElement("summary");
      summary.textContent = "상세 정보";
      summary.style.cursor = "pointer";
      summary.style.fontSize = "12px";
      summary.style.color = "var(--accent)";
      const pre = document.createElement("pre");
      pre.textContent = JSON.stringify(data.detail, null, 2);
      pre.style.fontSize = "11px";
      pre.style.marginTop = "8px";
      details.appendChild(summary);
      details.appendChild(pre);
      card.appendChild(details);
    }

    qualityReport.appendChild(card);
  });
}

function highlightPython(code) {
  const placeholders = [];
  const stash = (html) => {
    const key = placeholders.length;
    placeholders.push(html);
    return `__HL_${key}__`;
  };

  let html = escapeHtml(code);
  html = html.replace(/(\"([^\"\\\\]|\\\\.)*\"|\'([^\'\\\\]|\\\\.)*\')/g, (m) => {
    return stash(`<span class="str">${m}</span>`);
  });
  html = html.replace(/(#.*)$/gm, (m) => stash(`<span class="com">${m}</span>`));
  html = html.replace(
    /\b(def|class|return|import|from|if|elif|else|for|while|try|except|with|as|lambda|yield|raise|True|False|None|async|await)\b/g,
    (m) => stash(`<span class="kw">${m}</span>`)
  );
  html = html.replace(/\b(\d+(\.\d+)?)\b/g, (m) => stash(`<span class="num">${m}</span>`));

  return html.replace(/__HL_(\d+)__/g, (_, idx) => placeholders[Number(idx)] || "");
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function extractCodeBlocks(text) {
  const blocks = [];
  const fence = /```(?:[a-zA-Z]+)?([\s\S]*?)```/g;
  let match;
  while ((match = fence.exec(text)) !== null) {
    blocks.push(match[1].trim());
  }
  return blocks;
}

function renderCodeBlocks(text) {
  if (!text) {
    llmOutput.textContent = "(AI 응답이 없습니다)";
    testOutput.textContent = "(테스트 케이스가 없습니다)";
    return;
  }
  const blocks = extractCodeBlocks(text);
  if (blocks.length === 0) {
    llmOutput.textContent = text;
    testOutput.textContent = "(테스트 케이스가 없습니다)";
    return;
  }
  llmOutput.innerHTML = `<code>${highlightPython(blocks[0])}</code>`;
  if (blocks[1]) {
    testOutput.innerHTML = `<code>${highlightPython(blocks[1])}</code>`;
  } else {
    testOutput.textContent = "(테스트 케이스가 없습니다)";
  }
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
    empty.textContent = "아직 실행 기록이 없습니다.";
    historyList.appendChild(empty);
    return;
  }

  history.forEach((h) => {
    const item = document.createElement("div");
    item.className = "history-item";

    const left = document.createElement("div");
    const taskTypeMap = {
      code_generation: "코드 생성",
      refactoring: "리팩토링",
      code_review: "코드 리뷰",
    };
    left.textContent = h.user_input.slice(0, 100) || "(입력 없음)";
    const meta = document.createElement("div");
    meta.className = "history-meta";
    meta.textContent = `${taskTypeMap[h.task_type] || h.task_type} • ${h.project_id} • ${new Date(h.ts).toLocaleString("ko-KR")}`;
    left.appendChild(meta);

    const btn = document.createElement("button");
    btn.className = "ghost";
    btn.textContent = "불러오기";
    btn.addEventListener("click", () => {
      document.getElementById("taskType").value = h.task_type;
      projectIdInput.value = h.project_id;
      document.getElementById("userInput").value = h.user_input;
      window.scrollTo({ top: 0, behavior: "smooth" });
    });

    item.appendChild(left);
    item.appendChild(btn);
    historyList.appendChild(item);
  });
}

function validateRequest(taskType, userInput) {
  if (!taskType) return "작업 유형을 선택해주세요.";
  if (!userInput || userInput.trim().length < 3) return "요청 사항을 3자 이상 입력해주세요.";
  return "";
}

function validateResponse(data) {
  if (!data || typeof data !== "object") return "응답 형식이 올바르지 않습니다.";
  if (!("llm_output" in data)) return "응답에 필수 필드가 없습니다.";
  return "";
}

copyAllBtn.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(result.textContent || "");
    alert("✓ 전체 내용이 복사되었습니다.");
  } catch (err) {
    setError(`복사 실패: ${err}`);
  }
});

copyCodeBtn.addEventListener("click", async () => {
  try {
    const text = llmOutput.textContent || "";
    await navigator.clipboard.writeText(text);
    alert("✓ 코드가 복사되었습니다.");
  } catch (err) {
    setError(`복사 실패: ${err}`);
  }
});

copyTestBtn.addEventListener("click", async () => {
  try {
    const text = testOutput.textContent || "";
    await navigator.clipboard.writeText(text);
    alert("✓ 테스트 케이스가 복사되었습니다.");
  } catch (err) {
    setError(`복사 실패: ${err}`);
  }
});

clearHistoryBtn.addEventListener("click", () => {
  if (confirm("정말로 모든 기록을 삭제하시겠습니까?")) {
    localStorage.removeItem(HISTORY_KEY);
    renderHistory();
    alert("✓ 기록이 삭제되었습니다.");
  }
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
    project_id: projectId,
  };

  clearResult();
  setLoading(true);

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    const res = await fetch("/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${res.status}`);
    }

    const data = await res.json();
    const respErr = validateResponse(data);
    if (respErr) {
      throw new Error(respErr);
    }

    renderCodeBlocks(data.llm_output || "");
    memorySnapshot.textContent = data.memory_snapshot || "(메모리 정보 없음)";
    renderContext(data.retrieved_context || []);
    renderQuality(data.quality_report || {});
    result.textContent = JSON.stringify(data, null, 2);

    saveHistory({
      task_type: taskType,
      project_id: projectId,
      user_input: userInput,
      ts: Date.now(),
    });

    // 결과 섹션으로 스크롤
    document.querySelector(".panel:nth-of-type(2)").scrollIntoView({ behavior: "smooth" });
  } catch (err) {
    if (err && err.name === "AbortError") {
      setError("요청 시간이 초과되었습니다. 다시 시도해주세요.");
    } else {
      setError(`${err.message || err}`);
    }
  } finally {
    setLoading(false);
  }
});

function init() {
  renderHistory();
  const dark = localStorage.getItem("daicp_dark") === "1";
  darkToggle.checked = dark;
  document.body.classList.toggle("dark", dark);
  setLoading(false);
  clearResult();
}

init();
