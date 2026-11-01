#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script para geração do projeto Three.js:
'Vidro com Refração, Aberração Cromática e Zoom Ultra-Suave'
"""

import os
from pathlib import Path

# Definição dos conteúdos de cada arquivo do projeto
FILES = {
    # -------------------------------------------------------------
    # 1. index.html
    # -------------------------------------------------------------
    "index.html": """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Three.js - Vidro com Refração & Aberração Cromática</title>
  <link rel="stylesheet" href="./css/style.css" />

  <!-- Import Map para resolução moderna de módulos Three.js e lil-gui via CDN -->
  <script type="importmap">
    {
      "imports": {
        "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
        "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/",
        "lil-gui": "https://unpkg.com/lil-gui@0.19.1/dist/lil-gui.esm.min.js"
      }
    }
  </script>
</head>
<body>
  <div id="canvas-container"></div>

  <!-- HUD informativo e elegante -->
  <header class="hud-overlay">
    <div class="hud-badge">Three.js Custom ShaderMaterial</div>
    <h1 class="hud-title">Vidro Refrativo & Aberração Cromática</h1>
    <p class="hud-desc">
      Renderização Multi-Pass com FBO, refração vetorial, RGB Split por canal de onda,
      Fresnel e realces especulares com zoom cinemático ultra-suave.
    </p>
    <div class="hud-instructions">
      <span>🖱️ <strong>Girar:</strong> Botão esquerdo</span>
      <span>🔍 <strong>Zoom Suave:</strong> Scroll / Trackpad</span>
      <span>🖐️ <strong>Pan:</strong> Botão direito</span>
      <span>⚙️ <strong>Controles:</strong> Menu lateral</span>
    </div>
  </header>

  <script type="module" src="./js/main.js"></script>
</body>
</html>
""",

    # -------------------------------------------------------------
    # 2. css/style.css
    # -------------------------------------------------------------
    "css/style.css": """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  height: 100%;
  overflow: hidden;
  background-color: #050508;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: #f1f5f9;
}

#canvas-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

/* Painel de HUD / UI */
.hud-overlay {
  position: absolute;
  top: 24px;
  left: 24px;
  z-index: 10;
  max-width: 440px;
  pointer-events: none;
  background: rgba(13, 17, 23, 0.65);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  padding: 20px 24px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: opacity 0.3s ease;
}

.hud-badge {
  display: inline-block;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.15);
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 9999px;
  margin-bottom: 10px;
}

.hud-title {
  font-size: 20px;
  font-weight: 700;
  line-height: 1.3;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hud-desc {
  font-size: 13px;
  line-height: 1.5;
  color: #94a3b8;
  margin-bottom: 14px;
}

.hud-instructions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  font-size: 11.5px;
  color: #cbd5e1;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding-top: 12px;
}

.hud-instructions span {
  display: flex;
  align-items: center;
  gap: 5px;
}

/* lil-gui custom styling */
.lil-gui {
  --background-color: rgba(13, 17, 23, 0.85) !important;
  --text-color: #f1f5f9 !important;
  --title-background-color: rgba(30, 41, 59, 0.9) !important;
  --widget-color: rgba(51, 65, 85, 0.8) !important;
  --hover-color: rgba(71, 85, 105, 0.9) !important;
  --focus-color: #38bdf8 !important;
  --number-color: #38bdf8 !important;
  --string-color: #a78bfa !important;
  font-family: inherit !important;
  border-radius: 12px !important;
  overflow: hidden !important;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6) !important;
  border: 1px solid rgba(255, 255, 255, 0.12) !important;
  backdrop-filter: blur(12px) !important;
  -webkit-backdrop-filter: blur(12px) !important;
  margin: 24px !important;
}

@media (max-width: 640px) {
  .hud-overlay {
    top: 12px;
    left: 12px;
    right: 12px;
    max-width: none;
    padding: 14px 16px;
  }
  .hud-title {
    font-size: 17px;
  }
  .hud-desc {
    display: none;
  }
}
""",

    # -------------------------------------------------------------
    # 3. js/shaders.js
    # -------------------------------------------------------------
    "js/shaders.js": """/**
 * Shaders GLSL para Vidro com Refração, Aberração Cromática, Fresnel e Especularidade.
 */

export const glassVertexShader = /* glsl */ `
  varying vec3 vWorldPosition;
  varying vec3 vWorldNormal;
  varying vec3 vViewNormal;
  varying vec3 vViewPosition;

  void main() {
    vec4 worldPos = modelMatrix * vec4(position, 1.0);
    vWorldPosition = worldPos.xyz;

    vWorldNormal = normalize(mat3(modelMatrix) * normal);
    vViewNormal = normalize(normalMatrix * normal);

    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
    vViewPosition = -mvPosition.xyz;

    gl_Position = projectionMatrix * mvPosition;
  }
`;

export const glassFragmentShader = /* glsl */ `
  precision highp float;

  uniform sampler2D uSceneTexture;
  uniform vec2 uResolution;
  uniform float uRefractPower;
  uniform float uChromaticAberration;
  uniform float uFresnelIntensity;
  uniform float uFresnelPower;
  uniform vec3 uFresnelColor;
  uniform vec3 uLightPos;
  uniform vec3 uSpecularColor;
  uniform float uShininess;

  varying vec3 vWorldPosition;
  varying vec3 vWorldNormal;
  varying vec3 vViewNormal;
  varying vec3 vViewPosition;

  void main() {
    // 1. Mapeamento exato de tela (1:1 com FBO e DPI)
    vec2 screenUV = gl_FragCoord.xy / uResolution.xy;

    vec3 normal = normalize(vWorldNormal);
    vec3 viewNormal = normalize(vViewNormal);
    vec3 viewDir = normalize(cameraPosition - vWorldPosition);

    // 2. Distorção refrativa projetada na tela
    vec2 distortion = viewNormal.xy * uRefractPower;

    // 3. Aberração Cromática (RGB Split)
    float rFactor = 1.0 + uChromaticAberration;
    float gFactor = 1.0;
    float bFactor = 1.0 - uChromaticAberration;

    vec2 uvR = clamp(screenUV - distortion * rFactor, vec2(0.001), vec2(0.999));
    vec2 uvG = clamp(screenUV - distortion * gFactor, vec2(0.001), vec2(0.999));
    vec2 uvB = clamp(screenUV - distortion * bFactor, vec2(0.001), vec2(0.999));

    float r = texture2D(uSceneTexture, uvR).r;
    float g = texture2D(uSceneTexture, uvG).g;
    float b = texture2D(uSceneTexture, uvB).b;
    vec3 refractedColor = vec3(r, g, b);

    // 4. Efeito Fresnel
    float cosTheta = clamp(dot(viewDir, normal), 0.0, 1.0);
    float fresnel = pow(1.0 - cosTheta, uFresnelPower) * uFresnelIntensity;

    // 5. Brilho Especular Blinn-Phong
    vec3 lightDir = normalize(uLightPos - vWorldPosition);
    vec3 halfVec = normalize(lightDir + viewDir);
    float NdotH = max(dot(normal, halfVec), 0.0);
    float specular = pow(NdotH, uShininess);

    float rimSpec = pow(max(dot(reflect(-lightDir, normal), -viewDir), 0.0), uShininess * 0.4) * 0.35;

    // 6. Composição
    vec3 finalColor = refractedColor;
    finalColor += fresnel * uFresnelColor;
    finalColor += (specular + rimSpec) * uSpecularColor;

    gl_FragColor = vec4(finalColor, 1.0);
  }
`;
""",

    # -------------------------------------------------------------
    # 4. js/scene.js
    # -------------------------------------------------------------
    "js/scene.js": """/**
 * Elementos de fundo vibrantes e de alto contraste gerados proceduralmente.
 */

import * as THREE from 'three';

function createProceduralGridTexture() {
  const size = 1024;
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');

  const grad = ctx.createLinearGradient(0, 0, size, size);
  grad.addColorStop(0, '#060814');
  grad.addColorStop(1, '#0f172a');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, size, size);

  const tileSize = 64;
  for (let y = 0; y < size; y += tileSize) {
    for (let x = 0; x < size; x += tileSize) {
      if (((x / tileSize) + (y / tileSize)) % 2 === 0) {
        ctx.fillStyle = 'rgba(30, 41, 59, 0.7)';
        ctx.fillRect(x, y, tileSize, tileSize);
      }
    }
  }

  ctx.strokeStyle = 'rgba(6, 182, 212, 0.45)';
  ctx.lineWidth = 2;
  for (let i = 0; i <= size; i += 64) {
    ctx.beginPath();
    ctx.moveTo(i, 0); ctx.lineTo(i, size);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(0, i); ctx.lineTo(size, i);
    ctx.stroke();
  }

  ctx.strokeStyle = 'rgba(244, 63, 94, 0.7)';
  ctx.lineWidth = 5;
  for (let r = 70; r <= 480; r += 90) {
    ctx.beginPath();
    ctx.arc(size / 2, size / 2, r, 0, Math.PI * 2);
    ctx.stroke();
  }

  ctx.strokeStyle = 'rgba(234, 179, 8, 0.4)';
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(0, 0); ctx.lineTo(size, size);
  ctx.moveTo(size, 0); ctx.lineTo(0, size);
  ctx.stroke();

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(1.5, 1.5);
  return texture;
}

export function setupBackground(scene) {
  const animatedObjects = [];

  const bgTexture = createProceduralGridTexture();
  const bgPlaneGeo = new THREE.PlaneGeometry(32, 22);
  const bgPlaneMat = new THREE.MeshBasicMaterial({ map: bgTexture });
  const bgPlane = new THREE.Mesh(bgPlaneGeo, bgPlaneMat);
  bgPlane.position.set(0, 0, -5.5);
  scene.add(bgPlane);

  const geometries = [
    new THREE.BoxGeometry(0.85, 0.85, 0.85),
    new THREE.SphereGeometry(0.55, 32, 32),
    new THREE.IcosahedronGeometry(0.65, 0),
    new THREE.TorusGeometry(0.55, 0.22, 16, 40),
    new THREE.OctahedronGeometry(0.65, 0),
    new THREE.ConeGeometry(0.55, 1.1, 32),
  ];

  const colors = [
    0x00f0ff,
    0xff0055,
    0x39ff14,
    0xffbe0b,
    0x8338ec,
    0xfb5607,
  ];

  const count = 14;
  for (let i = 0; i < count; i++) {
    const geo = geometries[i % geometries.length];
    const color = colors[i % colors.length];

    const mat = new THREE.MeshStandardMaterial({
      color: color,
      roughness: 0.2,
      metalness: 0.8,
      emissive: color,
      emissiveIntensity: 0.35,
    });

    const mesh = new THREE.Mesh(geo, mat);

    const angle = (i / count) * Math.PI * 2;
    const radius = 2.4 + (i % 3) * 0.7;
    mesh.position.set(
      Math.cos(angle) * radius,
      Math.sin(angle) * radius,
      -2.0 - (i % 4) * 0.7
    );

    mesh.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);
    scene.add(mesh);

    animatedObjects.push({
      mesh,
      baseRadius: radius,
      baseAngle: angle,
      speed: 0.35 + (i % 4) * 0.15,
      rotSpeedX: 0.015 * ((i % 2 === 0) ? 1 : -1),
      rotSpeedY: 0.02 * ((i % 3 === 0) ? 1 : -1),
      bobFreq: 1.5 + (i % 3),
      bobAmp: 0.25,
      zBase: mesh.position.z,
    });
  }

  const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
  scene.add(ambientLight);

  const mainLight = new THREE.DirectionalLight(0xffffff, 2.0);
  mainLight.position.set(6, 8, 7);
  scene.add(mainLight);

  const fillLight = new THREE.DirectionalLight(0x38bdf8, 1.2);
  fillLight.position.set(-6, -4, 4);
  scene.add(fillLight);

  const coloredPointLight = new THREE.PointLight(0xff007f, 3.0, 15);
  coloredPointLight.position.set(0, 0, 1.5);
  scene.add(coloredPointLight);

  return {
    animatedObjects,
    coloredPointLight,
    update: (time, speedMultiplier = 1.0) => {
      animatedObjects.forEach((item) => {
        const curAngle = item.baseAngle + time * item.speed * speedMultiplier;
        item.mesh.position.x = Math.cos(curAngle) * item.baseRadius;
        item.mesh.position.y = Math.sin(curAngle) * item.baseRadius + Math.sin(time * item.bobFreq) * item.bobAmp;
        item.mesh.rotation.x += item.rotSpeedX * speedMultiplier;
        item.mesh.rotation.y += item.rotSpeedY * speedMultiplier;
      });

      coloredPointLight.position.x = Math.sin(time * 0.8) * 3.0;
      coloredPointLight.position.y = Math.cos(time * 0.6) * 2.5;
    }
  };
}
""",

    # -------------------------------------------------------------
    # 5. js/main.js (Com Sistema de Zoom Suave / Damped Lerp)
    # -------------------------------------------------------------
    "js/main.js": """/**
 * Main Entry Point:
 * Pipeline Multi-Pass FBO com Shader de Vidro, DPI seguro,
 * e controle de Zoom Suave interpolado (sem saltos bruscos).
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import GUI from 'lil-gui';
import { glassVertexShader, glassFragmentShader } from './shaders.js';
import { setupBackground } from './scene.js';

// --- Parâmetros de Controle (GUI) ---
const PARAMS = {
  refractPower: 0.12,
  chromaticAberration: 0.035,
  fresnelIntensity: 1.1,
  fresnelPower: 3.0,
  fresnelColor: '#a5f3fc',
  specularColor: '#ffffff',
  shininess: 48.0,
  geometry: 'Torus Knot',
  autoRotate: true,
  rotationSpeed: 1.0,
  bgSpeed: 1.0,
  zoomSmoothness: 0.08, // Fator de amortecimento da interpolação do zoom
};

// --- Inicialização Básica ---
const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x060814);

const camera = new THREE.PerspectiveCamera(
  45,
  window.innerWidth / window.innerHeight,
  0.1,
  100
);
camera.position.set(0, 0, 4.6);

// --- Renderizador com Prevenção de Bugs DPI/Retina ---
const pixelRatio = Math.min(window.devicePixelRatio || 1, 2);

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(pixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
container.appendChild(renderer.domElement);

// --- OrbitControls ---
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.enableZoom = false; // Desabilitamos o zoom nativo brusco para assumir o controle interpolado

// --- SISTEMA DE ZOOM SUAVE (SMOOTH DAMPED ZOOM) ---
const MIN_DISTANCE = 1.8;
const MAX_DISTANCE = 8.5;
let targetDistance = camera.position.distanceTo(controls.target);
let currentDistance = targetDistance;

// 1. Escuta do evento de scroll do mouse / trackpad com prevenção de salto
window.addEventListener('wheel', (e) => {
  e.preventDefault();

  // Tratamento universal de delta (Windows, macOS, trackpads, mouses de clique)
  let delta = e.deltaY;
  if (e.deltaMode === 1) delta *= 16;       // Linhas (Firefox)
  else if (e.deltaMode === 2) delta *= 100; // Páginas

  // Limita o impulso máximo para evitar que scrolls rápidos gerem saltos instantâneos
  const clampedDelta = Math.sign(delta) * Math.min(Math.abs(delta), 120);

  // Escalonamento proporcional à distância (zoom uniforme tanto próximo quanto distante)
  const zoomStep = (clampedDelta / 100.0) * 0.065 * targetDistance;
  targetDistance = THREE.MathUtils.clamp(targetDistance + zoomStep, MIN_DISTANCE, MAX_DISTANCE);
}, { passive: false });

// 2. Suporte para gesto de pinça em telas touch / mobile
let touchStartDist = 0;
let touchStartTargetDist = targetDistance;

window.addEventListener('touchstart', (e) => {
  if (e.touches.length === 2) {
    const dx = e.touches[0].pageX - e.touches[1].pageX;
    const dy = e.touches[0].pageY - e.touches[1].pageY;
    touchStartDist = Math.hypot(dx, dy);
    touchStartTargetDist = targetDistance;
  }
}, { passive: true });

window.addEventListener('touchmove', (e) => {
  if (e.touches.length === 2 && touchStartDist > 0) {
    const dx = e.touches[0].pageX - e.touches[1].pageX;
    const dy = e.touches[0].pageY - e.touches[1].pageY;
    const dist = Math.hypot(dx, dy);
    const factor = touchStartDist / dist;
    targetDistance = THREE.MathUtils.clamp(touchStartTargetDist * factor, MIN_DISTANCE, MAX_DISTANCE);
  }
}, { passive: true });

window.addEventListener('touchend', (e) => {
  if (e.touches.length < 2) {
    touchStartDist = 0;
  }
}, { passive: true });

// --- WebGLRenderTarget (FBO Multi-Pass) dimensionado na resolução nativa exata do buffer ---
let fboWidth = Math.floor(window.innerWidth * pixelRatio);
let fboHeight = Math.floor(window.innerHeight * pixelRatio);

const renderTarget = new THREE.WebGLRenderTarget(fboWidth, fboHeight, {
  minFilter: THREE.LinearFilter,
  magFilter: THREE.LinearFilter,
  format: THREE.RGBAFormat,
  type: THREE.HalfFloatType,
});

// --- Configuração dos Elementos de Fundo ---
const bgController = setupBackground(scene);

// --- ShaderMaterial de Vidro ---
const glassUniforms = {
  uSceneTexture: { value: renderTarget.texture },
  uResolution: { value: new THREE.Vector2(fboWidth, fboHeight) },
  uRefractPower: { value: PARAMS.refractPower },
  uChromaticAberration: { value: PARAMS.chromaticAberration },
  uFresnelIntensity: { value: PARAMS.fresnelIntensity },
  uFresnelPower: { value: PARAMS.fresnelPower },
  uFresnelColor: { value: new THREE.Color(PARAMS.fresnelColor) },
  uLightPos: { value: new THREE.Vector3(5.0, 5.0, 5.0) },
  uSpecularColor: { value: new THREE.Color(PARAMS.specularColor) },
  uShininess: { value: PARAMS.shininess }
};

const glassMaterial = new THREE.ShaderMaterial({
  vertexShader: glassVertexShader,
  fragmentShader: glassFragmentShader,
  uniforms: glassUniforms,
  side: THREE.DoubleSide,
  transparent: false,
});

// --- Criação da Geometria Principal ---
function buildGeometry(type) {
  switch (type) {
    case 'Torus Knot':
      return new THREE.TorusKnotGeometry(1.0, 0.35, 180, 56);
    case 'Esfera':
      return new THREE.SphereGeometry(1.3, 64, 64);
    case 'Icosaedro':
      return new THREE.IcosahedronGeometry(1.35, 3);
    case 'Toro':
      return new THREE.TorusGeometry(1.15, 0.45, 48, 120);
    case 'Octaedro':
      return new THREE.OctahedronGeometry(1.4, 1);
    default:
      return new THREE.TorusKnotGeometry(1.0, 0.35, 180, 56);
  }
}

const glassMesh = new THREE.Mesh(buildGeometry(PARAMS.geometry), glassMaterial);
scene.add(glassMesh);

// --- Listener de Resize com Redimensionamento FBO e Uniform uResolution (DPI Seguro) ---
window.addEventListener('resize', () => {
  const width = window.innerWidth;
  const height = window.innerHeight;
  const pr = Math.min(window.devicePixelRatio || 1, 2);

  camera.aspect = width / height;
  camera.updateProjectionMatrix();

  renderer.setPixelRatio(pr);
  renderer.setSize(width, height);

  fboWidth = Math.floor(width * pr);
  fboHeight = Math.floor(height * pr);

  renderTarget.setSize(fboWidth, fboHeight);
  glassMaterial.uniforms.uResolution.value.set(fboWidth, fboHeight);
});

// --- Painel lil-gui Interativo ---
const gui = new GUI({ title: 'Configurações do Vidro' });

const fOptics = gui.addFolder('Óptica & Aberração');
fOptics.add(PARAMS, 'refractPower', 0.0, 0.35, 0.005)
  .name('Poder de Refração')
  .onChange(v => { glassMaterial.uniforms.uRefractPower.value = v; });

fOptics.add(PARAMS, 'chromaticAberration', 0.0, 0.1, 0.002)
  .name('RGB Split (Dispersão)')
  .onChange(v => { glassMaterial.uniforms.uChromaticAberration.value = v; });

const fSurface = gui.addFolder('Superfície & Reflexos');
fSurface.add(PARAMS, 'fresnelIntensity', 0.0, 3.0, 0.1)
  .name('Intensidade Fresnel')
  .onChange(v => { glassMaterial.uniforms.uFresnelIntensity.value = v; });

fSurface.add(PARAMS, 'fresnelPower', 1.0, 6.0, 0.1)
  .name('Exponente Fresnel')
  .onChange(v => { glassMaterial.uniforms.uFresnelPower.value = v; });

fSurface.addColor(PARAMS, 'fresnelColor')
  .name('Cor Fresnel')
  .onChange(v => { glassMaterial.uniforms.uFresnelColor.value.set(v); });

fSurface.add(PARAMS, 'shininess', 8.0, 128.0, 2.0)
  .name('Especularidade')
  .onChange(v => { glassMaterial.uniforms.uShininess.value = v; });

const fScene = gui.addFolder('Cena & Interação');
fScene.add(PARAMS, 'geometry', ['Torus Knot', 'Esfera', 'Icosaedro', 'Toro', 'Octaedro'])
  .name('Forma do Vidro')
  .onChange(type => {
    glassMesh.geometry.dispose();
    glassMesh.geometry = buildGeometry(type);
  });

fScene.add(PARAMS, 'zoomSmoothness', 0.02, 0.20, 0.01).name('Suavidade do Zoom');
fScene.add(PARAMS, 'autoRotate').name('Girar Objeto');
fScene.add(PARAMS, 'rotationSpeed', 0.1, 3.0, 0.1).name('Vel. Rotação');
fScene.add(PARAMS, 'bgSpeed', 0.0, 3.0, 0.1).name('Vel. Fundo');

fOptics.open();
fSurface.open();

// --- Loop de Renderização Multi-Pass ---
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);

  const delta = clock.getDelta();
  const elapsedTime = clock.getElapsedTime();

  // 1. Atualizar animações de fundo e luzes
  bgController.update(elapsedTime, PARAMS.bgSpeed);

  // 2. Rotação suave do objeto de vidro
  if (PARAMS.autoRotate) {
    glassMesh.rotation.x += 0.006 * PARAMS.rotationSpeed;
    glassMesh.rotation.y += 0.010 * PARAMS.rotationSpeed;
  }

  // 3. Aplicação do Zoom Suave contínuo (Lerp exponencial)
  currentDistance = THREE.MathUtils.lerp(currentDistance, targetDistance, PARAMS.zoomSmoothness);

  const camOffset = new THREE.Vector3().subVectors(camera.position, controls.target);
  if (camOffset.lengthSq() > 0.0001) {
    camOffset.normalize().multiplyScalar(currentDistance);
    camera.position.copy(controls.target).add(camOffset);
  }

  controls.update();

  // 4. Atualizar posição da luz especular com base na luz pontual da cena
  glassMaterial.uniforms.uLightPos.value.copy(bgController.coloredPointLight.position);

  // ==========================================================
  // PASSO 1 DO FBO: Renderizar a cena de fundo no RenderTarget
  // ==========================================================
  glassMesh.visible = false;
  renderer.setRenderTarget(renderTarget);
  renderer.render(scene, camera);

  // ==========================================================
  // PASSO 2: Renderizar a cena final no Canvas
  // ==========================================================
  renderer.setRenderTarget(null);
  glassMesh.visible = true;
  renderer.render(scene, camera);
}

// Início do Loop
animate();
"""
}

def main():
    print("=" * 70)
    print("  Atualizando: Three.js Glass Shader (Com Zoom Ultra-Suave)")
    print("=" * 70)

    base_dir = Path(".")

    for rel_path, content in FILES.items():
        file_path = base_dir / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f" [✔] Arquivo atualizado: {file_path}")

    print("\n" + "=" * 70)
    print("  ATUALIZAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 70)
    print("  Como rodar o projeto:")
    print("  1. No terminal, inicie o servidor:")
    print("       python -m http.server 3000")
    print("  2. Abra no navegador:")
    print("       http://localhost:3000")
    print("=" * 70)

if __name__ == "__main__":
    main()