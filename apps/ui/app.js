const runBtn = document.getElementById("runBtn");
const result = document.getElementById("result");
const llmOutput = document.getElementById("llmOutput");
const memorySnapshot = document.getElementById("memorySnapshot");
const retrievedContext = document.getElementById("retrievedContext");
const qualityReport = document.getElementById("qualityReport");
const loading = document.getElementById("loading");
const errorBox = document.getElementById("errorBox");
const projectIdInput = document.getElementById("projectId");
const copyAllBtn = document.getElementById("copyAllBtn");
const copyCodeBtn = document.getElementById("copyCodeBtn");
const copyTestBtn = document.getElementById("copyTestBtn");
const testOutput = document.getElementById("testOutput");
const runMeta = document.getElementById("runMeta");
const runHistory = document.getElementById("runHistory");
const promptList = document.getElementById("promptList");
const memoryStats = document.getElementById("memoryStats");
const apiStatus = document.getElementById("apiStatus");
const mcpStatus = document.getElementById("mcpStatus");
const refreshOpsBtn = document.getElementById("refreshOpsBtn");
const clearRunsBtn = document.getElementById("clearRunsBtn");

const REQUEST_TIMEOUT_MS = 30000;

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
  llmOutput.textContent = "출력을 기다리는 중...";
  testOutput.textContent = "테스트를 기다리는 중...";
  memorySnapshot.textContent = "메모리 스냅샷이 없습니다.";
  retrievedContext.innerHTML = "<li>검색된 컨텍스트가 없습니다.</li>";
  qualityReport.innerHTML = "<p style='color: var(--text-secondary); font-size: 13px;'>리포트가 없습니다.</p>";
  runMeta.innerHTML = "<div class='meta-item'>실행 메타데이터가 없습니다.</div>";
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

async function fetchJson(path, options = {}, timeoutMs = REQUEST_TIMEOUT_MS) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(path, { ...options, signal: controller.signal });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.detail || `HTTP ${res.status}`);
    }
    return data;
  } finally {
    clearTimeout(timeoutId);
  }
}

function renderContext(items) {
  retrievedContext.innerHTML = "";
  if (!items || items.length === 0) {
    const li = document.createElement("li");
    li.textContent = "검색된 컨텍스트가 없습니다.";
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
  if (status === "ok" || status === "passed") return "OK";
  if (status === "error" || status === "failed") return "ERR";
  if (status === "violations") return "WARN";
  return "SKIP";
}

function getStatusText(status) {
  const mapping = {
    ok: "통과",
    passed: "통과",
    error: "오류",
    failed: "실패",
    violations: "경고",
    skipped: "스킵",
    unknown: "미확인",
  };
  return mapping[status] || status;
}

function formatDetail(tool, detail) {
  if (tool === "lint") {
    const count = detail.count || 0;
    if (count === 0) return "린트 문제가 없습니다.";
    return `린트 이슈 ${count}건`;
  }
  if (tool === "test") {
    const summary = detail.summary || {};
    const passed = summary.passed || 0;
    const failed = summary.failed || 0;
    if (passed === 0 && failed === 0) return "테스트 실행 결과 없음";
    return `통과 ${passed}, 실패 ${failed}`;
  }
  if (tool === "coverage") {
    const pct = detail.coverage_percent;
    if (pct === null || pct === undefined) return "커버리지 정보 없음";
    return `커버리지: ${pct}%`;
  }
  return JSON.stringify(detail);
}

function renderQuality(report) {
  qualityReport.innerHTML = "";
  const tools = [
    { key: "lint", label: "Lint" },
    { key: "test", label: "Tests" },
    { key: "coverage", label: "Coverage" },
  ];

  tools.forEach(({ key, label }) => {
    const data = report?.[key] || { status: "unknown", detail: {} };
    const card = document.createElement("div");
    card.className = "report-card";

    const header = document.createElement("div");
    header.textContent = label;

    const badge = document.createElement("span");
    const status = data.status || "unknown";
    badge.className = `status ${status}`;
    badge.textContent = `${getStatusIcon(status)} ${getStatusText(status)}`;
    header.appendChild(badge);

    const detailText = document.createElement("div");
    detailText.style.fontSize = "12px";
    detailText.style.color = "var(--text-secondary)";
    detailText.style.marginTop = "8px";
    detailText.textContent = formatDetail(key, data.detail);

    card.appendChild(header);
    card.appendChild(detailText);

    if (Object.keys(data.detail).length > 0) {
      const details = document.createElement("details");
      details.style.marginTop = "8px";
      const summary = document.createElement("summary");
      summary.textContent = "상세 정보";
      summary.style.cursor = "pointer";
      summary.style.fontSize = "11px";
      summary.style.color = "var(--accent)";
      const pre = document.createElement("pre");
      pre.textContent = JSON.stringify(data.detail, null, 2);
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
  html = html.replace(/("([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\')/g, (m) => {
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
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
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
    llmOutput.textContent = "(응답 없음)";
    testOutput.textContent = "(테스트 없음)";
    return;
  }
  const blocks = extractCodeBlocks(text);
  if (blocks.length === 0) {
    llmOutput.textContent = text;
    testOutput.textContent = "(테스트 없음)";
    return;
  }
  llmOutput.innerHTML = `<code>${highlightPython(blocks[0])}</code>`;
  if (blocks[1]) {
    testOutput.innerHTML = `<code>${highlightPython(blocks[1])}</code>`;
  } else {
    testOutput.textContent = "(테스트 없음)";
  }
}

function renderRunMeta(data) {
  runMeta.innerHTML = "";
  const items = [
    { label: "실행 ID", value: data.run_id || "-" },
    { label: "소요 시간", value: data.duration_ms ? `${data.duration_ms} ms` : "-" },
    { label: "프로젝트", value: data.project_id || "-" },
    { label: "작업", value: data.task_type || "-" },
  ];
  items.forEach((item) => {
    const div = document.createElement("div");
    div.className = "meta-item";
    div.innerHTML = `<strong>${item.label}</strong><span>${item.value}</span>`;
    runMeta.appendChild(div);
  });
}

function renderRuns(records) {
  runHistory.innerHTML = "";
  if (!records || records.length === 0) {
    const empty = document.createElement("div");
    empty.className = "history-item";
    empty.textContent = "실행 기록이 없습니다.";
    runHistory.appendChild(empty);
    return;
  }
  records.forEach((run) => {
    const item = document.createElement("div");
    item.className = "history-item";

    const title = document.createElement("div");
    title.textContent = run.user_input.slice(0, 90) || "(빈 요청)";

    const meta = document.createElement("div");
    meta.className = "meta";
    const created = run.created_at ? new Date(run.created_at).toLocaleString("ko-KR") : "-";
    meta.textContent = `${run.task_type} | ${run.project_id} | ${created} | ${run.duration_ms} ms`;

    const loadBtn = document.createElement("button");
    loadBtn.textContent = "불러오기";
    loadBtn.addEventListener("click", () => {
      document.getElementById("taskType").value = run.task_type;
      projectIdInput.value = run.project_id;
      document.getElementById("userInput").value = run.user_input;
      window.scrollTo({ top: 0, behavior: "smooth" });
    });

    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "삭제";
    deleteBtn.className = "ghost";
    deleteBtn.addEventListener("click", async () => {
      await fetchJson(`/runs/${run.id}`, { method: "DELETE" });
      await loadOps();
    });

    item.appendChild(title);
    item.appendChild(meta);
    item.appendChild(loadBtn);
    item.appendChild(deleteBtn);
    runHistory.appendChild(item);
  });
}

function renderPrompts(prompts) {
  promptList.innerHTML = "";
  if (!prompts || prompts.length === 0) {
    promptList.innerHTML = "<div class='prompt-item'>프롬프트가 없습니다.</div>";
    return;
  }
  prompts.forEach((prompt) => {
    const div = document.createElement("div");
    div.className = "prompt-item";
    const label = `${prompt.type} / ${prompt.version}`;
    const desc = prompt.description || "설명 없음";
    div.innerHTML = `<strong>${label}</strong><span>${desc}</span>`;
    promptList.appendChild(div);
  });
}

function renderMemoryStats(stats) {
  memoryStats.innerHTML = "";
  if (!stats) {
    memoryStats.innerHTML = "<div class='stat-item'>통계가 없습니다.</div>";
    return;
  }
  const items = [
    { label: "프로젝트 수", value: stats.project_count },
    { label: "엔트리 수", value: stats.total_entries },
    { label: "히스토리 수", value: stats.total_history_items },
    { label: "최근 업데이트", value: stats.latest_update ? new Date(stats.latest_update).toLocaleString("ko-KR") : "-" },
  ];
  items.forEach((item) => {
    const div = document.createElement("div");
    div.className = "stat-item";
    div.innerHTML = `<strong>${item.label}</strong><span>${item.value}</span>`;
    memoryStats.appendChild(div);
  });
}
async function loadStatus() {
  try {
    await fetchJson("/");
    apiStatus.textContent = "API: 정상";
  } catch {
    apiStatus.textContent = "API: 오프라인";
  }

  try {
    await fetchJson("http://localhost:8090/tool/lint", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ payload: { code: "" } }),
    }, 2000);
    mcpStatus.textContent = "MCP: 정상";
  } catch {
    mcpStatus.textContent = "MCP: 오프라인";
  }
}

async function loadOps() {
  try {
    const [runs, prompts, memStats] = await Promise.all([
      fetchJson("/runs?limit=20"),
      fetchJson("/prompts"),
      fetchJson("/memory/stats"),
    ]);
    renderRuns(runs);
    renderPrompts(prompts);
    renderMemoryStats(memStats);
  } catch (err) {
    setError(err.message || String(err));
  }
}

function validateRequest(taskType, userInput) {
  if (!taskType) return "작업 유형을 선택해주세요.";
  if (!userInput || userInput.trim().length < 3) return "요청 내용을 3자 이상 입력해주세요.";
  return "";
}

function validateResponse(data) {
  if (!data || typeof data !== "object") return "응답 형식이 올바르지 않습니다.";
  if (!("llm_output" in data)) return "응답 필드가 누락되었습니다.";
  return "";
}

copyAllBtn.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(result.textContent || "");
  } catch (err) {
    setError(`복사 실패: ${err}`);
  }
});

copyCodeBtn.addEventListener("click", async () => {
  try {
    const text = llmOutput.textContent || "";
    await navigator.clipboard.writeText(text);
  } catch (err) {
    setError(`복사 실패: ${err}`);
  }
});

copyTestBtn.addEventListener("click", async () => {
  try {
    const text = testOutput.textContent || "";
    await navigator.clipboard.writeText(text);
  } catch (err) {
    setError(`복사 실패: ${err}`);
  }
});

clearRunsBtn.addEventListener("click", async () => {
  if (!confirm("모든 실행 기록을 삭제할까요?")) {
    return;
  }
  const runs = await fetchJson("/runs?limit=50");
  for (const run of runs) {
    await fetchJson(`/runs/${run.id}`, { method: "DELETE" });
  }
  await loadOps();
});

refreshOpsBtn.addEventListener("click", async () => {
  await loadStatus();
  await loadOps();
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
    const data = await fetchJson("/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const respErr = validateResponse(data);
    if (respErr) {
      throw new Error(respErr);
    }

    renderCodeBlocks(data.llm_output || "");
    memorySnapshot.textContent = data.memory_snapshot || "(비어 있음)";
    renderContext(data.retrieved_context || []);
    renderQuality(data.quality_report || {});
    renderRunMeta({
      run_id: data.run_id,
      duration_ms: data.duration_ms,
      project_id: payload.project_id,
      task_type: payload.task_type,
    });
    result.textContent = JSON.stringify(data, null, 2);

    await loadOps();
    document.getElementById("results").scrollIntoView({ behavior: "smooth" });
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
  setLoading(false);
  clearResult();
  loadStatus();
  loadOps();
}

init();
