/**
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
