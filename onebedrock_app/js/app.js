/**
 * OneBedrock Application Core Controller.
 * Powers PolyGlass navigation, Bedrock launch flows, Xbox Live profile management,
 * and instance configurations.
 */

class OneBedrockApp {
  constructor() {
    this.currentView = 'home';
    this.state = {
      accounts: [],
      activeAccount: null,
      instances: [],
      activeInstance: null,
      metrics: {},
      presets: {},
      servers: [],
      packs: [],
      news: [],
      isRunning: false
    };

    this.consolePollInterval = null;
    this.init();
  }

  async init() {
    this.initLucide();
    await this.refreshState();
    this.renderHome();
    this.renderInstances();
    this.renderBrowse();
    this.renderStats();
    this.startStatusPoller();
  }

  initLucide() {
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  async api(endpoint, method = 'GET', body = null) {
    try {
      const options = {
        method,
        headers: { 'Content-Type': 'application/json' }
      };
      if (body) options.body = JSON.stringify(body);
      const res = await fetch(`/api/${endpoint}`, options);
      return await res.json();
    } catch (e) {
      console.warn(`API Error [${endpoint}]:`, e);
      return null;
    }
  }

  async refreshState() {
    const [statusData, accData, instData, optData, browseData] = await Promise.all([
      this.api('status'),
      this.api('accounts'),
      this.api('instances'),
      this.api('optimizer'),
      this.api('browse')
    ]);

    if (statusData) {
      this.state.isRunning = statusData.is_running;
      this.updateStatusBadge(statusData.bedrock?.installed);
    }
    if (accData) {
      this.state.accounts = accData.accounts || [];
      this.state.activeAccount = accData.active_account;
      this.updateNavbarProfile();
    }
    if (instData) {
      this.state.instances = instData.instances || [];
      this.state.activeInstance = instData.active_instance;
      this.updateHeroInstance();
    }
    if (optData) {
      this.state.metrics = optData.metrics || {};
      this.state.presets = optData.presets || {};
      this.updateMetricsUI();
    }
    if (browseData) {
      this.state.servers = browseData.servers || [];
      this.state.packs = browseData.packs || [];
      this.state.news = browseData.news || [];
    }
  }

  navigate(viewName) {
    this.currentView = viewName;
    document.querySelectorAll('.view-panel').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-tab').forEach(el => el.classList.remove('active'));

    const targetView = document.getElementById(`view-${viewName}`);
    const targetTab = document.querySelector(`.nav-tab[data-view="${viewName}"]`);
    if (targetView) targetView.classList.add('active');
    if (targetTab) targetTab.classList.add('active');

    this.initLucide();
  }

  updateStatusBadge(installed) {
    const label = document.getElementById('bedrock-status-label');
    if (label) {
      label.textContent = installed ? 'Bedrock Ready' : 'Bedrock Standby';
    }
  }

  updateNavbarProfile() {
    const acc = this.state.activeAccount;
    if (!acc) return;
    const nameEl = document.getElementById('navbar-gamertag');
    const picEl = document.getElementById('navbar-gamerpic');
    const statsTag = document.getElementById('stats-gamertag');

    if (nameEl) nameEl.textContent = acc.gamertag;
    if (picEl) picEl.src = acc.gamerpic_url;
    if (statsTag) statsTag.textContent = acc.gamertag;
  }

  updateHeroInstance() {
    const inst = this.state.activeInstance;
    if (!inst) return;
    const nameEl = document.getElementById('hero-instance-name');
    const tagEl = document.getElementById('hero-instance-tag');
    const inspectName = document.getElementById('inspect-name');
    const inspectDesc = document.getElementById('inspect-desc');

    if (nameEl) nameEl.textContent = inst.name;
    if (tagEl) tagEl.textContent = `${inst.version} • ${inst.tag}`;
    if (inspectName) inspectName.textContent = inst.name;
    if (inspectDesc) inspectDesc.textContent = inst.description;
  }

  updateMetricsUI() {
    const m = this.state.metrics;
    const fpsBadge = document.getElementById('metric-fps-badge');
    const vsyncToggle = document.getElementById('setting-toggle-vsync');
    const rtxToggle = document.getElementById('setting-toggle-rtx');
    const pathInput = document.getElementById('settings-mojang-path');

    if (fpsBadge) {
      fpsBadge.textContent = m.vsync ? 'VSync ON (60 FPS)' : 'Uncapped (VSync OFF)';
    }
    if (vsyncToggle) vsyncToggle.checked = !m.vsync;
    if (rtxToggle) rtxToggle.checked = !!m.raytracing;
    if (pathInput) pathInput.value = m.options_path || 'com.mojang/minecraftpe/options.txt';

    this.renderInspectOptions();
  }

  renderHome() {
    const grid = document.getElementById('home-news-grid');
    if (!grid) return;
    grid.innerHTML = this.state.news.map(n => `
      <div class="card p-6 flex flex-col justify-between space-y-4 hover:border-accent/40 transition-all">
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-accent/20 text-accent">${n.category}</span>
            <span class="text-xs text-secondary">${n.date}</span>
          </div>
          <h3 class="text-base font-bold text-white hover:text-accent transition-colors">${n.title}</h3>
          <p class="text-xs text-secondary leading-relaxed">${n.summary}</p>
        </div>
        <div class="pt-2 border-t border-white/5 flex items-center justify-between text-xs text-accent font-semibold cursor-pointer">
          <span>Read Changelog</span>
          <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
        </div>
      </div>
    `).join('');
    this.initLucide();
  }

  renderInstances() {
    const grid = document.getElementById('instances-grid');
    if (!grid) return;
    grid.innerHTML = this.state.instances.map(inst => {
      const isActive = inst.id === this.state.activeInstance?.id;
      return `
        <div class="card p-6 flex flex-col justify-between space-y-4 cursor-pointer ${isActive ? 'border-accent shadow-[0_0_20px_rgba(43,75,255,0.25)]' : 'hover:border-white/20'}" onclick="app.switchInstance('${inst.id}')">
          <div class="flex items-start justify-between">
            <div class="w-12 h-12 rounded-2xl ${isActive ? 'bg-accent text-white' : 'bg-component text-secondary'} flex items-center justify-center">
              <i data-lucide="${inst.icon || 'layers'}" class="w-6 h-6"></i>
            </div>
            ${isActive ? '<span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-accent text-white">ACTIVE</span>' : ''}
          </div>

          <div class="space-y-1">
            <h3 class="text-lg font-bold text-white">${inst.name}</h3>
            <span class="text-xs text-secondary">${inst.version} • ${inst.tag}</span>
            <p class="text-xs text-secondary/80 mt-2 leading-relaxed">${inst.description}</p>
          </div>

          <div class="pt-3 border-t border-white/5 flex items-center justify-between text-xs">
            <span class="text-secondary">${inst.playtime_minutes} mins played</span>
            <span class="text-accent font-semibold">${isActive ? 'Selected' : 'Select'}</span>
          </div>
        </div>
      `;
    }).join('');
    this.initLucide();
  }

  renderInspectOptions() {
    const grid = document.getElementById('inspect-options-grid');
    if (!grid) return;
    const m = this.state.metrics;
    const items = [
      { label: 'Framerate Cap', val: m.vsync ? 'VSync 60 FPS' : 'Uncapped', color: 'text-success' },
      { label: 'Render Distance', val: `${m.render_distance || 12} Chunks`, color: 'text-white' },
      { label: 'Hardware Ray Tracing', val: m.raytracing ? 'Enabled' : 'Disabled', color: m.raytracing ? 'text-accent' : 'text-secondary' },
      { label: 'Anti-Aliasing (MSAA)', val: `${m.msaa || 2}x`, color: 'text-white' }
    ];

    grid.innerHTML = items.map(item => `
      <div class="p-4 rounded-xl bg-component border border-white/5 space-y-1">
        <span class="text-[10px] uppercase font-bold text-secondary tracking-wider">${item.label}</span>
        <div class="text-sm font-bold ${item.color}">${item.val}</div>
      </div>
    `).join('');
  }

  renderBrowse() {
    // Servers
    const serversGrid = document.getElementById('browse-servers-grid');
    if (serversGrid) {
      serversGrid.innerHTML = this.state.servers.map(s => `
        <div class="card p-6 flex flex-col justify-between space-y-4 hover:border-accent/40 transition-all">
          <div class="flex items-start justify-between">
            <div class="flex items-center space-x-3">
              <img src="${s.icon}" class="w-10 h-10 rounded-xl bg-component">
              <div>
                <h3 class="text-base font-bold text-white">${s.name}</h3>
                <span class="text-xs text-success font-medium">${s.players}</span>
              </div>
            </div>
            <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-white/5 text-secondary border border-white/10">${s.tag}</span>
          </div>

          <p class="text-xs text-secondary leading-relaxed">${s.description}</p>

          <div class="pt-2 border-t border-white/5 flex items-center justify-between">
            <span class="text-[11px] font-mono text-secondary">${s.ip}</span>
            <button class="btn-primary px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1" onclick="app.launchBedrock('${s.ip}', ${s.port})">
              <i data-lucide="play" class="w-3.5 h-3.5 fill-white"></i>
              <span>Play</span>
            </button>
          </div>
        </div>
      `).join('');
    }

    // Packs
    const packsGrid = document.getElementById('browse-packs-grid');
    if (packsGrid) {
      packsGrid.innerHTML = this.state.packs.map(p => `
        <div class="card p-6 flex flex-col justify-between space-y-4 hover:border-accent/40 transition-all">
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-accent/20 text-accent">${p.category}</span>
              <span class="text-xs text-warning flex items-center"><i data-lucide="star" class="w-3 h-3 fill-warning inline mr-1"></i>${p.rating}</span>
            </div>
            <h3 class="text-base font-bold text-white">${p.name}</h3>
            <span class="text-xs text-secondary">by ${p.author} • ${p.downloads} downloads</span>
            <p class="text-xs text-secondary/80 leading-relaxed">${p.description}</p>
          </div>

          <div class="pt-3 border-t border-white/5 flex items-center justify-between">
            <span class="text-xs text-secondary">${p.type}</span>
            <button class="btn-secondary px-3 py-1.5 rounded-lg text-xs font-semibold ${p.installed ? 'active' : ''}">
              ${p.installed ? 'Installed' : 'Get Add-on'}
            </button>
          </div>
        </div>
      `).join('');
    }

    this.initLucide();
  }

  renderStats() {
    // Stat cards update automatically from state
  }

  async switchInstance(id) {
    const res = await this.api('instances/switch', 'POST', { id });
    if (res && res.success) {
      this.state.activeInstance = res.active;
      this.updateHeroInstance();
      this.renderInstances();
    }
  }

  async applyPreset(preset) {
    const res = await this.api('optimizer/preset', 'POST', { preset });
    if (res && res.success) {
      this.state.metrics = res.metrics;
      this.updateMetricsUI();
    }
  }

  async launchBedrock(serverIp = null, serverPort = 19132) {
    const btn = document.getElementById('btn-main-launch');
    const btnText = document.getElementById('btn-launch-text');

    if (!serverIp) {
      const quickSelect = document.getElementById('quick-server-select');
      if (quickSelect && quickSelect.value) {
        serverIp = quickSelect.value;
      }
    }

    btn.disabled = true;
    btnText.textContent = 'STARTING BEDROCK...';

    // Open live console immediately
    this.openConsoleModal();

    const res = await this.api('launch', 'POST', {
      server_ip: serverIp,
      server_port: serverPort
    });

    setTimeout(() => {
      btn.disabled = false;
      btnText.textContent = 'LAUNCH BEDROCK';
    }, 2000);
  }

  openAccountModal() {
    const modal = document.getElementById('modal-account');
    if (!modal) return;
    this.renderAccountList();
    modal.classList.remove('hidden');
    this.initLucide();
  }

  renderAccountList() {
    const list = document.getElementById('modal-accounts-list');
    if (!list) return;
    list.innerHTML = this.state.accounts.map(acc => {
      const isActive = acc.id === this.state.activeAccount?.id;
      return `
        <div class="p-3 rounded-xl bg-component border ${isActive ? 'border-accent' : 'border-white/5'} flex items-center justify-between cursor-pointer" onclick="app.switchAccount('${acc.id}')">
          <div class="flex items-center space-x-3">
            <img src="${acc.gamerpic_url}" class="w-9 h-9 rounded-full bg-card">
            <div>
              <div class="text-sm font-bold text-white flex items-center space-x-2">
                <span>${acc.gamertag}</span>
                ${isActive ? '<span class="text-[9px] font-bold px-1.5 py-0.2 rounded bg-accent text-white">ACTIVE</span>' : ''}
              </div>
              <span class="text-[11px] text-secondary">XUID: ${acc.xuid} • Bedrock</span>
            </div>
          </div>
          <button class="text-secondary hover:text-warning p-1" onclick="event.stopPropagation(); app.removeAccount('${acc.id}')">
            <i data-lucide="trash-2" class="w-4 h-4"></i>
          </button>
        </div>
      `;
    }).join('');
    this.initLucide();
  }

  async switchAccount(id) {
    const res = await this.api('accounts/switch', 'POST', { id });
    if (res && res.success) {
      this.state.activeAccount = res.active;
      this.updateNavbarProfile();
      this.renderAccountList();
    }
  }

  async addLocalAccount() {
    const input = document.getElementById('input-new-gamertag');
    const gamertag = input.value.trim();
    if (!gamertag) return;
    const res = await this.api('accounts/add', 'POST', { gamertag });
    if (res && res.success) {
      input.value = '';
      await this.refreshState();
      this.renderAccountList();
    }
  }

  async startDeviceFlow() {
    const res = await this.api('accounts/device_flow', 'POST');
    if (res && res.success) {
      alert(`Microsoft Sign-In:\n\n1. Go to: ${res.verification_uri}\n2. Enter Code: ${res.user_code}\n\nThis links your Xbox Live profile for Bedrock Edition.`);
    }
  }

  async removeAccount(id) {
    if (this.state.accounts.length <= 1) {
      alert("At least one Bedrock account must remain active.");
      return;
    }
    const res = await this.api('accounts/remove', 'POST', { id });
    if (res && res.success) {
      await this.refreshState();
      this.renderAccountList();
    }
  }

  openSettingsModal() {
    const modal = document.getElementById('modal-settings');
    if (modal) modal.classList.remove('hidden');
    this.initLucide();
  }

  openConsoleModal() {
    const modal = document.getElementById('modal-console');
    if (modal) modal.classList.remove('hidden');
    this.pollConsoleLogs();
  }

  closeModals() {
    document.querySelectorAll('.modal-overlay').forEach(el => el.classList.add('hidden'));
  }

  async pollConsoleLogs() {
    const out = document.getElementById('console-output');
    if (!out) return;
    const res = await this.api('logs');
    if (res && res.logs) {
      out.innerHTML = res.logs.map(l => {
        const timeStr = new Date(l.timestamp * 1000).toLocaleTimeString();
        return `<div><span class="text-secondary">[${timeStr}]</span> <span class="text-accent font-semibold">[${l.stage}]</span> <span class="text-white">${l.message}</span></div>`;
      }).join('');
      out.scrollTop = out.scrollHeight;
    }
  }

  startStatusPoller() {
    setInterval(async () => {
      const logsModal = document.getElementById('modal-console');
      if (logsModal && !logsModal.classList.contains('hidden')) {
        await this.pollConsoleLogs();
      }
    }, 1500);
  }

  async toggleVSync(enabled) {
    await this.applyPreset(enabled ? 'pvp_fps' : 'balanced');
  }

  async toggleRTX(enabled) {
    await this.applyPreset(enabled ? 'ultra_rtx' : 'balanced');
  }

  openNewInstanceModal() {
    const name = prompt("Enter Bedrock Profile / Instance Name:", "Bedrock Custom Profile");
    if (name) {
      this.api('instances/create', 'POST', { name, preset: 'balanced' }).then(() => {
        this.refreshState().then(() => this.renderInstances());
      });
    }
  }
}

// Global App Instance
let app;
document.addEventListener('DOMContentLoaded', () => {
  app = new OneBedrockApp();
});
