import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import GUI from 'lil-gui';
import { Shaders } from './shaders.js';
import { setupBackgroundScene, updateBackgroundScene } from './scene.js';

// =============================================================================
// SETUP DE CENA, RENDERER E CÂMERA
// =============================================================================
const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x050508);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 150);
camera.position.set(0, 2.5, 9.5);

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
const dpr = Math.min(window.devicePixelRatio, 2);
renderer.setPixelRatio(dpr);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;
container.appendChild(renderer.domElement);

// =============================================================================
// PIPELINE MULTI-PASS COM FBO E ALINHAMENTO DPI
// =============================================================================
let fboWidth = Math.floor(window.innerWidth * dpr);
let fboHeight = Math.floor(window.innerHeight * dpr);

const renderTarget = new THREE.WebGLRenderTarget(fboWidth, fboHeight, {
    minFilter: THREE.LinearFilter,
    magFilter: THREE.LinearFilter,
    format: THREE.RGBAFormat
});

const uResolutionVec = new THREE.Vector2(fboWidth, fboHeight);

// Cenário de fundo procedural (zero texturas externas)
const bgData = setupBackgroundScene(scene);

// =============================================================================
// PASSE FULLSCREEN EXCLUSIVO PARA O BURACO NEGRO (LENSING CONTÍNUO)
// =============================================================================
const postScene = new THREE.Scene();
const postCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

const blackHoleMaterial = new THREE.ShaderMaterial({
    vertexShader: Shaders.blackhole.vertexShader,
    fragmentShader: Shaders.blackhole.fragmentShader,
    uniforms: {
        uSceneTexture: { value: renderTarget.texture },
        uResolution: { value: uResolutionVec },
        uCenterUV: { value: new THREE.Vector2(0.5, 0.5) },
        uTime: { value: 0.0 },
        uCameraPosition: { value: camera.position },
        uBlackHolePosition: { value: new THREE.Vector3(0, 0, 0) },
        uInvViewMatrix: { value: new THREE.Matrix4() },
        uInvProjectionMatrix: { value: new THREE.Matrix4() },

        uHorizonRadius: { value: 0.85 },
        uLensingStrength: { value: 0.55 },
        uPhotonRingIntensity: { value: 3.2 },
        uPhotonRingThickness: { value: 0.035 },
        uDiskInner: { value: 1.25 },
        uDiskOuter: { value: 3.6 },
        uDiskSpeed: { value: 1.4 },
        uDopplerStrength: { value: 0.8 },
        uDiskColorCore: { value: new THREE.Color(0xffeed6) },
        uDiskColorEdge: { value: new THREE.Color(0xff4d05) },
        uDispersion: { value: 0.012 },
        uSpin: { value: 0.25 }
    },
    depthTest: false,
    depthWrite: false
});

const postQuad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), blackHoleMaterial);
postScene.add(postQuad);

// =============================================================================
// MATERIAIS PARA MALHAS 3D (VIDRO, PELÍCULA, MERCÚRIO)
// =============================================================================
const materials = {
    'Buraco Negro (Lensing)': blackHoleMaterial,

    'Vidro Refrativo (RGB Split)': new THREE.ShaderMaterial({
        vertexShader: Shaders.glass.vertexShader,
        fragmentShader: Shaders.glass.fragmentShader,
        uniforms: {
            uSceneTexture: { value: renderTarget.texture },
            uResolution: { value: uResolutionVec },
            uIor: { value: 1.18 },
            uDispersion: { value: 0.025 },
            uFresnelPower: { value: 2.8 },
            uRoughness: { value: 0.08 },
            uTint: { value: new THREE.Color(0xffffff) }
        },
        transparent: false,
        depthWrite: true
    }),

    'Película Iridescente': new THREE.ShaderMaterial({
        vertexShader: Shaders.iridescent.vertexShader,
        fragmentShader: Shaders.iridescent.fragmentShader,
        uniforms: {
            uSceneTexture: { value: renderTarget.texture },
            uResolution: { value: uResolutionVec },
            uTime: { value: 0.0 },
            uFilmThickness: { value: 2.4 },
            uNoiseScale: { value: 2.8 },
            uIridescenceIntensity: { value: 1.0 },
            uOpacity: { value: 0.88 }
        },
        transparent: true,
        depthWrite: false
    }),

    'Mercúrio Líquido': new THREE.ShaderMaterial({
        vertexShader: Shaders.mercury.vertexShader,
        fragmentShader: Shaders.mercury.fragmentShader,
        uniforms: {
            uSceneTexture: { value: renderTarget.texture },
            uResolution: { value: uResolutionVec },
            uTime: { value: 0.0 },
            uNoiseScale: { value: 1.4 },
            uNoiseSpeed: { value: 0.75 },
            uDisplacement: { value: 0.32 },
            uMetalness: { value: 0.96 }
        },
        transparent: false,
        depthWrite: true
    })
};

// =============================================================================
// MALHA CENTRAL E GEOMETRIAS (USADAS NOS SHADERS 3D)
// =============================================================================
const geometries = {
    'Esfera': new THREE.SphereGeometry(2.0, 64, 64),
    'Torus Knot': new THREE.TorusKnotGeometry(1.4, 0.45, 128, 32),
    'Icosaedro': new THREE.IcosahedronGeometry(2.1, 4),
    'Cilindro': new THREE.CylinderGeometry(1.6, 1.6, 3.2, 64, 16)
};

const state = {
    shader: 'Buraco Negro (Lensing)',
    geometry: 'Esfera',
    autoRotateScene: true
};

const centralMesh = new THREE.Mesh(geometries[state.geometry], materials['Vidro Refrativo (RGB Split)']);
centralMesh.position.set(0, 0, 0);
scene.add(centralMesh);

// =============================================================================
// ZOOM CINEMÁTICO SUAVE (EXPONENTIAL LERP)
// =============================================================================
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.enableZoom = false;

let targetCameraDistance = camera.position.distanceTo(controls.target);
const minDistance = 3.2;
const maxDistance = 22.0;

window.addEventListener('wheel', (e) => {
    e.preventDefault();
    const factor = 1.0 + Math.sign(e.deltaY) * 0.085;
    targetCameraDistance = Math.max(minDistance, Math.min(maxDistance, targetCameraDistance * factor));
}, { passive: false });

let touchStartDist = 0;
window.addEventListener('touchstart', (e) => {
    if (e.touches.length === 2) {
        touchStartDist = Math.hypot(
            e.touches[0].clientX - e.touches[1].clientX,
            e.touches[0].clientY - e.touches[1].clientY
        );
    }
}, { passive: true });

window.addEventListener('touchmove', (e) => {
    if (e.touches.length === 2) {
        const dist = Math.hypot(
            e.touches[0].clientX - e.touches[1].clientX,
            e.touches[0].clientY - e.touches[1].clientY
        );
        const delta = touchStartDist - dist;
        if (Math.abs(delta) > 2) {
            const factor = 1.0 + (delta / 280.0);
            targetCameraDistance = Math.max(minDistance, Math.min(maxDistance, targetCameraDistance * factor));
            touchStartDist = dist;
        }
    }
}, { passive: true });

// =============================================================================
// INTERFACE LIL-GUI DINÂMICA
// =============================================================================
const gui = new GUI({ title: 'Shader Playground' });

const shaderCtrl = gui.add(state, 'shader', Object.keys(materials)).name('Shader Ativo').onChange(val => {
    if (val !== 'Buraco Negro (Lensing)') {
        centralMesh.material = materials[val];
    }
    updateGuiFolders(val);
    updateHudInfo(val);
});

const geomCtrl = gui.add(state, 'geometry', Object.keys(geometries)).name('Geometria 3D').onChange(val => {
    centralMesh.geometry = geometries[val];
});

gui.add(state, 'autoRotateScene').name('Girar Fundo');

// Pastas para cada shader
const folderBlackHole = gui.addFolder('Buraco Negro');
const bhUniforms = blackHoleMaterial.uniforms;
folderBlackHole.add(bhUniforms.uHorizonRadius, 'value', 0.4, 1.6, 0.01).name('Raio Horizonte (Rs)');
folderBlackHole.add(bhUniforms.uLensingStrength, 'value', 0.1, 1.5, 0.01).name('Força Lente');
folderBlackHole.add(bhUniforms.uPhotonRingIntensity, 'value', 0.5, 6.0, 0.1).name('Brilho Anel Fótons');
folderBlackHole.add(bhUniforms.uPhotonRingThickness, 'value', 0.005, 0.08, 0.005).name('Espessura Fótons');
folderBlackHole.add(bhUniforms.uDiskInner, 'value', 0.9, 2.2, 0.01).name('Disco ISCO (Raio In)');
folderBlackHole.add(bhUniforms.uDiskOuter, 'value', 2.0, 5.0, 0.05).name('Disco (Raio Out)');
folderBlackHole.add(bhUniforms.uDiskSpeed, 'value', 0.0, 4.0, 0.1).name('Velocidade Kepler');
folderBlackHole.add(bhUniforms.uDopplerStrength, 'value', 0.0, 1.5, 0.05).name('Doppler Beaming');
folderBlackHole.addColor({ color: '#ffeed6' }, 'color').name('Cor Núcleo').onChange(c => bhUniforms.uDiskColorCore.value.set(c));
folderBlackHole.addColor({ color: '#ff4d05' }, 'color').name('Cor Borda').onChange(c => bhUniforms.uDiskColorEdge.value.set(c));
folderBlackHole.add(bhUniforms.uSpin, 'value', 0.0, 0.8, 0.01).name('Kerr Spin (Arrasto)');
folderBlackHole.add(bhUniforms.uDispersion, 'value', 0.0, 0.04, 0.001).name('Dispersão Cromática');

const folderGlass = gui.addFolder('Vidro Refrativo');
const gUniforms = materials['Vidro Refrativo (RGB Split)'].uniforms;
folderGlass.add(gUniforms.uIor, 'value', 1.0, 2.5, 0.01).name('Índice Refr. (IOR)');
folderGlass.add(gUniforms.uDispersion, 'value', 0.0, 0.08, 0.002).name('RGB Split');
folderGlass.add(gUniforms.uFresnelPower, 'value', 0.5, 5.0, 0.1).name('Força Fresnel');
folderGlass.add(gUniforms.uRoughness, 'value', 0.0, 0.5, 0.01).name('Rugosidade');
folderGlass.addColor({ color: '#ffffff' }, 'color').name('Tonalidade').onChange(c => gUniforms.uTint.value.set(c));

const folderIridescent = gui.addFolder('Película Iridescente');
const iUniforms = materials['Película Iridescente'].uniforms;
folderIridescent.add(iUniforms.uFilmThickness, 'value', 0.5, 6.0, 0.1).name('Espessura Filme');
folderIridescent.add(iUniforms.uNoiseScale, 'value', 0.5, 8.0, 0.1).name('Escala de Ondas');
folderIridescent.add(iUniforms.uIridescenceIntensity, 'value', 0.1, 2.0, 0.05).name('Intensidade Cor');
folderIridescent.add(iUniforms.uOpacity, 'value', 0.1, 1.0, 0.02).name('Opacidade');

const folderMercury = gui.addFolder('Mercúrio Líquido');
const mUniforms = materials['Mercúrio Líquido'].uniforms;
folderMercury.add(mUniforms.uNoiseScale, 'value', 0.2, 4.0, 0.1).name('Escala Turbulência');
folderMercury.add(mUniforms.uNoiseSpeed, 'value', 0.1, 2.5, 0.05).name('Velocidade Fluido');
folderMercury.add(mUniforms.uDisplacement, 'value', 0.0, 0.8, 0.02).name('Altura Deformação');
folderMercury.add(mUniforms.uMetalness, 'value', 0.5, 1.0, 0.02).name('Metalicidade');

function updateGuiFolders(activeShader) {
    const isBH = activeShader === 'Buraco Negro (Lensing)';
    folderBlackHole.show(isBH);
    folderGlass.show(activeShader === 'Vidro Refrativo (RGB Split)');
    folderIridescent.show(activeShader === 'Película Iridescente');
    folderMercury.show(activeShader === 'Mercúrio Líquido');

    // A singularidade cósmica não usa geometria poligonal fechada
    if (isBH) {
        geomCtrl.hide();
        folderBlackHole.open();
    } else {
        geomCtrl.show();
        if (activeShader === 'Vidro Refrativo (RGB Split)') folderGlass.open();
        if (activeShader === 'Película Iridescente') folderIridescent.open();
        if (activeShader === 'Mercúrio Líquido') folderMercury.open();
    }
}

function updateHudInfo(shaderName) {
    const titleEl = document.getElementById('hud-active-shader');
    const descEl = document.getElementById('hud-description');

    const descriptions = {
        'Buraco Negro (Lensing)': 'Lente gravitacional einsteiniana contínua com horizonte de Schwarzschild, disco de acreção 3D com rotação Kepleriana, efeito Doppler relativístico e duplo arco de auréola.',
        'Vidro Refrativo (RGB Split)': 'Refração vetorial baseada na normal de visão, 3 amostragens na textura do FBO com offsets espectrais para separação de canais R, G e B, Fresnel e Blinn-Phong.',
        'Película Iridescente': 'Gradiente de cores baseado na fórmula de cossenos de Inigo Quilez, deformação ondulatória na espessura do filme via ruído procedural, Fresnel e transmissão FBO.',
        'Mercúrio Líquido': 'Deformação orgânica da malha direto no Vertex Shader com Simplex 3D Noise multi-oitavas, recálculo analítico de normais no espaço tangente por diferenças finitas e reflexo cromado.'
    };

    if (titleEl) titleEl.textContent = shaderName;
    if (descEl) descEl.textContent = descriptions[shaderName] || '';
}

updateGuiFolders(state.shader);

// =============================================================================
// REDIMENSIONAMENTO E PREVENÇÃO DE BUGS DPI
// =============================================================================
window.addEventListener('resize', () => {
    const w = window.innerWidth;
    const h = window.innerHeight;
    const currentDpr = Math.min(window.devicePixelRatio, 2);

    camera.aspect = w / h;
    camera.updateProjectionMatrix();

    renderer.setSize(w, h);
    renderer.setPixelRatio(currentDpr);

    const fW = Math.floor(w * currentDpr);
    const fH = Math.floor(h * currentDpr);
    renderTarget.setSize(fW, fH);

    uResolutionVec.set(fW, fH);
});

// =============================================================================
// LOOP MULTI-PASS COM FBO (60 FPS)
// =============================================================================
const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);

    const delta = clock.getDelta();
    const elapsedTime = clock.getElapsedTime();

    if (state.autoRotateScene) {
        updateBackgroundScene(bgData, elapsedTime, delta);
    }

    // Zoom Cinemático (Lerp contínuo)
    const currentDist = camera.position.distanceTo(controls.target);
    if (Math.abs(currentDist - targetCameraDistance) > 0.001) {
        const newDist = THREE.MathUtils.lerp(currentDist, targetCameraDistance, 0.08);
        const dir = camera.position.clone().sub(controls.target).normalize();
        camera.position.copy(controls.target).addScaledVector(dir, newDist);
    }
    controls.update();

    camera.updateMatrixWorld();

    const isBH = state.shader === 'Buraco Negro (Lensing)';

    // =========================================================================
    // PASSO 1: Captura a cena de fundo completa no FBO
    // =========================================================================
    centralMesh.visible = false;
    renderer.setRenderTarget(renderTarget);
    renderer.render(scene, camera);

    // =========================================================================
    // PASSO 2: Renderização final com Shader Ativo
    // =========================================================================
    renderer.setRenderTarget(null);

    if (isBH) {
        // Buraco Negro Cósmico: Passe Fullscreen contínuo
        bhUniforms.uTime.value = elapsedTime;
        bhUniforms.uCameraPosition.value.copy(camera.position);

        // Projeção exata do centro da singularidade na tela
        const projected = new THREE.Vector3(0, 0, 0).project(camera);
        bhUniforms.uCenterUV.value.set(
            projected.x * 0.5 + 0.5,
            projected.y * 0.5 + 0.5
        );

        // Matrizes inversas para reconstrução do raio de visão de cada pixel
        bhUniforms.uInvViewMatrix.value.copy(camera.matrixWorld);
        bhUniforms.uInvProjectionMatrix.value.copy(camera.projectionMatrixInverse);

        renderer.render(postScene, postCamera);
    } else {
        // Shaders de Malha 3D (Vidro, Película, Mercúrio)
        centralMesh.visible = true;

        const activeMat = materials[state.shader];
        if (activeMat && activeMat.uniforms) {
            if (activeMat.uniforms.uTime) activeMat.uniforms.uTime.value = elapsedTime;
        }

        centralMesh.rotation.y = elapsedTime * 0.25;
        centralMesh.rotation.x = Math.sin(elapsedTime * 0.2) * 0.15;

        renderer.render(scene, camera);
    }
}

animate();
