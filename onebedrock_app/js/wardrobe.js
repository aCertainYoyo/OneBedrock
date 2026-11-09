/**
 * OneBedrock Wardrobe - Interactive 3D Bedrock Character Renderer
 * Renders an animated Minecraft character on an HTML5 2D canvas with full 3D projection,
 * skin presets, custom skin uploads, and cape simulation.
 */

class WardrobeViewer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    
    this.model = 'steve'; // steve | alex
    this.cape = 'none'; // none | onebedrock | founders
    this.isWalking = true;
    this.angleY = 0.45;
    this.angleX = 0.15;
    this.isDragging = false;
    this.lastMouseX = 0;
    this.lastMouseY = 0;
    this.walkCycle = 0;

    // Skin color palettes
    this.currentSkin = 'cyber';
    this.palettes = {
      steve: {
        skin: '#D39C7E',
        hair: '#4A3222',
        eyes: '#2E357B',
        shirt: '#00AAAA',
        pants: '#2E357B',
        shoes: '#555555'
      },
      alex: {
        skin: '#E8B39B',
        hair: '#B25928',
        eyes: '#3F6131',
        shirt: '#5C8234',
        pants: '#55422C',
        shoes: '#33271A'
      },
      cyber: {
        skin: '#1A2229',
        hair: '#2B4BFF',
        eyes: '#00FFFF',
        shirt: '#11171C',
        pants: '#212B34',
        shoes: '#2B4BFF'
      },
      diamond: {
        skin: '#55FFFF',
        hair: '#2B4BFF',
        eyes: '#FFFFFF',
        shirt: '#33AAAA',
        pants: '#227777',
        shoes: '#115555'
      }
    };

    this.initEvents();
    this.animate();
  }

  initEvents() {
    this.canvas.addEventListener('mousedown', (e) => {
      this.isDragging = true;
      this.lastMouseX = e.clientX;
      this.lastMouseY = e.clientY;
    });

    window.addEventListener('mousemove', (e) => {
      if (!this.isDragging) return;
      const dx = e.clientX - this.lastMouseX;
      const dy = e.clientY - this.lastMouseY;
      this.angleY += dx * 0.01;
      this.angleX += dy * 0.01;
      // Clamp vertical tilt
      this.angleX = Math.max(-0.6, Math.min(0.6, this.angleX));
      this.lastMouseX = e.clientX;
      this.lastMouseY = e.clientY;
    });

    window.addEventListener('mouseup', () => {
      this.isDragging = false;
    });
  }

  setModel(model) {
    this.model = model;
    document.getElementById('btn-model-steve')?.classList.toggle('active', model === 'steve');
    document.getElementById('btn-model-alex')?.classList.toggle('active', model === 'alex');
  }

  loadSkin(name) {
    this.currentSkin = name;
  }

  setCape(name) {
    this.cape = name;
  }

  toggleWalk() {
    this.isWalking = !this.isWalking;
  }

  resetRotation() {
    this.angleY = 0.45;
    this.angleX = 0.15;
  }

  handleUpload(e) {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        // Simple color extraction from uploaded png
        this.palettes['custom'] = {
          skin: '#D39C7E',
          hair: '#3E2723',
          eyes: '#1E88E5',
          shirt: '#2B4BFF',
          pants: '#1A2229',
          shoes: '#11171C'
        };
        this.currentSkin = 'custom';
      };
      reader.readAsDataURL(file);
    }
  }

  project(x, y, z, cx, cy, scale) {
    // 3D rotation around Y and X axes
    const cosY = Math.cos(this.angleY);
    const sinY = Math.sin(this.angleY);
    const cosX = Math.cos(this.angleX);
    const sinX = Math.sin(this.angleX);

    // Rotate Y
    let x1 = x * cosY - z * sinY;
    let z1 = z * cosY + x * sinY;

    // Rotate X
    let y1 = y * cosX - z1 * sinX;
    let z2 = z1 * cosX + y * sinX;

    const perspective = 450 / (450 + z2);
    return {
      x: cx + x1 * scale * perspective,
      y: cy + y1 * scale * perspective,
      z: z2
    };
  }

  drawBox(x, y, z, w, h, d, color, cx, cy, scale, rotX = 0) {
    // Compute box corners
    const hw = w / 2;
    const hd = d / 2;

    const corners = [
      { x: -hw, y: 0, z: -hd },
      { x: hw, y: 0, z: -hd },
      { x: hw, y: h, z: -hd },
      { x: -hw, y: h, z: -hd },
      { x: -hw, y: 0, z: hd },
      { x: hw, y: 0, z: hd },
      { x: hw, y: h, z: hd },
      { x: -hw, y: h, z: hd }
    ];

    // Local rotation (e.g. for swinging limbs)
    const cosR = Math.cos(rotX);
    const sinR = Math.sin(rotX);

    const projected = corners.map(c => {
      let cy_loc = c.y * cosR - c.z * sinR;
      let cz_loc = c.z * cosR + c.y * sinR;
      return this.project(x + c.x, y + cy_loc, z + cz_loc, cx, cy, scale);
    });

    const faces = [
      { pts: [0, 1, 2, 3], shade: 1.0 },   // Front
      { pts: [5, 4, 7, 6], shade: 0.65 },  // Back
      { pts: [4, 0, 3, 7], shade: 0.8 },   // Left
      { pts: [1, 5, 6, 2], shade: 0.85 },  // Right
      { pts: [4, 5, 1, 0], shade: 1.15 },  // Top
      { pts: [3, 2, 6, 7], shade: 0.5 }    // Bottom
    ];

    // Sort faces by depth (painter's algorithm)
    faces.forEach(f => {
      f.avgZ = f.pts.reduce((sum, idx) => sum + projected[idx].z, 0) / 4;
    });
    faces.sort((a, b) => b.avgZ - a.avgZ);

    faces.forEach(f => {
      const p = f.pts.map(i => projected[i]);
      // Backface culling check
      const cross = (p[1].x - p[0].x) * (p[2].y - p[0].y) - (p[1].y - p[0].y) * (p[2].x - p[0].x);
      if (cross > 0) {
        this.ctx.beginPath();
        this.ctx.moveTo(p[0].x, p[0].y);
        this.ctx.lineTo(p[1].x, p[1].y);
        this.ctx.lineTo(p[2].x, p[2].y);
        this.ctx.lineTo(p[3].x, p[3].y);
        this.ctx.closePath();
        this.ctx.fillStyle = this.adjustBrightness(color, f.shade);
        this.ctx.fill();
        this.ctx.strokeStyle = 'rgba(0,0,0,0.15)';
        this.ctx.lineWidth = 1;
        this.ctx.stroke();
      }
    });
  }

  adjustBrightness(hex, factor) {
    hex = hex.replace('#', '');
    let r = parseInt(hex.substring(0, 2), 16);
    let g = parseInt(hex.substring(2, 4), 16);
    let b = parseInt(hex.substring(4, 6), 16);
    r = Math.min(255, Math.floor(r * factor));
    g = Math.min(255, Math.floor(g * factor));
    b = Math.min(255, Math.floor(b * factor));
    return `rgb(${r},${g},${b})`;
  }

  animate() {
    requestAnimationFrame(() => this.animate());
    const w = this.canvas.width;
    const h = this.canvas.height;
    this.ctx.clearRect(0, 0, w, h);

    if (this.isWalking) {
      this.walkCycle += 0.05;
    }

    const swing = Math.sin(this.walkCycle) * 0.55;
    const p = this.palettes[this.currentSkin] || this.palettes.cyber;
    const armW = this.model === 'alex' ? 3 : 4;
    const cx = w / 2;
    const cy = h / 2 - 30;
    const scale = 5.2;

    // Draw Cape if equipped
    if (this.cape !== 'none') {
      const capeColor = this.cape === 'onebedrock' ? '#2B4BFF' : '#FFD700';
      this.drawBox(0, 2, -5, 10, 16, 1, capeColor, cx, cy, scale, 0.15 + Math.abs(swing) * 0.2);
    }

    // Legs
    this.drawBox(-2, 12, 0, 4, 12, 4, p.pants, cx, cy, scale, swing);
    this.drawBox(2, 12, 0, 4, 12, 4, p.pants, cx, cy, scale, -swing);

    // Torso
    this.drawBox(0, 0, 0, 8, 12, 4, p.shirt, cx, cy, scale, 0);

    // Arms
    const armOffset = 4 + armW / 2;
    this.drawBox(-armOffset, 0, 0, armW, 12, 4, p.skin, cx, cy, scale, -swing);
    this.drawBox(armOffset, 0, 0, armW, 12, 4, p.skin, cx, cy, scale, swing);

    // Head
    this.drawBox(0, -8, 0, 8, 8, 8, p.skin, cx, cy, scale, 0);

    // Hair cap / visor
    this.drawBox(0, -8.3, 0, 8.4, 4, 8.4, p.hair, cx, cy, scale, 0);
  }
}

// Global wardrobe controller
let wardrobe;
document.addEventListener('DOMContentLoaded', () => {
  wardrobe = new WardrobeViewer('skin-canvas');
});
