const state = {
  sessionType: "标准会话",
  primaryMode: "普通聊天",
  capability: null,
  conversationId: null,
  conversations: [],
  mock: false,
  memoryData: null,
};

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

const dropdown = $("#modeDropdown");
const trigger = $("#modeTrigger");
const triggerSub = $("#modeTriggerSub");
const currentModeTitle = $("#currentModeTitle");
const sessionTypeTip = $("#sessionTypeTip");
const capabilityTip = $("#capabilityTip");
const capabilityTipText = $("#capabilityTipText");
const capabilityTipActions = $("#capabilityTipActions");
const topModeChipRow = $("#topModeChipRow");
const inputCapabilityRow = $("#inputCapabilityRow");
const chatInput = $("#chatInput");
const sendBtn = $("#sendBtn");
const messageList = $("#messageList");
const welcomeBlock = $("#welcomeBlock");
const leftConversations = $(".conversations");
const saveSettingsBtn = $("#saveSettingsBtn");
const apiKeyInput = $("#apiKeyInput");
const baseUrlInput = $("#baseUrlInput");
const modelInput = $("#modelInput");
const mockToggleBtn = $("#mockToggleBtn");
const mockToggleDesc = $("#mockToggleDesc");
const hiddenFileInput = $("#hiddenFileInput");
const settingsOverlay = $("#settingsOverlay");
const settingsMainView = $("#settingsMainView");
const settingsDetailView = $("#settingsDetailView");

// --- Helpers ---
function getStoredSettings() {
  return {
    api_key: localStorage.getItem("lifepath_api_key") || "",
    base_url: localStorage.getItem("lifepath_base_url") || "https://api.deepseek.com/v1",
    model: localStorage.getItem("lifepath_model") || "deepseek-chat",
    mock_mode: localStorage.getItem("lifepath_mock_mode") === 'true',
  };
}

async function api(path, options = {}) {
  const res = await fetch(path, options);
  if (!res.ok) throw new Error(await res.text() || `HTTP ${res.status}`);
  return await res.json();
}

let _toastTimer = null;
function toast(text, persistent = false) {
  if (!capabilityTip || !capabilityTipText) return;
  clearTimeout(_toastTimer);
  capabilityTip.classList.add("show");
  capabilityTipText.innerHTML = text;
  if (capabilityTipActions) capabilityTipActions.innerHTML = "";
  const dur = persistent ? 5000 : 2600;
  _toastTimer = setTimeout(() => capabilityTip.classList.remove("show"), dur);
  // Click anywhere to dismiss
  capabilityTip.onclick = () => { capabilityTip.classList.remove("show"); capabilityTip.onclick = null; };
}

function mapMode(m) { return m === "普通聊天" ? "normal" : m === "深度理解" ? "deep_understanding" : "decision_support"; }
function mapSub(c) { return c === "自我对立视角" ? "self_opposition" : c === "多角色聊天" ? "multi_role" : null; }

// --- Settings ---
function openSettings() { settingsOverlay.classList.add('show'); loadFileList(); loadMemoryData(); }
function closeSettingsAll() { settingsOverlay.classList.remove('show'); backToSettingsMain(); }

async function saveSettings() {
  const p = { api_key: apiKeyInput.value.trim(), base_url: baseUrlInput.value.trim(), model: modelInput.value.trim(), mock_mode: state.mock };
  localStorage.setItem("lifepath_api_key", p.api_key);
  localStorage.setItem("lifepath_base_url", p.base_url);
  localStorage.setItem("lifepath_model", p.model);
  localStorage.setItem("lifepath_mock_mode", String(p.mock_mode));
  try { await api('/api/settings', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(p) }); toast("配置已保存"); } catch (e) { toast("保存失败: " + e.message, true); }
}

async function loadSettings() {
  let remote = {};
  try { remote = await api('/api/settings'); } catch(e){}
  const apiKey = localStorage.getItem("lifepath_api_key") || remote.api_key || '';
  const baseUrl = localStorage.getItem("lifepath_base_url") || remote.base_url || 'https://api.deepseek.com/v1';
  const model = localStorage.getItem("lifepath_model") || remote.model || 'deepseek-chat';
  if(apiKey) localStorage.setItem("lifepath_api_key", apiKey);
  localStorage.setItem("lifepath_base_url", baseUrl);
  localStorage.setItem("lifepath_model", model);
  if(apiKeyInput) apiKeyInput.value = apiKey;
  if(baseUrlInput) baseUrlInput.value = baseUrl;
  if(modelInput) modelInput.value = model;
}

// --- File Upload ---
async function loadFileList() {
  const area = $("#fileList"); const empty = $("#fileListEmpty");
  if (!area) return;
  try {
    const data = await api('/api/files');
    area.innerHTML = '';
    if (data.files.length === 0) { empty.style.display = 'block'; return; }
    empty.style.display = 'none';
    data.files.forEach(f => {
      const div = document.createElement('div'); div.className = 'file-item';
      const sizeKB = (f.size / 1024).toFixed(1);
      div.innerHTML = `<div class="file-item-name">📄 ${f.name}</div><span class="file-item-meta">${sizeKB}KB · ${f.uploaded_at}</span><button class="btn btn-danger" style="font-size:12px;padding:4px 10px;margin-left:8px;" data-del-file="${f.name}">删除</button>`;
      area.appendChild(div);
    });
    area.querySelectorAll('[data-del-file]').forEach(btn => btn.onclick = async function () { await api(`/api/files/${this.dataset.delFile}`, { method: 'DELETE' }); loadFileList(); });
  } catch (e) { area.innerHTML = '<div style="color:var(--muted);font-size:13px;">加载失败</div>'; }
}

async function uploadFiles() {
  hiddenFileInput.click();
}

hiddenFileInput.onchange = async function () {
  if (!this.files.length) return;
  const loading = $("#uploadLoading");
  const loadingSpan = loading.querySelector('span');
  loading.style.display = 'flex';
  loadingSpan.textContent = "正在上传文件...";
  
  const fd = new FormData();
  for (const f of this.files) fd.append('files', f);
  const s = getStoredSettings();
  fd.append('api_key', s.api_key); fd.append('base_url', s.base_url); fd.append('model', s.model); fd.append('mock', 'false');
  
  try {
    const res = await fetch('/api/upload-profile-files', { method: 'POST', body: fd });
    if (!res.ok) throw new Error(await res.text() || `HTTP ${res.status}`);
    
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let lines = buffer.split('\n');
      buffer = lines.pop(); // keep the incomplete line in buffer
      
      for (let line of lines) {
        if (!line.trim()) continue;
        try {
          const data = JSON.parse(line);
          if (data.type === 'progress') {
            loadingSpan.textContent = data.label;
          } else if (data.type === 'done') {
            toast(data.message || "资料分析完成，画像已更新！");
            loadFileList(); loadMemoryData();
          } else if (data.type === 'error') {
            throw new Error(data.message);
          }
        } catch(e) {
          if (e.message && e.message.includes('Unexpected')) {
            // JSON parse error, ignore partial
          } else {
            throw e;
          }
        }
      }
    }
  } catch (e) { 
    toast("上传失败: " + e.message, true); 
  } finally { 
    loading.style.display = 'none'; 
    loadingSpan.textContent = "正在分析资料，生成画像中..."; // Reset for next time
    this.value = ''; 
  }
};

// --- Memory ---
async function loadMemoryData() {
  try {
    const data = await api('/api/memory');
    state.memoryData = data;
    const profile = data.profile || {};
    const mem = data.memory || {};
    $("#memCardStatic").textContent = profile.executive_summary || "暂无画像数据";
    const dynCount = (mem.dynamic_memory || []).length;
    $("#memCardDynamic").textContent = dynCount > 0 ? `共 ${dynCount} 条记录` : "暂无动态记忆";
    const snap = mem.current_snapshot || {};
    const snapParts = [snap.emotion_state, snap.life_phase, snap.decision_state].filter(Boolean);
    $("#memCardSnapshot").textContent = snapParts.length ? snapParts.join(' · ') : "暂无快照";
  } catch (e) { }
}

function openMemoryDetail(type) {
  settingsMainView.style.display = 'none';
  settingsDetailView.style.display = 'block';
  const title = $("#detailTitle"), desc = $("#detailDesc"), content = $("#detailContent");
  content.innerHTML = '';
  const data = state.memoryData || {};
  const profile = data.profile || {};
  const mem = data.memory || {};

  if (type === 'static_profile') {
    title.textContent = '全局静态画像';
    desc.textContent = '通过资料分析生成的长期画像底座';
    if (!profile || !profile.executive_summary) { content.innerHTML = '<div style="color:var(--muted)">暂无画像数据，请先上传资料。</div>'; return; }
    const fields = [
      { label: '总结', value: profile.executive_summary },
      { label: '性格标签', value: JSON.stringify(profile.human_info_card?.labels || profile.labels || [], null, 0) },
      { label: '表达风格', value: JSON.stringify(profile.expression_style || {}, null, 2) },
      { label: '行为模式', value: JSON.stringify(profile.behavior_patterns || {}, null, 2) },
      { label: '隐含信念', value: JSON.stringify(profile.implicit_beliefs || {}, null, 2) },
      { label: '四层系统', value: JSON.stringify(profile.four_layer_system || {}, null, 2) },
    ];
    fields.forEach(f => {
      if (!f.value || f.value === '{}' || f.value === '[]') return;
      const d = document.createElement('div'); d.className = 'detail-item';
      d.innerHTML = `<div class="detail-item-content"><div>${f.value}</div><div class="detail-label">${f.label}</div></div>`;
      content.appendChild(d);
    });
  }
  else if (type === 'dynamic_memory') {
    title.textContent = '全局动态记忆';
    desc.textContent = '系统在对话中自动记住的长期主题与变化';
    const items = mem.dynamic_memory || [];
    if (!items.length) { content.innerHTML = '<div style="color:var(--muted)">暂无动态记忆。</div>'; return; }
    items.forEach(item => {
      const d = document.createElement('div'); d.className = 'detail-item';
      d.innerHTML = `<div class="detail-item-content"><div>${item.summary}</div><div class="detail-label">${item.type || ''} · confidence: ${item.confidence || '-'}</div></div><div class="detail-item-actions"><button class="btn btn-danger" style="font-size:12px;padding:4px 10px;" data-del-mem="${item.id}">删除</button></div>`;
      content.appendChild(d);
    });
    content.querySelectorAll('[data-del-mem]').forEach(btn => btn.onclick = async function () {
      await api(`/api/memory/dynamic/${this.dataset.delMem}`, { method: 'DELETE' });
      await loadMemoryData();
      openMemoryDetail('dynamic_memory');
    });
  }
  else if (type === 'short_term') {
    title.textContent = '当前会话短期记忆';
    desc.textContent = '当前会话内部的上下文摘要';
    if (!state.conversationId) { content.innerHTML = '<div style="color:var(--muted)">请先打开一个会话。</div>'; return; }
    const conv = state.conversations.find(c => c.id === state.conversationId);
    const stm = conv?.short_term_memory || conv?.analysis_state || {};
    const entries = Object.entries(stm).filter(([k, v]) => v !== null && v !== '' && v !== false);
    if (!entries.length) { content.innerHTML = '<div style="color:var(--muted)">当前会话暂无短期记忆。</div>'; return; }
    entries.forEach(([k, v]) => {
      const d = document.createElement('div'); d.className = 'detail-item';
      d.innerHTML = `<div class="detail-item-content"><div>${typeof v === 'object' ? JSON.stringify(v, null, 2) : v}</div><div class="detail-label">${k}</div></div>`;
      content.appendChild(d);
    });
  }
  else if (type === 'snapshot') {
    title.textContent = '当前状态快照';
    desc.textContent = '系统对你近期状态的判断';
    const snap = mem.current_snapshot || {};
    const fields = [
      { label: '情绪状态', value: snap.emotion_state },
      { label: '决策状态', value: snap.decision_state },
      { label: '生命阶段', value: snap.life_phase },
      { label: '置信度', value: snap.confidence },
      { label: '更新时间', value: snap.updated_at },
    ];
    const valid = fields.filter(f => f.value);
    if (!valid.length) { content.innerHTML = '<div style="color:var(--muted)">暂无状态快照。</div>'; return; }
    valid.forEach(f => {
      const d = document.createElement('div'); d.className = 'detail-item';
      d.innerHTML = `<div class="detail-item-content"><div>${f.value}</div><div class="detail-label">${f.label}</div></div>`;
      content.appendChild(d);
    });
  }
}

function backToSettingsMain() {
  settingsMainView.style.display = 'block';
  settingsDetailView.style.display = 'none';
}

// --- Mode & State ---
function renderState() {
  const summary = [state.sessionType, state.primaryMode];
  if (state.capability) summary.push(state.capability);
  if (triggerSub) triggerSub.textContent = summary.join(" · ");
  if (currentModeTitle) currentModeTitle.textContent = state.primaryMode;
  if (sessionTypeTip) sessionTypeTip.textContent = state.sessionType;
  $$("[data-session-type]").forEach(b => b.classList.toggle("btn-primary", b.dataset.sessionType === state.sessionType));
  $$(".mode-primary-item").forEach(i => i.classList.toggle("active", i.dataset.primary === state.primaryMode));
  $$(".mode-subitem").forEach(i => i.classList.toggle("btn-primary", i.dataset.capability === state.capability));
  if (inputCapabilityRow) {
    inputCapabilityRow.innerHTML = "";
    if (state.capability) {
      const chip = document.createElement("div");
      chip.style.cssText = "padding:4px 12px;font-size:12px;background:#eee;border-radius:999px;display:inline-flex;align-items:center;gap:8px;";
      chip.innerHTML = `<span>${state.capability}</span>`;
      const x = document.createElement("button"); x.textContent = "×"; x.style.cssText = "border:none;background:transparent;cursor:pointer;"; x.onclick = () => { state.capability = null; syncModeToBackend(); renderState(); };
      chip.appendChild(x); inputCapabilityRow.appendChild(chip); inputCapabilityRow.style.display = "block";
    } else { inputCapabilityRow.style.display = "none"; }
  }
}

// --- Helper: Format bubble content (handles objects and basic markdown) ---
function formatBubbleContent(content) {
  if (!content) return "";
  
  let data = content;
  // 0. If it's a string but looks like JSON, try to parse it first
  if (typeof content === 'string' && content.trim().startsWith('{')) {
    const trimmed = content.trim();
    try {
      data = JSON.parse(trimmed);
    } catch (e) {
      // Try healing truncated JSON
      for (const fix of ['}', '"}', '"]}', '"}]}']) {
        try { data = JSON.parse(trimmed + fix); break; } catch (err) {}
      }
    }
  }

  // 1. If it's an object (agent view), format it beautifully
  if (typeof data === 'object' && data !== null) {
    // Fallback for failed backend parsing
    if (data.raw_output) {
      let raw = String(data.raw_output);
      raw = raw.replace(/\\n/g, '\n').replace(/\\"/g, '"');
      return formatBubbleContent(raw);
    }

    let html = '<div class="agent-view-card">';
    if (data.core_concern) html += `<div class="agent-item"><strong>🎯 核心关注：</strong> ${data.core_concern}</div>`;
    if (data.preferred_option) html += `<div class="agent-item"><strong>✅ 建议选择：</strong> ${data.preferred_option}</div>`;
    if (data.path_logic) {
      const logic = Array.isArray(data.path_logic) ? data.path_logic : [data.path_logic];
      html += `<div class="agent-item"><strong>💡 分析逻辑：</strong><ul style="margin-top:4px; padding-left:20px;">${logic.map(l => `<li>${l}</li>`).join('')}</ul></div>`;
    }
    if (data.risk_note) html += `<div class="agent-item" style="color:#c0392b;"><strong>⚠️ 风险提醒：</strong> ${data.risk_note}</div>`;
    html += '</div>';
    
    // If we didn't find our specific keys, but it's still an object, show it as formatted JSON or text
    if (html === '<div class="agent-view-card"></div>') {
       return `<pre style="white-space:pre-wrap;font-family:inherit;font-size:14px;">${JSON.stringify(data, null, 2)}</pre>`;
    }
    return html;
  }

  // 2. Simple Markdown: **bold** -> <strong>bold</strong>
  let text = String(data);
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // Handle line breaks
  text = text.replace(/\n/g, '<br>');
  return text;
}

// --- Messages ---
function renderMessages(messages) {
  if (!messageList) return;
  messageList.innerHTML = "";
  if (messages.length > 0) { if (welcomeBlock) welcomeBlock.style.display = "none"; }
  else { if (welcomeBlock) welcomeBlock.style.display = "flex"; }
  messages.forEach(msg => {
    if (msg.role === "card") {
      const card = typeof msg.content === "string" ? { title: "阶段卡片", items: [msg.content] } : msg.content;
      const w = document.createElement("div"); w.className = "bubble"; w.style.cssText = "max-width:800px;margin:0 auto;";
      w.innerHTML = `<div style="font-weight:bold;margin-bottom:12px;">${card.title}</div>`;
      (card.items || []).forEach(it => { const d = document.createElement('div'); d.style.cssText = 'font-size:14px;margin-bottom:8px;'; d.textContent = `• ${typeof it === 'string' ? it : JSON.stringify(it)}`; w.appendChild(d); });
      messageList.appendChild(w); return;
    }
    const row = document.createElement("div"); row.className = `message ${msg.role === "user" ? "user" : "ai"}`;
    const avatarText = msg.avatar || (msg.role === "assistant" ? "AI" : "你");
    row.innerHTML = `<div class="avatar">${avatarText}</div><div class="bubble">${formatBubbleContent(msg.content)}</div>`;
    messageList.appendChild(row);
  });
  messageList.scrollTop = messageList.scrollHeight;
}

// --- Conversations ---
async function createConversation() {
  const conv = await api('/api/conversations/new', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ title: '新的会话', conversation_type: state.sessionType === '不留痕聊天' ? 'private' : 'standard' }) });
  state.conversationId = conv.id; await refreshConversations(); await loadConversation(conv.id);
}

async function refreshConversations() {
  if (!leftConversations) return;
  const data = await api('/api/conversations'); state.conversations = data.items || []; renderConversationList();
}

function renderConversationList() {
  if (!leftConversations) return; leftConversations.innerHTML = '';
  state.conversations.forEach(item => {
    const btn = document.createElement('button'); btn.className = 'btn'; btn.style.cssText = `width:100%;justify-content:flex-start;margin-bottom:8px;padding:12px;border:${item.id === state.conversationId ? '1px solid #111' : '1px solid transparent'};background:${item.id === state.conversationId ? '#fff' : 'transparent'};`;
    btn.innerHTML = `<div style="font-weight:600;font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${item.title}</div>`;
    btn.onclick = () => loadConversation(item.id); leftConversations.appendChild(btn);
  });
}

async function loadConversation(id) {
  const conv = await api(`/api/conversations/${id}`);
  state.conversationId = conv.id;
  state.sessionType = conv.type === 'private' ? '不留痕聊天' : '标准会话';
  state.primaryMode = conv.main_mode === 'deep_understanding' ? '深度理解' : conv.main_mode === 'decision_support' ? '决策辅助' : '普通聊天';
  state.capability = conv.sub_mode === 'self_opposition' ? '自我对立视角' : conv.sub_mode === 'multi_role' ? '多角色聊天' : null;
  renderState(); renderMessages(conv.messages || []); await refreshConversations();
}

async function syncModeToBackend() {
  if (!state.conversationId) return;
  await api('/api/conversations/toggle-mode', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ conversation_id: state.conversationId, main_mode: mapMode(state.primaryMode), sub_mode: mapSub(state.capability) }) });
}

// --- Send Message (Streaming) ---
async function sendMessage() {
  if (!chatInput) return;
  const text = chatInput.value.trim(); if (!text) return;
  if (!state.conversationId) await createConversation();
  const settings = getStoredSettings();
  chatInput.value = '';
  if (welcomeBlock) welcomeBlock.style.display = 'none';

  // Add user bubble
  const userRow = document.createElement("div"); userRow.className = "message user";
  userRow.innerHTML = `<div class="avatar">你</div><div class="bubble">${text}</div>`;
  messageList.appendChild(userRow);

  // Add AI bubble placeholder with loading indicator
  const aiRow = document.createElement("div"); aiRow.className = "message ai";
  const loadingText = state.primaryMode === '决策辅助' ? '正在进行深度决策分析，请稍候...' : '正在思考...';
  aiRow.innerHTML = `<div class="avatar">AI</div><div class="bubble"><div style="display:flex;align-items:center;gap:10px;color:var(--muted);"><div class="spinner" style="width:14px;height:14px;border-width:2px;"></div><span>${loadingText}</span></div></div>`;
  const aiBubble = aiRow.querySelector('.bubble');
  messageList.appendChild(aiRow);
  messageList.scrollTop = messageList.scrollHeight;
  if (sendBtn) sendBtn.disabled = true;

  try {
    const response = await fetch('/api/chat/send', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ conversation_id: state.conversationId, message: text, api_key: settings.api_key, base_url: settings.base_url, model: settings.model, mock: false, main_mode: mapMode(state.primaryMode), sub_mode: mapSub(state.capability) }) });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const reader = response.body.getReader(); const decoder = new TextDecoder(); let fullReply = "";
    let buffer = "";
    while (true) {
      const { done, value } = await reader.read(); if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let lines = buffer.split('\n');
      buffer = lines.pop(); // keep the incomplete line in buffer
      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const data = JSON.parse(line);
          if (data.type === 'text') { fullReply += data.content; aiBubble.innerHTML = formatBubbleContent(fullReply); messageList.scrollTop = messageList.scrollHeight; }
          else if (data.type === 'error') {
            toast(data.message, true);
            aiBubble.innerHTML = formatBubbleContent(fullReply || "请求发生错误，请重试。");
          }
          else if (data.type === 'agent_bubble') {
            // Insert a new complete bubble before the main AI bubble
            const agentRow = document.createElement("div"); agentRow.className = "message ai";
            agentRow.innerHTML = `<div class="avatar">${data.agent_name}</div><div class="bubble">${formatBubbleContent(data.content)}</div>`;
            messageList.insertBefore(agentRow, aiRow);
            messageList.scrollTop = messageList.scrollHeight;
          }
          else if (data.type === 'final') {
            renderMessages(data.conversation.messages || []);
            // Suggest deeper
            if (data.suggest_deeper && state.primaryMode === '普通聊天') {
              const bar = document.createElement('div'); bar.className = 'suggest-deeper-bar';
              bar.innerHTML = `<div class="suggest-text">💡 这个话题可能适合更深入的分析</div><button class="btn" data-switch-mode="深度理解">切换到深度理解</button><button class="btn" data-switch-mode="决策辅助">切换到决策辅助</button>`;
              messageList.appendChild(bar);
              bar.querySelectorAll('[data-switch-mode]').forEach(b => b.onclick = async function () {
                state.primaryMode = this.dataset.switchMode; state.capability = null; renderState(); await syncModeToBackend(); bar.remove(); toast(`已切换到${state.primaryMode}模式`);
              });
            }
            await refreshConversations();
            messageList.scrollTop = messageList.scrollHeight;
          }
        } catch (e) { 
          // Ignoring JSON parse error for incomplete line edge cases
        }
      }
    }
  } catch (err) { toast('发送失败：' + err.message, true); }
  finally { if (sendBtn) sendBtn.disabled = false; }
}

// --- Event Listeners ---
if (trigger) trigger.onclick = () => dropdown && dropdown.classList.toggle('show');
if (sendBtn) sendBtn.onclick = sendMessage;
if (chatInput) chatInput.onkeydown = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } };
document.addEventListener('click', e => { if (dropdown && trigger && !trigger.contains(e.target) && !dropdown.contains(e.target)) dropdown.classList.remove('show'); });
$$("[data-session-type]").forEach(b => b.addEventListener('click', function () { state.sessionType = this.dataset.sessionType; renderState(); if (dropdown) dropdown.classList.remove('show'); }));
$$('[data-primary-select]').forEach(b => b.addEventListener('click', async function () { state.primaryMode = this.dataset.primarySelect; state.capability = null; renderState(); if (dropdown) dropdown.classList.remove('show'); await syncModeToBackend(); }));
$$('.mode-subitem').forEach(b => b.addEventListener('click', async function () { state.primaryMode = this.dataset.parent; state.capability = this.dataset.capability; renderState(); if (dropdown) dropdown.classList.remove('show'); await syncModeToBackend(); }));
if (saveSettingsBtn) saveSettingsBtn.onclick = saveSettings;
if (mockToggleBtn) mockToggleBtn.onclick = () => { state.mock = !state.mock; if (mockToggleDesc) mockToggleDesc.textContent = `当前：${state.mock ? "开启" : "关闭"}`; toast(`Mock 模式已${state.mock ? '开启' : '关闭'}`); };
if ($("#newThreadBtn")) $("#newThreadBtn").onclick = createConversation;
if ($("#settingsTrigger")) $("#settingsTrigger").onclick = openSettings;
if ($("#closeSettings")) $("#closeSettings").onclick = closeSettingsAll;
if ($("#closeSettingsDetail")) $("#closeSettingsDetail").onclick = closeSettingsAll;
if ($("#backToMainBtn")) $("#backToMainBtn").onclick = backToSettingsMain;
if ($("#uploadTriggerBtn")) $("#uploadTriggerBtn").onclick = uploadFiles;
$$('.memory-card').forEach(card => card.onclick = function () { openMemoryDetail(this.dataset.memoryType); });

// Update short-term memory card when conversation changes
const origLoadConv = loadConversation;

// --- Init ---
(async function init() {
  try { const d = await api('/api/config/defaults'); if (!localStorage.getItem('lifepath_base_url')) localStorage.setItem('lifepath_base_url', d.base_url); if (!localStorage.getItem('lifepath_model')) localStorage.setItem('lifepath_model', d.model); } catch (e) { }
  await loadSettings(); renderState(); await refreshConversations();
  if (state.conversations.length) await loadConversation(state.conversations[0].id);
})();