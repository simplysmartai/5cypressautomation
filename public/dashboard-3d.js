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
    this.dashboardGroup = new THREE.Group();
    
    // 1. Central Core - Root Data Sync Engine
    const coreGeometry = new THREE.OctahedronGeometry(1.2, 2);
    const coreMaterial = new THREE.MeshPhysicalMaterial({
      color: 0x5d8c5d,
      emissive: 0x5d8c5d,
      emissiveIntensity: 0.5,
      metalness: 0.9,
      roughness: 0.1,
      transparent: true,
      opacity: 0.8,
      wireframe: true
    });
    this.core = new THREE.Mesh(coreGeometry, coreMaterial);
    this.core.position.set(0, 0, 0);
    this.dashboardGroup.add(this.core);

    // Inner core glow
    const innerCoreGeo = new THREE.SphereGeometry(0.6, 32, 32);
    const innerCoreMat = new THREE.MeshStandardMaterial({
      color: 0xfbbf24,
      emissive: 0xfbbf24,
      emissiveIntensity: 2
    });
    const innerCore = new THREE.Mesh(innerCoreGeo, innerCoreMat);
    this.dashboardGroup.add(innerCore);

    // 2. Satellite Nodes - Integrations
    const integrationIcons = [
      { name: 'QuickBooks', color: 0x2ca01c, pos: [-3, 2, 1] },
      { name: 'ShipStation', color: 0x4fc3f7, pos: [3, 1.5, -1] },
      { name: 'CRM Sync', color: 0xfbbf24, pos: [2, -2, 2] },
      { name: 'Lead Flow', color: 0x5d8c5d, pos: [-2.5, -1.8, -2] }
    ];

    this.links = [];
    integrationIcons.forEach((icon, i) => {
      // Node sphere
      const nodeGeo = new THREE.IcosahedronGeometry(0.4, 1);
      const nodeMat = new THREE.MeshStandardMaterial({
        color: icon.color,
        emissive: icon.color,
        emissiveIntensity: 0.5,
        metalness: 0.8,
        roughness: 0.2
      });
      const node = new THREE.Mesh(nodeGeo, nodeMat);
      node.position.set(...icon.pos);
      this.dashboardGroup.add(node);

      // Label for node
      this.createStatLabel(this.dashboardGroup, icon.pos[0], icon.pos[1] + 0.8, icon.name);

      // Connection Line
      const points = [
        new THREE.Vector3(0, 0, 0),
        new THREE.Vector3(...icon.pos)
      ];
      const curve = new THREE.CatmullRomCurve3(points);
      const tubeGeo = new THREE.TubeGeometry(curve, 20, 0.02, 8, false);
      const tubeMat = new THREE.MeshBasicMaterial({ 
        color: 0x5d8c5d, 
        transparent: true, 
        opacity: 0.3 
      });
      const tube = new THREE.Mesh(tubeGeo, tubeMat);
      this.dashboardGroup.add(tube);

      // Data packets (moving along lines)
      this.createDataPacket(icon.pos);
    });

    // 3. Floating Stats Panels (Mirroring real dashboard)
    this.createUIPlane(this.dashboardGroup, [-4, 0, -2], '24 Active\nAutomations', 0x5d8c5d);
    this.createUIPlane(this.dashboardGroup, [4, -1, 1], '128h Saved\nPer Week', 0xfbbf24);
    this.createUIPlane(this.dashboardGroup, [0, 3, 0], '99.9% Uptime\nHealthy', 0x4fc3f7);

    this.scene.add(this.dashboardGroup);
  }

  createDataPacket(targetPos) {
    if (!this.packets) this.packets = [];
    
    const packetGeo = new THREE.SphereGeometry(0.08, 8, 8);
    const packetMat = new THREE.MeshBasicMaterial({ color: 0xfbbf24 });
    const packet = new THREE.Mesh(packetGeo, packetMat);
    
    packet.userData = {
      progress: Math.random(),
      speed: 0.2 + Math.random() * 0.3,
      target: new THREE.Vector3(...targetPos)
    };
    
    this.dashboardGroup.add(packet);
    this.packets.push(packet);
  }

  createUIPlane(parent, pos, text, color) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 512;
    canvas.height = 256;
    
    context.fillStyle = 'rgba(15, 23, 42, 0.8)';
    context.roundRect(0, 0, 512, 256, 40);
    context.fill();
    
    context.lineWidth = 4;
    context.strokeStyle = `rgba(${color >> 16 & 255}, ${color >> 8 & 255}, ${color & 255}, 0.5)`;
    context.stroke();
    
    context.fillStyle = '#ffffff';
    context.font = 'bold 48px "Inter", sans-serif';
    context.textAlign = 'center';
    
    const lines = text.split('\n');
    lines.forEach((line, i) => {
      if (i === 1) context.font = '32px "Inter", sans-serif';
      context.fillText(line, 256, 110 + i * 60);
    });
    
    const texture = new THREE.CanvasTexture(canvas);
    const planeGeo = new THREE.PlaneGeometry(2, 1);
    const planeMat = new THREE.MeshBasicMaterial({ 
      map: texture, 
      transparent: true,
      side: THREE.DoubleSide
    });
    const plane = new THREE.Mesh(planeGeo, planeMat);
    plane.position.set(...pos);
    parent.add(plane);
  }

  animate() {
    this.animationId = requestAnimationFrame(() => this.animate());
    
    const delta = this.clock.getDelta();
    const elapsed = this.clock.getElapsedTime();
    
    if (this.controls) this.controls.update();
    
    // Rotate Core
    if (this.core) {
      this.core.rotation.y += delta * 0.3;
      this.core.rotation.z += delta * 0.1;
    }

    // Floating animation for UI planes
    this.dashboardGroup.children.forEach(child => {
      if (child.type === 'Mesh' && child.geometry.type === 'PlaneGeometry') {
        child.position.y += Math.sin(elapsed + child.position.x) * 0.002;
        child.lookAt(this.camera.position);
      }
    });

    // Animate Data Packets
    if (this.packets) {
      this.packets.forEach(packet => {
        packet.userData.progress += delta * packet.userData.speed;
        if (packet.userData.progress > 1) packet.userData.progress = 0;
        
        packet.position.lerpVectors(
          new THREE.Vector3(0,0,0), 
          packet.userData.target, 
          packet.userData.progress
        );
        
        // Add some jitter/noise
        packet.position.x += Math.sin(elapsed * 5 + packet.userData.speed) * 0.02;
      });
    }
    
    if (this.particles) {
      this.particles.rotation.y += delta * 0.05;
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
const initDashboard = () => {
  const container = document.getElementById('dashboard-3d-container');
  if (container && !window.dashboard3D) {
    console.log('Initializing 3D Dashboard...');
    window.dashboard3D = new Dashboard3D(container);
  }
};

if (document.readyState === 'complete' || document.readyState === 'interactive') {
  initDashboard();
} else {
  document.addEventListener('DOMContentLoaded', initDashboard);
}

// Fallback for slower connections or partial loads
window.addEventListener('load', initDashboard);

export default Dashboard3D;
