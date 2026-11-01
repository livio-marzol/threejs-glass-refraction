#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script para atualização do Three.js Shader Playground:
Correção de compilação GLSL no Vertex Shader do 'Mercúrio Líquido Cromado'.
"""

import os
from pathlib import Path

FILES = {
    # -------------------------------------------------------------
    # 1. index.html
    # -------------------------------------------------------------
    "index.html": """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Three.js - Shader Playground (Vidro, Iridescência & Mercúrio Líquido)</title>
  <link rel="stylesheet" href="./css/style.css" />

  <!-- Import Map para Three.js e lil-gui via CDN -->
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
    <div class="hud-badge">Shader Playground • GLSL</div>
    <h1 class="hud-title">Vidro, Iridescência & Mercúrio Líquido</h1>
    <p class="hud-desc">
      Alterne entre 3 shaders avançados: refração de vidro com RGB Split,
      interferência de bolha de sabão e mercúrio líquido cromado com deformação de vértices.
    </p>
    <div class="hud-instructions">
      <span>🖱️ <strong>Girar:</strong> Botão esquerdo</span>
      <span>🔍 <strong>Zoom Suave:</strong> Scroll / Trackpad</span>
      <span>🖐️ <strong>Pan:</strong> Botão direito</span>
      <span>⚙️ <strong>Shaders:</strong> Menu lateral</span>
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
  --background-color: rgba(13, 17, 23, 0.88) !important;
  --text-color: #f1f5f9 !important;
  --title-background-color: rgba(30, 41, 59, 0.95) !important;
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
    # 3. js/shaders.js (Com correção no Simplex 3D Noise)
    # -------------------------------------------------------------
    "js/shaders.js": """/**
 * Repositório de Shaders GLSL:
 * 1. Vidro Refrativo (RGB Split)
 * 2. Película Iridescente (Thin-Film)
 * 3. Mercúrio Líquido Cromado (Vertex Displacement + Simplex 3D Noise)
 */

// =================================================================
// SHADER 1: VIDRO REFRATIVO (RGB SPLIT)
// =================================================================

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
    vec2 screenUV = gl_FragCoord.xy / uResolution.xy;

    vec3 normal = normalize(vWorldNormal);
    vec3 viewNormal = normalize(vViewNormal);
    vec3 viewDir = normalize(cameraPosition - vWorldPosition);

    vec2 distortion = viewNormal.xy * uRefractPower;

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

    float cosTheta = clamp(dot(viewDir, normal), 0.0, 1.0);
    float fresnel = pow(1.0 - cosTheta, uFresnelPower) * uFresnelIntensity;

    vec3 lightDir = normalize(uLightPos - vWorldPosition);
    vec3 halfVec = normalize(lightDir + viewDir);
    float NdotH = max(dot(normal, halfVec), 0.0);
    float specular = pow(NdotH, uShininess);

    float rimSpec = pow(max(dot(reflect(-lightDir, normal), -viewDir), 0.0), uShininess * 0.4) * 0.35;

    vec3 finalColor = refractedColor;
    finalColor += fresnel * uFresnelColor;
    finalColor += (specular + rimSpec) * uSpecularColor;

    gl_FragColor = vec4(finalColor, 1.0);
  }
`;

// =================================================================
// SHADER 2: PELÍCULA IRIDESCENTE / BOLHA DE SABÃO (THIN-FILM)
// =================================================================

export const iridescentVertexShader = /* glsl */ `
  varying vec3 vWorldPosition;
  varying vec3 vWorldNormal;
  varying vec3 vViewNormal;

  void main() {
    vec4 worldPos = modelMatrix * vec4(position, 1.0);
    vWorldPosition = worldPos.xyz;
    vWorldNormal = normalize(mat3(modelMatrix) * normal);
    vViewNormal = normalize(normalMatrix * normal);

    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

export const iridescentFragmentShader = /* glsl */ `
  precision highp float;

  uniform sampler2D uSceneTexture;
  uniform vec2 uResolution;
  uniform float uTime;
  uniform float uRefractPower;
  uniform float uFrequency;
  uniform float uNoiseScale;
  uniform float uIridescenceIntensity;
  uniform float uTransparency;
  uniform float uFresnelPower;
  uniform vec3 uLightPos;
  uniform vec3 uSpecularColor;
  uniform float uShininess;

  varying vec3 vWorldPosition;
  varying vec3 vWorldNormal;
  varying vec3 vViewNormal;

  vec3 spectralColor(float t) {
    vec3 a = vec3(0.5, 0.5, 0.5);
    vec3 b = vec3(0.5, 0.5, 0.5);
    vec3 c = vec3(1.0, 1.0, 1.0);
    vec3 d = vec3(0.00, 0.33, 0.67);
    return a + b * cos(6.28318 * (c * t + d));
  }

  void main() {
    vec2 screenUV = gl_FragCoord.xy / uResolution.xy;

    vec3 normal = normalize(vWorldNormal);
    vec3 viewNormal = normalize(vViewNormal);
    vec3 viewDir = normalize(cameraPosition - vWorldPosition);

    vec2 distortion = viewNormal.xy * uRefractPower;
    vec3 bgColor = texture2D(uSceneTexture, clamp(screenUV - distortion, vec2(0.001), vec2(0.999))).rgb;

    float cosTheta = clamp(dot(viewDir, normal), 0.0, 1.0);
    float fresnel = pow(1.0 - cosTheta, uFresnelPower);

    float wave = sin(vWorldPosition.x * 2.4 + uTime * 0.7) * cos(vWorldPosition.y * 2.4 + vWorldPosition.z * 1.6 + uTime * 0.5);
    float filmCoord = (1.0 - cosTheta) * uFrequency + wave * uNoiseScale;
    vec3 iridColor = spectralColor(filmCoord);

    vec3 lightDir = normalize(uLightPos - vWorldPosition);
    vec3 halfVec = normalize(lightDir + viewDir);
    float NdotH = max(dot(normal, halfVec), 0.0);
    float specular = pow(NdotH, uShininess);

    float rimSpec = pow(max(dot(reflect(-lightDir, normal), -viewDir), 0.0), uShininess * 0.35) * 0.6;

    float filmWeight = clamp(fresnel * uIridescenceIntensity + (1.0 - uTransparency), 0.0, 1.0);
    vec3 finalColor = mix(bgColor, iridColor, filmWeight);

    finalColor += (specular * uSpecularColor) + (rimSpec * iridColor * 0.75);

    gl_FragColor = vec4(finalColor, 1.0);
  }
`;

// =================================================================
// SHADER 3: MERCÚRIO LÍQUIDO CROMADO (CORRIGIDO)
// =================================================================

export const liquidVertexShader = /* glsl */ `
  uniform float uTime;
  uniform float uWaveSpeed;
  uniform float uDisplacementScale;
  uniform float uNoiseFrequency;

  varying vec3 vWorldPosition;
  varying vec3 vWorldNormal;
  varying vec3 vViewNormal;
  varying vec3 vViewPosition;
  varying float vDisplacement;

  // Implementação correta e canônica de Simplex 3D Noise (Stefan Gustavson)
  vec4 permute(vec4 x){ return mod(((x * 34.0) + 1.0) * x, 289.0); }
  vec4 taylorInvSqrt(vec4 r){ return 1.79284291400159 - 0.85373472095314 * r; }

  float snoise(vec3 v){
    const vec2 C = vec2(1.0 / 6.0, 1.0 / 3.0);
    const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);

    vec3 i  = floor(v + dot(v, C.yyy));
    vec3 x0 = v - i + dot(i, C.xxx);

    vec3 g = step(x0.yzx, x0.xyz);
    vec3 l = 1.0 - g;
    vec3 i1 = min(g.xyz, l.zxy);
    vec3 i2 = max(g.xyz, l.zxy);

    vec3 x1 = x0 - i1 + 1.0 * C.xxx;
    vec3 x2 = x0 - i2 + 2.0 * C.xxx;
    vec3 x3 = x0 - 1.0 + 3.0 * C.xxx;

    i = mod(i, 289.0);
    vec4 p = permute(permute(permute(
              i.z + vec4(0.0, i1.z, i2.z, 1.0))
            + i.y + vec4(0.0, i1.y, i2.y, 1.0))
            + i.x + vec4(0.0, i1.x, i2.x, 1.0));

    float n_ = 0.142857142857; // 1.0 / 7.0
    vec3 ns = n_ * D.wyz - D.xzx;

    // Correção: multiplicação escalar correta para mod(p, 49)
    vec4 j = p - 49.0 * floor(p * ns.z * ns.z);

    vec4 x_ = floor(j * ns.z);
    vec4 y_ = floor(j - 7.0 * x_);

    vec4 x = x_ * ns.x + ns.yyyy;
    vec4 y = y_ * ns.x + ns.yyyy;
    vec4 h = 1.0 - abs(x) - abs(y);

    vec4 b0 = vec4(x.xy, y.xy);
    vec4 b1 = vec4(x.zw, y.zw);

    vec4 s0 = floor(b0) * 2.0 + 1.0;
    vec4 s1 = floor(b1) * 2.0 + 1.0;
    vec4 sh = -step(h, vec4(0.0));

    vec4 a0 = b0.xzyw + s0.xzyw * sh.xxyy;
    vec4 a1 = b1.xzyw + s1.xzyw * sh.zzww;

    vec3 p0 = vec3(a0.xy, h.x);
    vec3 p1 = vec3(a0.zw, h.y);
    vec3 p2 = vec3(a1.xy, h.z);
    vec3 p3 = vec3(a1.zw, h.w);

    vec4 norm = taylorInvSqrt(vec4(dot(p0, p0), dot(p1, p1), dot(p2, p2), dot(p3, p3)));
    p0 *= norm.x; p1 *= norm.y; p2 *= norm.z; p3 *= norm.w;

    vec4 m = max(0.6 - vec4(dot(x0, x0), dot(x1, x1), dot(x2, x2), dot(x3, x3)), 0.0);
    m = m * m;
    return 42.0 * dot(m * m, vec4(dot(p0, x0), dot(p1, x1), dot(p2, x2), dot(p3, x3)));
  }

  // Deformação harmônica orgânica de metal líquido
  float getDisplacement(vec3 p) {
    float t = uTime * uWaveSpeed;
    float n1 = snoise(p * uNoiseFrequency + vec3(0.0, 0.0, t * 0.5));
    float n2 = snoise(p * uNoiseFrequency * 2.2 - vec3(t * 0.6, t * 0.4, 0.0)) * 0.45;
    float n3 = snoise(p * uNoiseFrequency * 4.0 + vec3(0.0, t * 0.7, t * 0.3)) * 0.15;
    return (n1 + n2 + n3) * uDisplacementScale;
  }

  void main() {
    float disp = getDisplacement(position);
    vDisplacement = disp;
    vec3 displacedPos = position + normal * disp;

    // Recálculo suave das normais por diferenças finitas em espaço tangente
    float eps = 0.02;
    vec3 tangent = normalize(abs(normal.y) < 0.99 ? cross(normal, vec3(0.0, 1.0, 0.0)) : cross(normal, vec3(0.0, 0.0, 1.0)));
    vec3 bitangent = cross(normal, tangent);

    vec3 p0 = position + normal * disp;
    vec3 p1 = position + tangent * eps + normal * getDisplacement(position + tangent * eps);
    vec3 p2 = position + bitangent * eps + normal * getDisplacement(position + bitangent * eps);

    vec3 recalculatedNormal = normalize(cross(p1 - p0, p2 - p0));

    vec4 worldPos = modelMatrix * vec4(displacedPos, 1.0);
    vWorldPosition = worldPos.xyz;
    vWorldNormal = normalize(mat3(modelMatrix) * recalculatedNormal);
    vViewNormal = normalize(normalMatrix * recalculatedNormal);

    vec4 mvPosition = modelViewMatrix * vec4(displacedPos, 1.0);
    vViewPosition = -mvPosition.xyz;
    gl_Position = projectionMatrix * mvPosition;
  }
`;

export const liquidFragmentShader = /* glsl */ `
  precision highp float;

  uniform sampler2D uSceneTexture;
  uniform vec2 uResolution;
  uniform vec3 uMetalColor;
  uniform float uReflectionIntensity;
  uniform float uFresnelPower;
  uniform float uRoughness;
  uniform vec3 uLightPos;
  uniform vec3 uSpecularColor;

  varying vec3 vWorldPosition;
  varying vec3 vWorldNormal;
  varying vec3 vViewNormal;
  varying vec3 vViewPosition;
  varying float vDisplacement;

  // Ambiente de estúdio cromado procedural (horizonte nítido de metal espelhado)
  vec3 getChromeEnvironment(vec3 rayDir) {
    float y = rayDir.y;
    vec3 skyColor = vec3(0.90, 0.95, 1.0);
    vec3 groundColor = vec3(0.08, 0.10, 0.15);
    vec3 horizonGlow = vec3(0.4, 0.75, 1.0);

    float horizon = smoothstep(-0.06, 0.06, y);
    float horizonBand = exp(-abs(y) * 14.0);

    vec3 env = mix(groundColor, skyColor, horizon);
    env += horizonBand * horizonGlow * 1.3;

    // Faixa neon sutil para adicionar dinamismo de estúdio 3D
    float neonStrip = pow(max(dot(rayDir, normalize(vec3(0.8, 0.35, -0.5))), 0.0), 16.0);
    env += neonStrip * vec3(1.0, 0.25, 0.65) * 1.6;

    return env;
  }

  void main() {
    vec3 normal = normalize(vWorldNormal);
    vec3 viewDir = normalize(cameraPosition - vWorldPosition);
    vec3 viewNormal = normalize(vViewNormal);

    // 1. Vetor de reflexão no espaço do mundo
    vec3 reflectDir = reflect(-viewDir, normal);

    // 2. Reflexo do ambiente cromado
    vec3 chromeEnv = getChromeEnvironment(reflectDir);

    // 3. Reflexo da cena de fundo (espelhando os objetos coloridos do FBO)
    vec2 screenUV = gl_FragCoord.xy / uResolution.xy;
    vec2 reflectUV = screenUV + viewNormal.xy * 0.22;
    vec3 sceneReflection = texture2D(uSceneTexture, clamp(reflectUV, vec2(0.001), vec2(0.999))).rgb;

    // 4. Efeito Fresnel condutor para metais (Schlick aproximado para cromo/mercúrio)
    float cosTheta = clamp(dot(viewDir, normal), 0.0, 1.0);
    float fresnel = 0.68 + 0.32 * pow(1.0 - cosTheta, uFresnelPower);

    // 5. Brilho Especular Blinn-Phong nítido
    vec3 lightDir = normalize(uLightPos - vWorldPosition);
    vec3 halfVec = normalize(lightDir + viewDir);
    float NdotH = max(dot(normal, halfVec), 0.0);
    float shininess = mix(128.0, 16.0, uRoughness);
    float specular = pow(NdotH, shininess) * 1.6;
    float secondarySpec = pow(NdotH, 20.0) * 0.45;

    // 6. Fusão Metálica
    vec3 combinedReflection = mix(chromeEnv, sceneReflection, 0.4) * uReflectionIntensity;
    vec3 finalColor = uMetalColor * combinedReflection * fresnel;

    // Adiciona realces especulares
    finalColor += (specular + secondarySpec) * uSpecularColor;

    // Micro-sombreamento nas dobras das ondas de mercúrio
    float waveContrast = smoothstep(-0.25, 0.25, vDisplacement);
    finalColor *= mix(0.86, 1.08, waveContrast);

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
    # 5. js/main.js
    # -------------------------------------------------------------
    "js/main.js": """/**
 * Main Entry Point: Shader Playground
 * Gerencia 3 Custom ShaderMaterials:
 * 1. Vidro Refrativo (RGB Split)
 * 2. Película Iridescente (Thin-Film)
 * 3. Mercúrio Líquido (Vertex Displacement + Simplex 3D Noise)
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import GUI from 'lil-gui';
import {
  glassVertexShader,
  glassFragmentShader,
  iridescentVertexShader,
  iridescentFragmentShader,
  liquidVertexShader,
  liquidFragmentShader
} from './shaders.js';
import { setupBackground } from './scene.js';

// --- Parâmetros de Estado e Interface ---
const PARAMS = {
  activeShader: 'Mercúrio Líquido (Cromado)',

  // Parâmetros do Vidro Refrativo
  glassRefractPower: 0.12,
  glassAberration: 0.035,
  glassFresnelIntensity: 1.1,
  glassFresnelPower: 3.0,
  glassFresnelColor: '#a5f3fc',
  glassShininess: 48.0,

  // Parâmetros da Película Iridescente
  iridFrequency: 2.2,
  iridNoiseScale: 0.45,
  iridIntensity: 1.3,
  iridTransparency: 0.85,
  iridRefractPower: 0.08,
  iridFresnelPower: 2.2,
  iridShininess: 64.0,

  // Parâmetros do Mercúrio Líquido Cromado
  liquidWaveSpeed: 1.0,
  liquidDisplacement: 0.16,
  liquidFrequency: 0.85,
  liquidReflection: 1.4,
  liquidRoughness: 0.04,
  liquidFresnelPower: 2.5,
  liquidColor: '#e2e8f0',

  // Configurações Gerais
  geometry: 'Torus Knot',
  autoRotate: true,
  rotationSpeed: 1.0,
  bgSpeed: 1.0,
  zoomSmoothness: 0.08,
};

// --- Inicialização da Cena e Câmera ---
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

// --- Renderizador com Tratamento Retina / DPI ---
const pixelRatio = Math.min(window.devicePixelRatio || 1, 2);

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(pixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
container.appendChild(renderer.domElement);

// --- OrbitControls com Zoom Desacoplado ---
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.enableZoom = false;

// --- Sistema de Zoom Suave (Damped Lerp) ---
const MIN_DISTANCE = 1.8;
const MAX_DISTANCE = 8.5;
let targetDistance = camera.position.distanceTo(controls.target);
let currentDistance = targetDistance;

window.addEventListener('wheel', (e) => {
  e.preventDefault();
  let delta = e.deltaY;
  if (e.deltaMode === 1) delta *= 16;
  else if (e.deltaMode === 2) delta *= 100;

  const clampedDelta = Math.sign(delta) * Math.min(Math.abs(delta), 120);
  const zoomStep = (clampedDelta / 100.0) * 0.065 * targetDistance;
  targetDistance = THREE.MathUtils.clamp(targetDistance + zoomStep, MIN_DISTANCE, MAX_DISTANCE);
}, { passive: false });

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
  if (e.touches.length < 2) touchStartDist = 0;
}, { passive: true });

// --- WebGLRenderTarget (FBO Multi-Pass) dimensionado com DPI ---
let fboWidth = Math.floor(window.innerWidth * pixelRatio);
let fboHeight = Math.floor(window.innerHeight * pixelRatio);

const renderTarget = new THREE.WebGLRenderTarget(fboWidth, fboHeight, {
  minFilter: THREE.LinearFilter,
  magFilter: THREE.LinearFilter,
  format: THREE.RGBAFormat,
  type: THREE.HalfFloatType,
});

// --- Fundo Procedural ---
const bgController = setupBackground(scene);

// --- Material 1: Vidro Refrativo ---
const glassMaterial = new THREE.ShaderMaterial({
  vertexShader: glassVertexShader,
  fragmentShader: glassFragmentShader,
  uniforms: {
    uSceneTexture: { value: renderTarget.texture },
    uResolution: { value: new THREE.Vector2(fboWidth, fboHeight) },
    uRefractPower: { value: PARAMS.glassRefractPower },
    uChromaticAberration: { value: PARAMS.glassAberration },
    uFresnelIntensity: { value: PARAMS.glassFresnelIntensity },
    uFresnelPower: { value: PARAMS.glassFresnelPower },
    uFresnelColor: { value: new THREE.Color(PARAMS.glassFresnelColor) },
    uLightPos: { value: new THREE.Vector3(5.0, 5.0, 5.0) },
    uSpecularColor: { value: new THREE.Color(0xffffff) },
    uShininess: { value: PARAMS.glassShininess }
  },
  side: THREE.DoubleSide,
  transparent: false,
});

// --- Material 2: Película Iridescente ---
const iridescentMaterial = new THREE.ShaderMaterial({
  vertexShader: iridescentVertexShader,
  fragmentShader: iridescentFragmentShader,
  uniforms: {
    uSceneTexture: { value: renderTarget.texture },
    uResolution: { value: new THREE.Vector2(fboWidth, fboHeight) },
    uTime: { value: 0.0 },
    uRefractPower: { value: PARAMS.iridRefractPower },
    uFrequency: { value: PARAMS.iridFrequency },
    uNoiseScale: { value: PARAMS.iridNoiseScale },
    uIridescenceIntensity: { value: PARAMS.iridIntensity },
    uTransparency: { value: PARAMS.iridTransparency },
    uFresnelPower: { value: PARAMS.iridFresnelPower },
    uLightPos: { value: new THREE.Vector3(5.0, 5.0, 5.0) },
    uSpecularColor: { value: new THREE.Color(0xffffff) },
    uShininess: { value: PARAMS.iridShininess }
  },
  side: THREE.DoubleSide,
  transparent: false,
});

// --- Material 3: Mercúrio Líquido Cromado (Vertex Displacement) ---
const liquidMaterial = new THREE.ShaderMaterial({
  vertexShader: liquidVertexShader,
  fragmentShader: liquidFragmentShader,
  uniforms: {
    uSceneTexture: { value: renderTarget.texture },
    uResolution: { value: new THREE.Vector2(fboWidth, fboHeight) },
    uTime: { value: 0.0 },
    uWaveSpeed: { value: PARAMS.liquidWaveSpeed },
    uDisplacementScale: { value: PARAMS.liquidDisplacement },
    uNoiseFrequency: { value: PARAMS.liquidFrequency },
    uReflectionIntensity: { value: PARAMS.liquidReflection },
    uRoughness: { value: PARAMS.liquidRoughness },
    uFresnelPower: { value: PARAMS.liquidFresnelPower },
    uMetalColor: { value: new THREE.Color(PARAMS.liquidColor) },
    uLightPos: { value: new THREE.Vector3(5.0, 5.0, 5.0) },
    uSpecularColor: { value: new THREE.Color(0xffffff) }
  },
  side: THREE.DoubleSide,
  transparent: false,
});

// --- Geometrias com Subdivisão Otimizada para Deformação Fluida ---
function buildGeometry(type) {
  switch (type) {
    case 'Torus Knot':
      return new THREE.TorusKnotGeometry(1.0, 0.35, 180, 56);
    case 'Esfera':
      return new THREE.SphereGeometry(1.3, 80, 80);
    case 'Icosaedro':
      return new THREE.IcosahedronGeometry(1.35, 4);
    case 'Toro':
      return new THREE.TorusGeometry(1.15, 0.45, 48, 100);
    case 'Octaedro':
      return new THREE.OctahedronGeometry(1.4, 3);
    default:
      return new THREE.TorusKnotGeometry(1.0, 0.35, 180, 56);
  }
}

// Inicia com o material ativo
let currentMaterialInstance = liquidMaterial;
if (PARAMS.activeShader.includes('Vidro')) currentMaterialInstance = glassMaterial;
else if (PARAMS.activeShader.includes('Iridescente')) currentMaterialInstance = iridescentMaterial;

const glassMesh = new THREE.Mesh(buildGeometry(PARAMS.geometry), currentMaterialInstance);
scene.add(glassMesh);

// --- Resize Listener ---
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
  iridescentMaterial.uniforms.uResolution.value.set(fboWidth, fboHeight);
  liquidMaterial.uniforms.uResolution.value.set(fboWidth, fboHeight);
});

// --- Interface lil-gui Interativa com Pastas Reativas ---
const gui = new GUI({ title: 'Shader Playground' });

// Seletor Principal de Shader
gui.add(PARAMS, 'activeShader', [
  'Mercúrio Líquido (Cromado)',
  'Vidro Refrativo (RGB Split)',
  'Película Iridescente (Bolha)'
])
  .name('✨ Shader Ativo')
  .onChange(type => {
    updateActiveShader(type);
  });

// Pasta: Mercúrio Líquido Cromado
const fLiquid = gui.addFolder('Propriedades: Mercúrio Cromado');
fLiquid.add(PARAMS, 'liquidDisplacement', 0.0, 0.45, 0.01).name('Altura das Ondas')
  .onChange(v => { liquidMaterial.uniforms.uDisplacementScale.value = v; });
fLiquid.add(PARAMS, 'liquidWaveSpeed', 0.1, 3.0, 0.1).name('Velocidade das Ondas')
  .onChange(v => { liquidMaterial.uniforms.uWaveSpeed.value = v; });
fLiquid.add(PARAMS, 'liquidFrequency', 0.2, 2.5, 0.05).name('Frequência do Ruído')
  .onChange(v => { liquidMaterial.uniforms.uNoiseFrequency.value = v; });
fLiquid.add(PARAMS, 'liquidReflection', 0.5, 3.0, 0.1).name('Brilho Cromado')
  .onChange(v => { liquidMaterial.uniforms.uReflectionIntensity.value = v; });
fLiquid.add(PARAMS, 'liquidRoughness', 0.0, 0.5, 0.01).name('Rugosidade')
  .onChange(v => { liquidMaterial.uniforms.uRoughness.value = v; });
fLiquid.addColor(PARAMS, 'liquidColor').name('Cor do Metal')
  .onChange(v => { liquidMaterial.uniforms.uMetalColor.value.set(v); });

// Pasta: Vidro Refrativo
const fGlass = gui.addFolder('Propriedades: Vidro Refrativo');
fGlass.add(PARAMS, 'glassRefractPower', 0.0, 0.35, 0.005).name('Poder de Refração')
  .onChange(v => { glassMaterial.uniforms.uRefractPower.value = v; });
fGlass.add(PARAMS, 'glassAberration', 0.0, 0.1, 0.002).name('RGB Split (Dispersão)')
  .onChange(v => { glassMaterial.uniforms.uChromaticAberration.value = v; });
fGlass.add(PARAMS, 'glassFresnelIntensity', 0.0, 3.0, 0.1).name('Intensidade Fresnel')
  .onChange(v => { glassMaterial.uniforms.uFresnelIntensity.value = v; });
fGlass.add(PARAMS, 'glassFresnelPower', 1.0, 6.0, 0.1).name('Exponente Fresnel')
  .onChange(v => { glassMaterial.uniforms.uFresnelPower.value = v; });
fGlass.addColor(PARAMS, 'glassFresnelColor').name('Cor Fresnel')
  .onChange(v => { glassMaterial.uniforms.uFresnelColor.value.set(v); });
fGlass.add(PARAMS, 'glassShininess', 8.0, 128.0, 2.0).name('Especularidade')
  .onChange(v => { glassMaterial.uniforms.uShininess.value = v; });

// Pasta: Película Iridescente
const fIrid = gui.addFolder('Propriedades: Película Iridescente');
fIrid.add(PARAMS, 'iridIntensity', 0.0, 3.0, 0.05).name('Brilho do Arco-íris')
  .onChange(v => { iridescentMaterial.uniforms.uIridescenceIntensity.value = v; });
fIrid.add(PARAMS, 'iridFrequency', 0.5, 6.0, 0.1).name('Densidade de Cores')
  .onChange(v => { iridescentMaterial.uniforms.uFrequency.value = v; });
fIrid.add(PARAMS, 'iridNoiseScale', 0.0, 1.5, 0.05).name('Ondulação Líquida')
  .onChange(v => { iridescentMaterial.uniforms.uNoiseScale.value = v; });
fIrid.add(PARAMS, 'iridTransparency', 0.0, 1.0, 0.02).name('Transparência do Sabão')
  .onChange(v => { iridescentMaterial.uniforms.uTransparency.value = v; });
fIrid.add(PARAMS, 'iridRefractPower', 0.0, 0.25, 0.005).name('Distorção de Fundo')
  .onChange(v => { iridescentMaterial.uniforms.uRefractPower.value = v; });
fIrid.add(PARAMS, 'iridFresnelPower', 1.0, 5.0, 0.1).name('Aro de Borda (Fresnel)')
  .onChange(v => { iridescentMaterial.uniforms.uFresnelPower.value = v; });
fIrid.add(PARAMS, 'iridShininess', 8.0, 128.0, 2.0).name('Polimento Especular')
  .onChange(v => { iridescentMaterial.uniforms.uShininess.value = v; });

// Pasta: Configurações da Cena
const fScene = gui.addFolder('Cena & Interação');
fScene.add(PARAMS, 'geometry', ['Torus Knot', 'Esfera', 'Icosaedro', 'Toro', 'Octaedro'])
  .name('Forma do Objeto')
  .onChange(type => {
    glassMesh.geometry.dispose();
    glassMesh.geometry = buildGeometry(type);
  });
fScene.add(PARAMS, 'zoomSmoothness', 0.02, 0.20, 0.01).name('Suavidade do Zoom');
fScene.add(PARAMS, 'autoRotate').name('Girar Objeto');
fScene.add(PARAMS, 'rotationSpeed', 0.1, 3.0, 0.1).name('Vel. Rotação');
fScene.add(PARAMS, 'bgSpeed', 0.0, 3.0, 0.1).name('Vel. Fundo');

function toggleFolderVisibility(folder, isVisible) {
  if (typeof folder.show === 'function' && typeof folder.hide === 'function') {
    isVisible ? folder.show() : folder.hide();
  } else if (folder.domElement) {
    folder.domElement.style.display = isVisible ? '' : 'none';
  }
}

function updateActiveShader(type) {
  if (type.includes('Vidro')) {
    glassMesh.material = glassMaterial;
    glassMesh.material.needsUpdate = true;
    toggleFolderVisibility(fGlass, true);
    toggleFolderVisibility(fIrid, false);
    toggleFolderVisibility(fLiquid, false);
  } else if (type.includes('Iridescente')) {
    glassMesh.material = iridescentMaterial;
    glassMesh.material.needsUpdate = true;
    toggleFolderVisibility(fGlass, false);
    toggleFolderVisibility(fIrid, true);
    toggleFolderVisibility(fLiquid, false);
  } else {
    glassMesh.material = liquidMaterial;
    glassMesh.material.needsUpdate = true;
    toggleFolderVisibility(fGlass, false);
    toggleFolderVisibility(fIrid, false);
    toggleFolderVisibility(fLiquid, true);
  }
}

// Configura o estado visual inicial das pastas
updateActiveShader(PARAMS.activeShader);
fScene.open();

// --- Loop de Renderização Multi-Pass ---
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);

  const delta = clock.getDelta();
  const elapsedTime = clock.getElapsedTime();

  // 1. Atualizar animações de fundo e ponto de luz
  bgController.update(elapsedTime, PARAMS.bgSpeed);

  // 2. Rotação do objeto
  if (PARAMS.autoRotate) {
    glassMesh.rotation.x += 0.006 * PARAMS.rotationSpeed;
    glassMesh.rotation.y += 0.010 * PARAMS.rotationSpeed;
  }

  // 3. Zoom Suave interpolado
  currentDistance = THREE.MathUtils.lerp(currentDistance, targetDistance, PARAMS.zoomSmoothness);
  const camOffset = new THREE.Vector3().subVectors(camera.position, controls.target);
  if (camOffset.lengthSq() > 0.0001) {
    camOffset.normalize().multiplyScalar(currentDistance);
    camera.position.copy(controls.target).add(camOffset);
  }
  controls.update();

  // 4. Atualizar uniforms dinâmicas
  const lightPos = bgController.coloredPointLight.position;
  glassMaterial.uniforms.uLightPos.value.copy(lightPos);
  iridescentMaterial.uniforms.uLightPos.value.copy(lightPos);
  liquidMaterial.uniforms.uLightPos.value.copy(lightPos);

  iridescentMaterial.uniforms.uTime.value = elapsedTime;
  liquidMaterial.uniforms.uTime.value = elapsedTime;

  // ==========================================================
  // PASSO 1 DO FBO: Renderizar fundo no RenderTarget
  // ==========================================================
  glassMesh.visible = false;
  renderer.setRenderTarget(renderTarget);
  renderer.render(scene, camera);

  // ==========================================================
  // PASSO 2: Renderizar cena completa no Canvas
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
    print("  Corrigindo: Three.js Shader Playground (Mercúrio Líquido)")
    print("=" * 70)

    base_dir = Path(".")

    for rel_path, content in FILES.items():
        file_path = base_dir / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f" [✔] Arquivo atualizado: {file_path}")

    print("\n" + "=" * 70)
    print("  CORREÇÃO APLICADA COM SUCESSO!")
    print("=" * 70)
    print("  Como testar:")
    print("  1. Recarregue a página no navegador (F5 ou Ctrl+R).")
    print("  2. O Mercúrio Líquido Ondulante aparecerá imediatamente no centro!")
    print("=" * 70)

if __name__ == "__main__":
    main()