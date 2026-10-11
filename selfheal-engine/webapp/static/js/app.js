/**
 * SelfHeal Studio — Frontend Application Logic
 */

let currentVersion = 'b';
let isRunning = false;
let phaseTimer = null;

document.addEventListener('DOMContentLoaded', () => {
  fetchSystemStatus();
  loadIntents();
  loadRecipes();
  loadRunsHistory();

  // Periodic telemetry polling
  setInterval(fetchSystemStatus, 6000);
});

// -------------------------------------------------------------
// System Status & Telemetry
// -------------------------------------------------------------
async function fetchSystemStatus() {
  try {
    const res = await fetch('/api/status');
    if (!res.ok) return;
    const data = await res.json();

    // MongoDB status pill
    const mongoVal = document.getElementById('mongoVal');
    const mongoDot = document.getElementById('mongoDot');
    if (data.db && data.db.connected) {
      mongoVal.textContent = `Live (${data.db.runs_count} runs)`;
      mongoDot.className = 'status-dot dot-live';
    } else {
      mongoVal.textContent = data.db.backend === 'in_memory_fallback' ? 'In-Memory Mode' : 'Disconnected';
      mongoDot.className = 'status-dot dot-purple';
    }

    // Healer status pill
    const llmVal = document.getElementById('llmVal');
    const llmDot = document.getElementById('llmDot');
    if (data.llm) {
      llmVal.textContent = data.llm.mode;
      llmDot.className = data.llm.status === 'OK' ? 'status-dot dot-live' : 'status-dot dot-blue';
    }

    // Target status pill
    const targetVal = document.getElementById('targetVal');
    if (data.demo_base_url) {
      targetVal.textContent = data.demo_base_url.replace('http://', '');
    }

    // MongoDB counter
    const mongoCount = document.getElementById('mongoCount');
    if (mongoCount && data.db) {
      mongoCount.textContent = data.db.runs_count || 0;
    }
  } catch (err) {
    console.error('Failed to fetch status:', err);
  }
}

// -------------------------------------------------------------
// Version Change & Preview
// -------------------------------------------------------------
function onVersionChange(version) {
  currentVersion = version;
  const iframe = document.getElementById('previewIframe');
  const urlBar = document.getElementById('previewUrlBar');
  const targetUrl = `http://127.0.0.1:5000/v/${version}/`;
  if (iframe) iframe.src = targetUrl;
  if (urlBar) urlBar.textContent = targetUrl;
}

function triggerRunFromSelect() {
  const select = document.getElementById('targetVersion');
  triggerRun(select.value);
}

// -------------------------------------------------------------
// Test Execution Pipeline Trigger
// -------------------------------------------------------------
async function triggerRun(version) {
  if (isRunning) return;
  isRunning = true;
  currentVersion = version;

  // Sync select dropdown & iframe
  const select = document.getElementById('targetVersion');
  if (select) select.value = version;
  onVersionChange(version);

  // Set running state in UI
  setButtonState(true);
  resetStepper();
  startPhaseProgression(version);

  // Hide previous result
  const resultBanner = document.getElementById('resultBanner');
  resultBanner.style.display = 'none';

  // Clear steps list with running skeleton
  const stepsList = document.getElementById('stepsList');
  stepsList.innerHTML = `
    <div class="empty-state">
      <div class="btn-spinner" style="width: 28px; height: 28px;"></div>
      <p>Autonomous engine executing test workflow against <strong>Version ${version.toUpperCase()}</strong>...</p>
    </div>
  `;

  try {
    const response = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ version }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }

    const runResult = await response.json();
    completePhaseProgression();
    renderRunResult(runResult);
    loadRecipes();
    loadRunsHistory();
  } catch (error) {
    console.error('Run failed:', error);
    clearInterval(phaseTimer);
    renderRunError(error);
  } finally {
    isRunning = false;
    setButtonState(false);
  }
}

// -------------------------------------------------------------
// Stepper & Animation Controls
// -------------------------------------------------------------
function setButtonState(running) {
  const btn = document.getElementById('btnRunMain');
  const spinner = document.getElementById('btnSpinner');
  const text = document.getElementById('btnRunText');
  if (running) {
    btn.disabled = true;
    spinner.style.display = 'inline-block';
    text.textContent = 'Executing...';
  } else {
    btn.disabled = false;
    spinner.style.display = 'none';
    text.textContent = 'Run Test';
  }
}

function resetStepper() {
  ['stepInit', 'stepExecute', 'stepTriage', 'stepHeal', 'stepVerify'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.className = 'phase-step step-idle';
  });
  ['conn1', 'conn2', 'conn3', 'conn4'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.className = 'phase-connector';
  });
}

function startPhaseProgression(version) {
  clearInterval(phaseTimer);
  const stepInit = document.getElementById('stepInit');
  const stepExecute = document.getElementById('stepExecute');
  const stepTriage = document.getElementById('stepTriage');
  const stepHeal = document.getElementById('stepHeal');
  const conn1 = document.getElementById('conn1');
  const conn2 = document.getElementById('conn2');

  stepInit.className = 'phase-step step-active';

  let currentPhase = 1;
  phaseTimer = setInterval(() => {
    currentPhase++;
    if (currentPhase === 2) {
      stepInit.className = 'phase-step step-done';
      conn1.className = 'phase-connector conn-done';
      stepExecute.className = 'phase-step step-active';
    } else if (currentPhase === 3) {
      if (version !== 'a') {
        stepExecute.className = 'phase-step step-done';
        conn2.className = 'phase-connector conn-done';
        stepTriage.className = 'phase-step step-active';
      }
    } else if (currentPhase === 4) {
      if (version === 'b') {
        stepTriage.className = 'phase-step step-done';
        const conn3 = document.getElementById('conn3');
        if (conn3) conn3.className = 'phase-connector conn-done';
        stepHeal.className = 'phase-step step-active';
      }
    }
  }, 1200);
}

function completePhaseProgression() {
  clearInterval(phaseTimer);
  ['stepInit', 'stepExecute', 'stepTriage', 'stepHeal', 'stepVerify'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.className = 'phase-step step-done';
  });
  ['conn1', 'conn2', 'conn3', 'conn4'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.className = 'phase-connector conn-done';
  });
}

// -------------------------------------------------------------
// Result Rendering
// -------------------------------------------------------------
function renderRunResult(run) {
  const resultBanner = document.getElementById('resultBanner');
  const resStatusBadge = document.getElementById('resStatusBadge');
  const resVersionTag = document.getElementById('resVersionTag');
  const resDuration = document.getElementById('resDuration');
  const resTitle = document.getElementById('resTitle');
  const resExplanation = document.getElementById('resExplanation');

  resultBanner.style.display = 'block';
  resStatusBadge.textContent = run.status;
  resVersionTag.textContent = `TARGET: VERSION ${run.version.toUpperCase()}`;
  resDuration.textContent = `${run.duration_ms} ms`;
  resTitle.textContent = run.status_label;
  resExplanation.innerHTML = formatMarkdown(run.agent_explanation);

  // Styling by status
  if (run.status === 'PASS_NO_HEAL') {
    resultBanner.className = 'result-banner res-pass';
  } else if (run.status === 'PASS_AFTER_HEAL') {
    resultBanner.className = 'result-banner res-heal';
  } else {
    resultBanner.className = 'result-banner res-bug';
  }

  // Render executed steps list
  const stepsList = document.getElementById('stepsList');
  const stepsCounter = document.getElementById('stepsCounter');
  stepsCounter.textContent = `${run.steps ? run.steps.length : 0} steps`;

  if (!run.steps || run.steps.length === 0) {
    stepsList.innerHTML = `<div class="empty-state"><p>No steps executed.</p></div>`;
  } else {
    stepsList.innerHTML = run.steps.map(s => {
      let tagClass = 'tag-goto';
      if (s.action === 'fill_field') tagClass = 'tag-fill';
      if (s.action === 'click_button') tagClass = 'tag-click';

      const iconClass = s.success ? 'icon-pass' : 'icon-fail';
      const iconSymbol = s.success ? '✓' : '✕';

      return `
        <div class="step-row">
          <div class="step-left">
            <span class="step-idx">#${s.step_index + 1}</span>
            <span class="step-action-tag ${tagClass}">${s.action}</span>
            <span class="step-target">${escapeHtml(s.target_name)}</span>
            ${s.field_key ? `<span class="step-field">[key: ${s.field_key}]</span>` : ''}
          </div>
          <div class="step-right">
            <span class="step-time">${s.duration_ms}ms</span>
            <span class="step-status-icon ${iconClass}">${iconSymbol}</span>
          </div>
        </div>
      `;
    }).join('');
  }

  // Populate UI Diff Tab
  renderDiffTab(run.diff_summary);
}

function renderRunError(err) {
  const resultBanner = document.getElementById('resultBanner');
  const resStatusBadge = document.getElementById('resStatusBadge');
  const resTitle = document.getElementById('resTitle');
  const resExplanation = document.getElementById('resExplanation');

  resultBanner.style.display = 'block';
  resultBanner.className = 'result-banner res-bug';
  resStatusBadge.textContent = 'ERROR';
  resTitle.textContent = 'Test Execution Failed';
  resExplanation.textContent = err.message || 'Unknown error occurred.';
}

// -------------------------------------------------------------
// UI Diff Tab Rendering
// -------------------------------------------------------------
function renderDiffTab(diffSummary) {
  if (!diffSummary) return;
  const addedCount = document.getElementById('diffAddedCount');
  const removedCount = document.getElementById('diffRemovedCount');
  const renamedCount = document.getElementById('diffRenamedCount');
  const tree = document.getElementById('diffDetailsTree');

  addedCount.textContent = `+${diffSummary.added} Added`;
  removedCount.textContent = `-${diffSummary.removed} Removed`;
  renamedCount.textContent = `~${diffSummary.renamed} Renamed`;

  if (!diffSummary.details || diffSummary.details.length === 0) {
    tree.innerHTML = `<div class="empty-state-small">Zero structural DOM differences detected.</div>`;
    return;
  }

  tree.innerHTML = diffSummary.details.map(item => {
    if (item.type === 'added') {
      return `
        <div class="diff-tree-item item-added">
          <span><strong>+ Added Element:</strong> ${escapeHtml(item.name)} (role: ${item.role})</span>
          <span class="badge badge-pass">NEW</span>
        </div>
      `;
    } else if (item.type === 'removed') {
      return `
        <div class="diff-tree-item item-removed">
          <span><strong>- Removed Element:</strong> ${escapeHtml(item.name)} (role: ${item.role})</span>
          <span class="badge badge-bug">REMOVED</span>
        </div>
      `;
    } else if (item.type === 'renamed') {
      return `
        <div class="diff-tree-item item-renamed">
          <span><strong>~ Renamed Control:</strong> "${escapeHtml(item.from)}" &rarr; "${escapeHtml(item.to)}"</span>
          <span class="badge badge-heal">${Math.round(item.confidence * 100)}% match</span>
        </div>
      `;
    }
    return '';
  }).join('');
}

// -------------------------------------------------------------
// Recipe Inspector Tab
// -------------------------------------------------------------
async function loadRecipes() {
  try {
    const res = await fetch('/api/recipes');
    if (!res.ok) return;
    const recipes = await res.json();

    const badgesContainer = document.getElementById('recipeVersionBadges');
    const cardsContainer = document.getElementById('recipeCardsContainer');

    if (!recipes || recipes.length === 0) {
      cardsContainer.innerHTML = `<div class="empty-state-small">No recipe files found.</div>`;
      return;
    }

    badgesContainer.innerHTML = recipes.map((r, i) => `
      <span class="version-tag ${i === recipes.length - 1 ? 'active' : ''}">v${r.version} (${r.created_by})</span>
    `).join('');

    cardsContainer.innerHTML = recipes.map(r => `
      <div class="recipe-version-card">
        <div class="recipe-card-header">
          <div>
            <strong>Recipe v${r.version}</strong>
            <span style="color: var(--text-muted); font-size: 11px; margin-left: 8px;">
              Created by: ${r.created_by} ${r.parent_version ? `(parent: v${r.parent_version})` : ''}
            </span>
          </div>
          <span class="badge ${r.version > 1 ? 'badge-heal' : 'badge-neutral'}">${r.steps.length} Steps</span>
        </div>
        <div class="recipe-steps-compact">
          ${r.steps.map((st, sidx) => `
            <div class="recipe-step-mini">
              <span style="font-family: var(--font-mono); color: var(--text-muted); font-size: 10px;">${sidx + 1}.</span>
              <span class="step-action-tag ${st.action === 'goto_start' ? 'tag-goto' : st.action === 'fill_field' ? 'tag-fill' : 'tag-click'}">${st.action}</span>
              <span>${escapeHtml(st.target ? st.target.name : 'Start URL')}</span>
              ${st.field_key ? `<span style="color: var(--text-muted); font-family: var(--font-mono); font-size: 10px;">[${st.field_key}]</span>` : ''}
            </div>
          `).join('')}
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error('Failed to load recipes:', err);
  }
}

// -------------------------------------------------------------
// Immutable Intent Tab
// -------------------------------------------------------------
async function loadIntents() {
  try {
    const res = await fetch('/api/intents');
    if (!res.ok) return;
    const intents = await res.json();
    if (!intents || intents.length === 0) return;

    const intent = intents[0];
    const hashTag = document.getElementById('intentHashTag');
    const container = document.getElementById('intentOverviewCard');

    if (hashTag) hashTag.textContent = `SHA-256: ${intent.content_hash || intent.id}`;

    let testDataHtml = '';
    const testData = intent.test_data_masked || intent.test_data || {};
    for (const [k, v] of Object.entries(testData)) {
      testDataHtml += `
        <div class="intent-key-val">
          <span style="font-family: var(--font-mono); color: var(--brand-accent); font-size: 11.5px; font-weight: 600;">${escapeHtml(k)}</span>
          <span style="color: var(--text-primary); font-family: var(--font-mono); font-size: 11.5px;">${escapeHtml(String(v))}</span>
        </div>
      `;
    }

    container.innerHTML = `
      <div class="intent-section">
        <div class="intent-section-title">Immutable Goal</div>
        <p style="font-size: 14px; font-weight: 600; color: var(--text-primary);">"${escapeHtml(intent.goal)}"</p>
      </div>

      <div class="intent-section">
        <div class="intent-section-title">Deterministic Expected Outcome</div>
        <div class="intent-key-val">
          <span>Confirmation Phrase:</span>
          <strong style="color: var(--text-primary);">"${escapeHtml(intent.expected_outcome.confirmation_phrase)}"</strong>
        </div>
        <div class="intent-key-val">
          <span>Order ID Pattern:</span>
          <code class="code-inline">${escapeHtml(intent.expected_outcome.order_id_pattern)}</code>
        </div>
        <div class="intent-key-val">
          <span>Expected Total:</span>
          <strong style="color: var(--status-pass); font-family: var(--font-mono);">$${Number(intent.expected_outcome.expected_total).toFixed(2)}</strong>
        </div>
      </div>

      <div class="intent-section">
        <div class="intent-section-title">Semantic Test Data Keys</div>
        ${testDataHtml}
      </div>
    `;
  } catch (err) {
    console.error('Failed to load intents:', err);
  }
}

// -------------------------------------------------------------
// MongoDB History Tab
// -------------------------------------------------------------
async function loadRunsHistory() {
  try {
    const res = await fetch('/api/runs?limit=30');
    if (!res.ok) return;
    const runs = await res.json();

    const tbody = document.getElementById('historyTableBody');
    const mongoCount = document.getElementById('mongoCount');
    if (mongoCount) mongoCount.textContent = runs.length;

    if (!runs || runs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="table-empty">No runs recorded in MongoDB yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = runs.map(r => {
      let badgeClass = 'badge-pass';
      if (r.status === 'PASS_AFTER_HEAL') badgeClass = 'badge-heal';
      if (r.status.startsWith('FAIL')) badgeClass = 'badge-bug';

      const timeStr = r.created_at ? new Date(r.created_at).toLocaleTimeString() : 'N/A';

      return `
        <tr>
          <td style="font-family: var(--font-mono); font-size: 11px; color: var(--text-muted);">${timeStr}</td>
          <td><strong>Version ${r.version ? r.version.toUpperCase() : 'A'}</strong></td>
          <td><span class="badge ${badgeClass}">${r.status}</span></td>
          <td>${r.healed ? 'Yes' : 'No'}</td>
          <td><span class="code-inline">v${r.new_recipe_version || r.old_recipe_version || 1}</span></td>
          <td style="font-family: var(--font-mono);">${r.duration_ms}ms</td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="showRunDetails('${r.run_id}')">Inspect JSON</button>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error('Failed to load runs history:', err);
  }
}

async function showRunDetails(runId) {
  try {
    const res = await fetch(`/api/runs/${runId}`);
    if (!res.ok) return;
    const run = await res.json();

    document.getElementById('modalTitle').textContent = `Run Details: ${runId}`;
    document.getElementById('modalJson').textContent = JSON.stringify(run, null, 2);
    document.getElementById('modalBackdrop').className = 'modal-backdrop open';
  } catch (err) {
    console.error('Failed to get run details:', err);
  }
}

function closeModal(event) {
  if (event && event.target !== document.getElementById('modalBackdrop') && !event.target.classList.contains('modal-close')) {
    return;
  }
  document.getElementById('modalBackdrop').className = 'modal-backdrop';
}

// -------------------------------------------------------------
// Environment Reset
// -------------------------------------------------------------
async function resetEnvironment() {
  if (!confirm('Reset recipes to baseline v1 and clear MongoDB test runs?')) return;
  try {
    const res = await fetch('/api/reset', { method: 'POST' });
    const data = await res.json();
    alert(`Reset complete! Removed ${data.deleted_recipes.length} generated recipes.`);
    loadRecipes();
    loadRunsHistory();
    fetchSystemStatus();
    resetStepper();
    document.getElementById('resultBanner').style.display = 'none';
    document.getElementById('stepsList').innerHTML = `
      <div class="empty-state">
        <p>Environment reset to baseline Recipe v1. Ready for test run.</p>
      </div>
    `;
  } catch (err) {
    alert(`Reset failed: ${err.message}`);
  }
}

// -------------------------------------------------------------
// Tab Switching
// -------------------------------------------------------------
function switchTab(tabId) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

  event.currentTarget.classList.add('active');
  const target = document.getElementById(tabId);
  if (target) target.classList.add('active');
}

// -------------------------------------------------------------
// Utilities
// -------------------------------------------------------------
function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
}

function formatMarkdown(text) {
  if (!text) return '';
  let out = escapeHtml(text);
  // Headings
  out = out.replace(/^### (.*$)/gim, '<h4 style="color:#fff; margin: 8px 0 4px; font-size:14px;">$1</h4>');
  // Bold
  out = out.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');
  // Code
  out = out.replace(/`([^`]+)`/gim, '<code class="code-inline">$1</code>');
  // Newlines
  out = out.replace(/\n/gim, '<br>');
  return out;
}
