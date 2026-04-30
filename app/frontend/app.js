const state = {
  sessionType: "标准会话",
  primaryMode: "普通聊天",
  capability: null,
  modeDescriptions: {
    "普通聊天": "正常聊天，逐步了解你当前的状态与问题。",
    "深度理解": "用于复杂问题，帮助你更深入拆解情绪、模式和内在冲突。",
    "决策辅助": "帮助你分析选项、比较路径，并梳理决策代价与收益。"
  },
  capabilityDescriptions: {
    "自我对立视角": "已启用“自我对立视角”，当前会话将持续从你内在相反立场切入。",
    "多角色聊天": "已启用“多角色聊天”，当前会话将持续以多立场并行方式辅助决策，其中内含未来视角。"
  },
  conversationId: null,
  conversations: [],
  mock: false,
};

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));
const dropdown = $("#modeDropdown");
const trigger = $("#modeTrigger");
const triggerSub = $("#modeTriggerSub");
const currentModeTitle = $("#currentModeTitle");
const currentModeMiniDesc = $("#currentModeMiniDesc");
const currentModeSecondaryLine = $("#currentModeSecondaryLine");
const currentSessionLine = $("#currentSessionLine");
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
const welcomeModeCards = $("#welcomeModeCards");
const leftConversations = $(".conversations");
const saveSettingsBtn = $("#saveSettingsBtn");
const apiKeyInput = $("#apiKeyInput");
const baseUrlInput = $("#baseUrlInput");
const modelInput = $("#modelInput");
const mockToggleBtn = $("#mockToggleBtn");
const mockToggleDesc = $("#mockToggleDesc");
const addUnderstandingBtn = $("#addUnderstandingBtn");
const pasteUnderstandingBtn = $("#pasteUnderstandingBtn");
const hiddenFileInput = $("#hiddenFileInput");
const memoryBlocks = $$(".memory-block");
const appShell = $("#appShell");
const memoryOverlay = $("#memoryOverlay");
const memoryCloseBtn = $("#memoryCloseBtn");
const memoryModalKicker = $("#memoryModalKicker");
const memoryModalTitle = $("#memoryModalTitle");
const memoryModalDesc = $("#memoryModalDesc");
const memoryPoints = $("#memoryPoints");
const memoryTimeline = $("#memoryTimeline");
const memoryTags = $("#memoryTags");

function getStoredSettings() {
  return {
    api_key: localStorage.getItem("lifepath_api_key") || "",
    base_url: localStorage.getItem("lifepath_base_url") || "https://api.deepseek.com/v1",
    model: localStorage.getItem("lifepath_model") || "deepseek-chat",
    mock_mode: localStorage.getItem("lifepath_mock_mode") === 'true',
  };
}
async function saveSettings() {
  const payload = {
    api_key: apiKeyInput.value.trim(),
    base_url: baseUrlInput.value.trim(),
    model: modelInput.value.trim(),
    mock_mode: state.mock,
  };
  localStorage.setItem("lifepath_api_key", payload.api_key);
  localStorage.setItem("lifepath_base_url", payload.base_url);
  localStorage.setItem("lifepath_model", payload.model);
  localStorage.setItem("lifepath_mock_mode", String(payload.mock_mode));
  try {
    await api('/api/settings', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
    toast("模型配置已保存。", false);
  } catch (err) {
    toast('配置保存失败：' + err.message, true);
  }
}
async function loadSettings() {
  let s = getStoredSettings();
  try {
    const remote = await api('/api/settings');
    s = {
      api_key: s.api_key || remote.api_key || '',
      base_url: s.base_url || remote.base_url || 'https://api.deepseek.com/v1',
      model: s.model || remote.model || 'deepseek-chat',
      mock_mode: localStorage.getItem("lifepath_mock_mode") !== null ? (localStorage.getItem("lifepath_mock_mode") === 'true') : !!remote.mock_mode,
    };
  } catch (err) {}
  apiKeyInput.value = s.api_key;
  baseUrlInput.value = s.base_url;
  modelInput.value = s.model;
  state.mock = !!s.mock_mode;
  mockToggleDesc.textContent = `当前：${state.mock ? "开启" : "关闭"}`;
}
function toast(text, persistent=false) {
  capabilityTip.classList.add("show");
  capabilityTipText.innerHTML = text;
  capabilityTipActions.innerHTML = "";
  if (!persistent) {
    setTimeout(() => {
      if (!state.capability) capabilityTip.classList.remove("show");
    }, 2600);
  }
}
function makeCapabilityChip(label) {
  const chip = document.createElement("div");
  chip.className = "capability-chip";
  chip.innerHTML = `<span>${label}</span>`;
  const closeBtn = document.createElement("button");
  closeBtn.type = "button";
  closeBtn.textContent = "×";
  closeBtn.onclick = (e) => { e.stopPropagation(); closeCapability(); };
  chip.appendChild(closeBtn);
  return chip;
}
function closeCapability() {
  state.capability = null;
  syncModeToBackend();
  renderState();
  toast(`已关闭二级能力，当前保留在 <strong>${state.primaryMode}</strong> 模式。`, false);
}
function mapModeForBackend(modeZh) {
  if (modeZh === "普通聊天") return "normal";
  if (modeZh === "深度理解") return "deep_understanding";
  return "decision_support";
}
function mapSubModeForBackend(capZh) {
  if (capZh === "自我对立视角") return "self_opposition";
  if (capZh === "多角色聊天") return "multi_role";
  return null;
}
function renderState() {
  const summary = [state.sessionType, state.primaryMode];
  if (state.capability) summary.push(state.capability);
  triggerSub.textContent = summary.join(" · ");
  currentModeTitle.textContent = state.primaryMode;
  currentModeMiniDesc.textContent = state.modeDescriptions[state.primaryMode];
  currentModeSecondaryLine.textContent = state.capability ? `已开启二级能力：${state.capability}` : "当前未开启二级能力";
  currentSessionLine.textContent = `当前会话类型：${state.sessionType}`;
  sessionTypeTip.textContent = state.sessionType === "不留痕聊天" ? "当前会话类型：不留痕聊天 · 读取已有理解，但不写回长期记忆" : "当前会话类型：标准会话";
  $$("[data-session-type]").forEach(btn => btn.classList.toggle("active", btn.dataset.sessionType === state.sessionType));
  $$(".mode-primary-item").forEach(item => {
    const mode = item.dataset.primary;
    item.classList.toggle("active", mode === state.primaryMode);
    item.classList.toggle("no-capability", mode === state.primaryMode && !state.capability);
  });
  $$(".mode-subitem").forEach(item => item.classList.toggle("active", item.dataset.capability === state.capability));
  topModeChipRow.innerHTML = "";
  inputCapabilityRow.innerHTML = "";
  if (state.capability) {
    const chip1 = makeCapabilityChip(`已启用能力：${state.capability}`);
    const chip2 = makeCapabilityChip(`已启用能力：${state.capability}`);
    topModeChipRow.appendChild(chip1);
    inputCapabilityRow.appendChild(chip2);
    inputCapabilityRow.classList.add("show");
    capabilityTip.classList.add("show");
    capabilityTipText.innerHTML = `<strong>${state.primaryMode}</strong> 模式下已开启 <strong>${state.capability}</strong>。该二级能力会在当前会话持续生效，直到你手动关闭或切换模式。`;
    capabilityTipActions.innerHTML = "";
    capabilityTipActions.appendChild(makeCapabilityChip(state.capability));
  } else {
    inputCapabilityRow.classList.remove("show");
    capabilityTip.classList.remove("show");
  }
}

function insertEnhancementActions() {
  const topbarActions = document.querySelector('.header-actions');
  if (topbarActions && !document.getElementById('showcaseBtn')) {
    const a = document.createElement('a');
    a.id = 'showcaseBtn';
    a.href = '/static/showcase.html';
    a.target = '_blank';
    a.className = 'ghost-btn';
    a.textContent = '比赛展示页';
    topbarActions.prepend(a);
  }
  const welcomeActions = document.querySelector('.welcome-actions');
  if (welcomeActions && !document.getElementById('demoQ1')) {
    const samples = [
      '请你根据我的资料，信息，帮我分析一下，我现阶段是考研还是找工作更好？',
      '我总是在成长和稳定之间反复摇摆，你先用深度理解帮我看清自己。',
      '帮我开启多角色聊天，从当前的我、未来的我、理性导师和情绪支持者几个视角看这个问题。'
    ];
    samples.forEach((q, i) => {
      const b = document.createElement('button');
      b.id = 'demoQ' + (i + 1);
      b.type = 'button';
      b.className = 'secondary-btn';
      b.style.marginRight = '8px';
      b.style.marginTop = '8px';
      b.textContent = '示例问题 ' + (i + 1);
      b.onclick = () => {
        chatInput.value = q;
        chatInput.focus();
      };
      welcomeActions.appendChild(b);
    });
  }
}

function renderMessages(messages) {
  messageList.innerHTML = "";
  if (messages.length > 0) {
    welcomeBlock.style.display = "none";
    welcomeModeCards.style.display = "none";
  }
  messages.forEach(msg => {
    if (msg.role === "card") {
      const card = typeof msg.content === "string" ? {title: "阶段卡片", items: [msg.content]} : msg.content;
      const wrap = document.createElement("div");
      wrap.className = "mini-summary";
      wrap.innerHTML = `<div>${card.title}</div><div class="summary-grid"></div>`;
      const grid = wrap.querySelector('.summary-grid');
      (card.items || []).forEach((item, i) => {
        const d = document.createElement('div');
        d.className = 'summary-item';
        d.innerHTML = `<div class="k">要点 ${i+1}</div><div class="v">${typeof item === 'string' ? item : JSON.stringify(item)}</div>`;
        grid.appendChild(d);
      });
      messageList.appendChild(wrap);
      return;
    }
    const row = document.createElement("div");
    row.className = `msg-row ${msg.role === "user" ? "user" : ""}`;
    row.innerHTML = `<div class="avatar ${msg.role === "assistant" ? "ai" : ""}">${msg.role === "assistant" ? "AI" : "你"}</div><div class="bubble"></div>`;
    row.querySelector('.bubble').textContent = msg.content;
    messageList.appendChild(row);
  });
  messageList.scrollIntoView({behavior:"smooth", block:"end"});
}
async function api(path, options={}) {
  const res = await fetch(path, options);
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(txt || `HTTP ${res.status}`);
  }
  return await res.json();
}
async function loadDefaults() {
  const data = await api('/api/config/defaults');
  if (!localStorage.getItem('lifepath_base_url')) localStorage.setItem('lifepath_base_url', data.base_url);
  if (!localStorage.getItem('lifepath_model')) localStorage.setItem('lifepath_model', data.model);
  loadSettings();
}
function conversationTitleByMode(mode, subMode) {
  if (subMode === 'self_opposition') return '新的深度理解会话';
  if (subMode === 'multi_role') return '新的多角色决策会话';
  if (mode === 'deep_understanding') return '新的深度理解会话';
  if (mode === 'decision_support') return '新的决策辅助会话';
  return '新的会话';
}
async function createConversation() {
  const payload = {
    title: conversationTitleByMode(mapModeForBackend(state.primaryMode), mapSubModeForBackend(state.capability)),
    conversation_type: state.sessionType === '不留痕聊天' ? 'private' : 'standard',
  };
  const conv = await api('/api/conversations/new', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
  state.conversationId = conv.id;
  await refreshConversations();
  await loadConversation(conv.id);
}
async function refreshConversations() {
  const data = await api('/api/conversations');
  state.conversations = data.items || [];
  renderConversationList();
}
function renderConversationList() {
  leftConversations.innerHTML = '';
  state.conversations.forEach(item => {
    const div = document.createElement('div');
    div.className = 'conv-item' + (item.id === state.conversationId ? ' active' : '');
    div.innerHTML = `<div class="conv-title">${item.title}</div><div class="conv-meta"><span class="mini">${item.updated_at}</span><span class="tag">${item.type === 'private' ? '不留痕聊天' : (item.sub_mode === 'self_opposition' ? '自我对立视角' : item.sub_mode === 'multi_role' ? '多角色聊天' : item.main_mode === 'deep_understanding' ? '深度理解' : item.main_mode === 'decision_support' ? '决策辅助' : '标准会话')}</span></div>`;
    div.onclick = () => loadConversation(item.id);
    leftConversations.appendChild(div);
  });
}
async function loadConversation(id) {
  const conv = await api(`/api/conversations/${id}`);
  state.conversationId = conv.id;
  state.sessionType = conv.type === 'private' ? '不留痕聊天' : '标准会话';
  state.primaryMode = conv.main_mode === 'deep_understanding' ? '深度理解' : conv.main_mode === 'decision_support' ? '决策辅助' : '普通聊天';
  state.capability = conv.sub_mode === 'self_opposition' ? '自我对立视角' : conv.sub_mode === 'multi_role' ? '多角色聊天' : null;
  renderState();
  renderMessages(conv.messages || []);
  await refreshMemoryBlockText();
  await refreshConversations();
}
async function syncModeToBackend() {
  if (!state.conversationId) return;
  await api('/api/conversations/toggle-mode', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({
    conversation_id: state.conversationId,
    main_mode: mapModeForBackend(state.primaryMode),
    sub_mode: mapSubModeForBackend(state.capability),
  })});
  await refreshConversations();
}
async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;
  if (!state.conversationId) await createConversation();
  const settings = getStoredSettings();
  sendBtn.disabled = true;
  try {
    const data = await api('/api/chat/send', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({
      conversation_id: state.conversationId,
      message: text,
      api_key: settings.api_key,
      base_url: settings.base_url,
      model: settings.model,
      mock: state.mock,
      main_mode: mapModeForBackend(state.primaryMode),
      sub_mode: mapSubModeForBackend(state.capability),
    })});
    chatInput.value = '';
    renderMessages(data.conversation.messages || []);
    await refreshMemoryBlockText(data.user_memory);
    await refreshConversations();
    if (state.primaryMode === '普通聊天' && data.reply.includes('更深的分析模式')) {
      toast(data.reply, true);
    }
  } catch (err) {
    toast('发送失败：' + err.message, true);
  } finally {
    sendBtn.disabled = false;
  }
}
async function refreshMemoryBlockText(memoryPayload=null) {
  let payload = memoryPayload;
  let profile = null;
  if (!payload) {
    const data = await api('/api/memory');
    payload = data.memory;
    profile = data.profile;
  }
  const blocks = $$('.memory-block');
  const dynamic = payload.dynamic_memory || [];
  const snapshot = payload.current_snapshot || {};
  // update texts
  if (blocks[0]) blocks[0].querySelector('.m-v').innerHTML = `<strong>默认简化</strong>：${payload.static_profile_summary || '尚未建立长期画像。'}`;
  if (blocks[1]) {
    const latest = dynamic.length ? dynamic[dynamic.length-1].summary : '最近暂无新的长期动态记忆。';
    blocks[1].querySelector('.m-v').innerHTML = `<strong>全局动态记忆</strong>：${latest}`;
    blocks[1].dataset.memoryPoints = JSON.stringify(dynamic.length ? dynamic.map(x => x.summary) : ['最近暂无新的长期动态记忆。']);
  }
  if (blocks[2]) {
    blocks[2].querySelector('.m-v').innerHTML = `<strong>当前会话短期记忆</strong>：只服务当前聊天线程，帮助回复保持连续、贴近当下。`;
  }
  if (blocks[3]) {
    blocks[3].querySelector('.m-v').innerHTML = `<strong>当前状态快照</strong>：${snapshot.emotion_state || 'stable'} / ${snapshot.decision_state || 'none'} / ${snapshot.life_phase || 'stable_phase'}`;
    blocks[3].dataset.memoryPoints = JSON.stringify([
      `emotion_state: ${snapshot.emotion_state || 'stable'}`,
      `decision_state: ${snapshot.decision_state || 'none'}`,
      `life_phase: ${snapshot.life_phase || 'stable_phase'}`,
      `confidence: ${snapshot.confidence ?? 0.5}`,
    ]);
  }
}
function openMemoryModal(data) {
  memoryModalKicker.textContent = data.kicker || 'Memory Layer';
  memoryModalTitle.textContent = data.title || '记忆详情';
  memoryModalDesc.textContent = data.desc || '';
  memoryPoints.innerHTML = '';
  memoryTimeline.innerHTML = '';
  memoryTags.innerHTML = '';
  (data.points || []).forEach(point => {
    const div = document.createElement('div');
    div.className = 'memory-point';
    div.textContent = point;
    memoryPoints.appendChild(div);
  });
  (data.timeline || []).forEach(item => {
    const div = document.createElement('div');
    div.className = 'timeline-item';
    div.textContent = item;
    memoryTimeline.appendChild(div);
  });
  (data.tags || []).forEach(tag => {
    const span = document.createElement('span');
    span.className = 'memory-tag';
    span.textContent = tag;
    memoryTags.appendChild(span);
  });
  appShell.classList.add('blurred');
  memoryOverlay.classList.add('show');
  document.body.style.overflow = 'hidden';
}
function closeMemoryModal() {
  appShell.classList.remove('blurred');
  memoryOverlay.classList.remove('show');
  document.body.style.overflow = '';
}
memoryBlocks.forEach(block => block.addEventListener('click', function () {
  openMemoryModal({
    title: this.dataset.memoryTitle,
    kicker: this.dataset.memoryKicker,
    desc: this.dataset.memoryDesc,
    points: JSON.parse(this.dataset.memoryPoints || '[]'),
    tags: JSON.parse(this.dataset.memoryTags || '[]'),
    timeline: JSON.parse(this.dataset.memoryTimeline || '[]')
  });
}));
memoryCloseBtn.onclick = closeMemoryModal;
memoryOverlay.addEventListener('click', e => { if (e.target === memoryOverlay) closeMemoryModal(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') { closeMemoryModal(); dropdown.classList.remove('open'); }});
trigger.addEventListener('click', e => { e.stopPropagation(); dropdown.classList.toggle('open'); });
$$("[data-session-type]").forEach(btn => btn.addEventListener('click', async function(e){
  e.stopPropagation();
  state.sessionType = this.dataset.sessionType;
  renderState();
  if (state.conversationId) {
    await api('/api/conversations/update-type', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({conversation_id: state.conversationId, conversation_type: state.sessionType === '不留痕聊天' ? 'private' : 'standard'})});
  }
  toast(state.sessionType === '不留痕聊天' ? '<strong>不留痕聊天</strong> 已启用。将读取已有理解，但不会写回长期记忆。' : '<strong>标准会话</strong> 已启用。会正常读取并写回长期理解。');
}));
$$('[data-primary-select]').forEach(row => row.addEventListener('click', async function(e){
  e.stopPropagation();
  state.primaryMode = this.dataset.primarySelect;
  state.capability = null;
  renderState();
  dropdown.classList.remove('open');
  await syncModeToBackend();
  toast(`<strong>${state.primaryMode}</strong> 已启用。二级能力已关闭；如需更强能力，可在对应模式下继续开启。`);
}));
$$('.mode-subitem').forEach(item => item.addEventListener('click', async function(e){
  e.stopPropagation();
  state.primaryMode = this.dataset.parent;
  state.capability = this.dataset.capability;
  renderState();
  dropdown.classList.remove('open');
  await syncModeToBackend();
  toast(state.capabilityDescriptions[state.capability], true);
}));
document.addEventListener('click', e => { if (!dropdown.contains(e.target)) dropdown.classList.remove('open'); });
sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }});
saveSettingsBtn.onclick = () => saveSettings();
mockToggleBtn.onclick = () => { state.mock = !state.mock; localStorage.setItem('lifepath_mock_mode', String(state.mock)); mockToggleDesc.textContent = `当前：${state.mock ? '开启' : '关闭'}`; toast(`Mock 模式已${state.mock ? '开启' : '关闭'}。`); };
addUnderstandingBtn.onclick = () => hiddenFileInput.click();
hiddenFileInput.addEventListener('change', async function(){
  if (!this.files || !this.files.length) return;
  const form = new FormData();
  const s = getStoredSettings();
  form.append('api_key', s.api_key);
  form.append('base_url', s.base_url);
  form.append('model', s.model);
  form.append('mock', String(state.mock));
  for (const file of this.files) form.append('files', file);
  try {
    const res = await fetch('/api/upload-profile-files', {method:'POST', body: form});
    const data = await res.json();
    toast(data.message || '资料已纳入理解。', true);
    await refreshMemoryBlockText(data.memory);
  } catch (err) {
    toast('上传失败', true);
  }
});
pasteUnderstandingBtn.onclick = async () => {
  const text = prompt('请粘贴想补充的内容：', '例如：我最近在考虑转岗，但对离开熟悉环境有点犹豫。');
  if (!text || !text.trim()) return;
  const blob = new Blob([text.trim()], {type: 'text/plain'});
  const file = new File([blob], 'manual_note.txt', {type:'text/plain'});
  const dt = new DataTransfer(); dt.items.add(file); hiddenFileInput.files = dt.files; hiddenFileInput.dispatchEvent(new Event('change'));
};
$(".solid-btn").onclick = createConversation;

(async function init(){
  insertEnhancementActions();
  await loadDefaults();
  renderState();
  await refreshConversations();
  if (state.conversations.length) await loadConversation(state.conversations[0].id); else await createConversation();
})();