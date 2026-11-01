/**
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
