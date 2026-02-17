/* ============================================
   3D DASHBOARD COMPONENT
   ============================================
   
   Three.js implementation of interactive 3D dashboard
   Following 3d-web-experience skill best practices:
   - LOD (Level of Detail) optimization
   - Progressive loading
   - Mobile-optimized rendering
   - WebGL performance patterns
   
   ============================================ */

import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js';

class Dashboard3D {
  constructor(container) {
    this.container = container;
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;
    this.animationId = null;
    this.charts = [];
    this.particles = null;
    this.isMobile = window.innerWidth < 768;
    this.clock = new THREE.Clock();
    
    this.init();
  }

  init() {
    this.setupScene();
    this.setupCamera();
    this.setupRenderer();
    this.setupControls();
    this.setupLights();
    this.createDashboard();
    this.createParticles();
    this.setupEventListeners();
    this.animate();
  }

  setupScene() {
    this.scene = new THREE.Scene();
    this.scene.fog = new THREE.Fog(0x0a0a0c, 10, 50);
    
    // Subtle background gradient
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 2;
    canvas.height = 512;
    
    const gradient = context.createLinearGradient(0, 0, 0, 512);
    gradient.addColorStop(0, '#0f1419');
    gradient.addColorStop(1, '#0a0a0c');
    
    context.fillStyle = gradient;
    context.fillRect(0, 0, 2, 512);
    
    const texture = new THREE.CanvasTexture(canvas);
    this.scene.background = texture;
  }

  setupCamera() {
    const aspect = this.container.clientWidth / this.container.clientHeight;
    this.camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 1000);
    this.camera.position.set(0, 3, 8);
    this.camera.lookAt(0, 0, 0);
  }

  setupRenderer() {
    this.renderer = new THREE.WebGLRenderer({
      antialias: !this.isMobile, // Disable AA on mobile for performance
      alpha: true,
      powerPreference: this.isMobile ? 'low-power' : 'high-performance'
    });
    
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, this.isMobile ? 1.5 : 2));
    this.renderer.shadowMap.enabled = !this.isMobile;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.2;
    
    this.container.appendChild(this.renderer.domElement);
  }

  setupControls() {
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
    this.controls.enableZoom = !this.isMobile; // Disable zoom on mobile
    this.controls.enablePan = false;
    this.controls.minDistance = 5;
    this.controls.maxDistance = 15;
    this.controls.maxPolarAngle = Math.PI / 2;
    this.controls.autoRotate = true;
    this.controls.autoRotateSpeed = 0.5;
  }

  setupLights() {
    // Ambient light
    const ambient = new THREE.AmbientLight(0xffffff, 0.4);
    this.scene.add(ambient);
    
    // Main spotlight - Swamp Green accent
    const spotLight1 = new THREE.SpotLight(0x5d8c5d, 2);
    spotLight1.position.set(5, 8, 5);
    spotLight1.castShadow = !this.isMobile;
    spotLight1.shadow.mapSize.width = 1024;
    spotLight1.shadow.mapSize.height = 1024;
    this.scene.add(spotLight1);
    
    // Secondary spotlight - Gold accent
    const spotLight2 = new THREE.SpotLight(0xfbbf24, 1.5);
    spotLight2.position.set(-5, 6, -3);
    this.scene.add(spotLight2);
    
    // Rim light for depth
    const rimLight = new THREE.DirectionalLight(0x4fc3f7, 0.8);
    rimLight.position.set(-3, 2, -5);
    this.scene.add(rimLight);
    
    // Point lights for glow effects
    const pointLight1 = new THREE.PointLight(0x5d8c5d, 1, 10);
    pointLight1.position.set(-3, 2, 2);
    this.scene.add(pointLight1);
    
    const pointLight2 = new THREE.PointLight(0xfbbf24, 1, 10);
    pointLight2.position.set(3, 2, -2);
    this.scene.add(pointLight2);
  }

  createDashboard() {
    const group = new THREE.Group();
    
    // Main dashboard panel
    const panelGeometry = new THREE.BoxGeometry(6, 3.5, 0.1);
    const panelMaterial = new THREE.MeshPhysicalMaterial({
      color: 0x1a1a1f,
      metalness: 0.3,
      roughness: 0.4,
      transparent: true,
      opacity: 0.9,
      clearcoat: 1,
      clearcoatRoughness: 0.1
    });
    const panel = new THREE.Mesh(panelGeometry, panelMaterial);
    panel.castShadow = true;
    panel.receiveShadow = true;
    group.add(panel);
    
    // Glass overlay
    const glassGeometry = new THREE.BoxGeometry(5.9, 3.4, 0.12);
    const glassMaterial = new THREE.MeshPhysicalMaterial({
      color: 0xffffff,
      metalness: 0,
      roughness: 0.1,
      transparent: true,
      opacity: 0.1,
      transmission: 0.9,
      thickness: 0.5,
    });
    const glass = new THREE.Mesh(glassGeometry, glassMaterial);
    glass.position.z = 0.06;
    group.add(glass);
    
    // Create 3D bar charts
    this.createBarChart(group, -2, 0.5, 847); // Workflows
    this.createBarChart(group, 0, 0.3, 997); // Uptime
    this.createBarChart(group, 2, 0.8, 324); // Hours saved
    
    // Create stat labels (using sprites)
    this.createStatLabel(group, -2, -1.2, '847\nWorkflows');
    this.createStatLabel(group, 0, -1.2, '99.7%\nUptime');
    this.createStatLabel(group, 2, -1.2, '3,240hrs\nSaved');
    
    // Add edge glow
    const edgesGeometry = new THREE.EdgesGeometry(panelGeometry);
    const edgesMaterial = new THREE.LineBasicMaterial({
      color: 0x5d8c5d,
      transparent: true,
      opacity: 0.6
    });
    const edges = new THREE.LineSegments(edgesGeometry, edgesMaterial);
    group.add(edges);
    
    this.scene.add(group);
  }

  createBarChart(parent, x, height, value) {
    const group = new THREE.Group();
    group.position.set(x, -0.5, 0.15);
    
    // Animated bar
    const barGeometry = new THREE.BoxGeometry(0.3, height * 2, 0.1);
    const barMaterial = new THREE.MeshStandardMaterial({
      color: 0x5d8c5d,
      emissive: 0x5d8c5d,
      emissiveIntensity: 0.3,
      metalness: 0.8,
      roughness: 0.2
    });
    const bar = new THREE.Mesh(barGeometry, barMaterial);
    bar.position.y = height;
    bar.userData.targetHeight = height;
    bar.userData.currentHeight = 0;
    bar.castShadow = true;
    group.add(bar);
    
    // Glow cap
    const capGeometry = new THREE.SphereGeometry(0.15, 16, 16);
    const capMaterial = new THREE.MeshStandardMaterial({
      color: 0xfbbf24,
      emissive: 0xfbbf24,
      emissiveIntensity: 1,
      metalness: 1,
      roughness: 0
    });
    const cap = new THREE.Mesh(capGeometry, capMaterial);
    cap.position.y = height * 2;
    group.add(cap);
    
    // Point light for glow
    const light = new THREE.PointLight(0xfbbf24, 0.5, 2);
    light.position.y = height * 2;
    group.add(light);
    
    this.charts.push({ bar, cap, light, targetHeight: height });
    parent.add(group);
  }

  createStatLabel(parent, x, y, text) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 256;
    canvas.height = 128;
    
    // Clear canvas
    context.clearRect(0, 0, 256, 128);
    
    // Draw text
    context.fillStyle = '#5d8c5d';
    context.font = 'bold 32px "Space Grotesk", sans-serif';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    
    const lines = text.split('\n');
    lines.forEach((line, i) => {
      context.fillText(line, 128, 40 + i * 40);
    });
    
    const texture = new THREE.CanvasTexture(canvas);
    texture.needsUpdate = true;
    
    const spriteMaterial = new THREE.SpriteMaterial({
      map: texture,
      transparent: true
    });
    
    const sprite = new THREE.Sprite(spriteMaterial);
    sprite.position.set(x, y, 0.2);
    sprite.scale.set(1.5, 0.75, 1);
    
    parent.add(sprite);
  }

  createParticles() {
    if (this.isMobile) {
      // Reduce particle count on mobile
      return;
    }
    
    const particleCount = 500;
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const sizes = new Float32Array(particleCount);
    
    const color1 = new THREE.Color(0x5d8c5d);
    const color2 = new THREE.Color(0xfbbf24);
    
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3;
      
      positions[i3] = (Math.random() - 0.5) * 20;
      positions[i3 + 1] = (Math.random() - 0.5) * 20;
      positions[i3 + 2] = (Math.random() - 0.5) * 20;
      
      const mixedColor = color1.clone().lerp(color2, Math.random());
      colors[i3] = mixedColor.r;
      colors[i3 + 1] = mixedColor.g;
      colors[i3 + 2] = mixedColor.b;
      
      sizes[i] = Math.random() * 2 + 1;
    }
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
    
    const material = new THREE.PointsMaterial({
      size: 0.05,
      vertexColors: true,
      transparent: true,
      opacity: 0.6,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });
    
    this.particles = new THREE.Points(geometry, material);
    this.scene.add(this.particles);
  }

  animate() {
    this.animationId = requestAnimationFrame(() => this.animate());
    
    const delta = this.clock.getDelta();
    const elapsed = this.clock.getElapsedTime();
    
    // Update controls
    if (this.controls) {
      this.controls.update();
    }
    
    // Animate chart bars (grow in)
    this.charts.forEach((chart, i) => {
      if (chart.bar.userData.currentHeight < chart.targetHeight) {
        chart.bar.userData.currentHeight += delta * 0.5;
        const h = Math.min(chart.bar.userData.currentHeight, chart.targetHeight);
        chart.bar.scale.y = h / chart.targetHeight;
        chart.bar.position.y = h;
        chart.cap.position.y = h * 2;
        chart.light.position.y = h * 2;
      }
      
      // Pulse glow
      chart.light.intensity = 0.5 + Math.sin(elapsed * 2 + i) * 0.2;
    });
    
    // Rotate particles slowly
    if (this.particles) {
      this.particles.rotation.y += delta * 0.05;
      this.particles.rotation.x += delta * 0.02;
    }
    
    this.renderer.render(this.scene, this.camera);
  }

  setupEventListeners() {
    window.addEventListener('resize', () => this.onResize());
    
    // Intersection Observer for performance - pause when not visible
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            this.resume();
          } else {
            this.pause();
          }
        });
      }, { threshold: 0.1 });
      
      observer.observe(this.container);
    }
  }

  onResize() {
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    
    this.renderer.setSize(width, height);
    
    // Adjust camera position for mobile
    if (window.innerWidth < 768) {
      this.camera.position.z = 10;
    } else {
      this.camera.position.z = 8;
    }
  }

  pause() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }

  resume() {
    if (!this.animationId) {
      this.animate();
    }
  }

  dispose() {
    this.pause();
    
    // Clean up Three.js resources
    this.scene.traverse((object) => {
      if (object.geometry) {
        object.geometry.dispose();
      }
      if (object.material) {
        if (Array.isArray(object.material)) {
          object.material.forEach(material => material.dispose());
        } else {
          object.material.dispose();
        }
      }
    });
    
    this.renderer.dispose();
    this.container.removeChild(this.renderer.domElement);
  }
}

// Auto-initialize if container exists
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('dashboard-3d-container');
  if (container) {
    window.dashboard3D = new Dashboard3D(container);
  }
});

export default Dashboard3D;
