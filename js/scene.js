/**
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
