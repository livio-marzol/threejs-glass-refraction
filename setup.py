import os
from pathlib import Path

FILES = {}

# ==============================================================================
# 1. index.html
# ==============================================================================
FILES["index.html"] = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Shader Playground - Buraco Negro & Lente Gravitacional</title>
    <link rel="stylesheet" href="css/style.css">
    
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

    <!-- HUD Glassmorphism -->
    <div id="hud-overlay">
        <div class="hud-card">
            <div class="hud-header">
                <span class="status-indicator"></span>
                <span class="hud-title">SHADER PLAYGROUND</span>
            </div>
            <div class="hud-shader-name" id="hud-active-shader">Buraco Negro (Lensing)</div>
            <p class="hud-desc" id="hud-description">
                Lente gravitacional einsteiniana contínua com horizonte de Schwarzschild, disco de acreção 3D com rotação Kepleriana, efeito Doppler relativístico e duplo arco de auréola.
            </p>
            <div class="hud-tags">
                <span class="hud-tag">Multi-Pass FBO</span>
                <span class="hud-tag">DPI Aligned</span>
                <span class="hud-tag">Zero Asset</span>
                <span class="hud-tag">Cinematic Zoom</span>
            </div>
        </div>
        <div class="hud-hint">
            <span>🖱️ Arraste para orbitar | Scroll para zoom cinemático | lil-gui para alternar shaders</span>
        </div>
    </div>

    <script type="module" src="js/main.js"></script>
</body>
</html>
"""

# ==============================================================================
# 2. css/style.css
# ==============================================================================
FILES["css/style.css"] = """* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    user-select: none;
    -webkit-user-select: none;
}

body, html {
    width: 100%;
    height: 100%;
    overflow: hidden;
    background-color: #050508;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #e2e8f0;
}

#canvas-container {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
}

#hud-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 10;
    pointer-events: none;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 24px;
}

.hud-card {
    pointer-events: auto;
    max-width: 380px;
    background: rgba(13, 16, 26, 0.75);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.15);
    transition: transform 0.3s ease, border-color 0.3s ease;
}

.hud-card:hover {
    border-color: rgba(0, 243, 255, 0.35);
}

.hud-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}

.status-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #00f3ff;
    box-shadow: 0 0 10px #00f3ff;
    animation: pulseGlow 2s infinite ease-in-out;
}

@keyframes pulseGlow {
    0%, 100% { opacity: 0.5; transform: scale(0.9); }
    50% { opacity: 1; transform: scale(1.15); }
}

.hud-title {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #94a3b8;
    text-transform: uppercase;
}

.hud-shader-name {
    font-size: 20px;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #ffffff;
    margin-bottom: 8px;
    text-shadow: 0 0 20px rgba(0, 243, 255, 0.3);
}

.hud-desc {
    font-size: 13px;
    line-height: 1.5;
    color: #cbd5e1;
    margin-bottom: 16px;
}

.hud-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.hud-tag {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.5px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 4px 10px;
    border-radius: 20px;
    color: #38bdf8;
}

.hud-hint {
    pointer-events: none;
    font-size: 12px;
    color: #64748b;
    background: rgba(10, 12, 18, 0.6);
    backdrop-filter: blur(8px);
    padding: 8px 16px;
    border-radius: 24px;
    align-self: center;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.lil-gui {
    --background-color: rgba(13, 16, 26, 0.85) !important;
    --text-color: #e2e8f0 !important;
    --title-background-color: rgba(20, 24, 38, 0.95) !important;
    --widget-color: rgba(30, 38, 58, 0.9) !important;
    --hover-color: rgba(0, 243, 255, 0.25) !important;
    --focus-color: #00f3ff !important;
    --number-color: #00f3ff !important;
    --string-color: #38bdf8 !important;
    font-family: inherit !important;
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5) !important;
    backdrop-filter: blur(20px) !important;
    margin-top: 24px !important;
    margin-right: 24px !important;
}

.lil-gui .title {
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
}
"""

# ==============================================================================
# 3. js/shaders.js
# ==============================================================================
FILES["js/shaders.js"] = """// Repositório Central de Shaders em GLSL (Shader Playground)

export const Shaders = {
    // -------------------------------------------------------------------------
    // 1. Vidro Refrativo (RGB Split / Aberração Cromática)
    // -------------------------------------------------------------------------
    glass: {
        vertexShader: `
            varying vec3 vNormalWorld;
            varying vec3 vViewDirWorld;
            varying vec3 vNormalView;
            varying vec3 vViewDirView;

            void main() {
                vec4 worldPos = modelMatrix * vec4(position, 1.0);
                vViewDirWorld = normalize(cameraPosition - worldPos.xyz);
                vNormalWorld = normalize(mat3(modelMatrix) * normal);
                
                vec4 viewPos = modelViewMatrix * vec4(position, 1.0);
                vViewDirView = normalize(-viewPos.xyz);
                vNormalView = normalize(normalMatrix * normal);

                gl_Position = projectionMatrix * viewPos;
            }
        `,
        fragmentShader: `
            uniform sampler2D uSceneTexture;
            uniform vec2 uResolution;
            uniform float uIor;
            uniform float uDispersion;
            uniform float uFresnelPower;
            uniform float uRoughness;
            uniform vec3 uTint;

            varying vec3 vNormalWorld;
            varying vec3 vViewDirWorld;
            varying vec3 vNormalView;
            varying vec3 vViewDirView;

            void main() {
                vec2 screenUV = gl_FragCoord.xy / uResolution.xy;
                vec3 N = normalize(vNormalView);
                vec3 V = normalize(vViewDirView);

                float NdotV = max(dot(N, V), 0.0);
                float f0 = pow((1.0 - uIor) / (1.0 + uIor), 2.0);
                float fresnel = f0 + (1.0 - f0) * pow(1.0 - NdotV, uFresnelPower);

                float etaR = 1.0 / (uIor - uDispersion);
                float etaG = 1.0 / uIor;
                float etaB = 1.0 / (uIor + uDispersion);

                vec3 refrR = refract(-V, N, etaR);
                vec3 refrG = refract(-V, N, etaG);
                vec3 refrB = refract(-V, N, etaB);

                vec2 uvR = screenUV + refrR.xy * (0.08 + uRoughness * 0.05);
                vec2 uvG = screenUV + refrG.xy * (0.08 + uRoughness * 0.05);
                vec2 uvB = screenUV + refrB.xy * (0.08 + uRoughness * 0.05);

                float colR = texture2D(uSceneTexture, uvR).r;
                float colG = texture2D(uSceneTexture, uvG).g;
                float colB = texture2D(uSceneTexture, uvB).b;

                vec3 refractedColor = vec3(colR, colG, colB) * uTint;

                vec3 lightDir = normalize(vec3(0.5, 1.0, 0.8));
                vec3 H = normalize(lightDir + V);
                float spec = pow(max(dot(N, H), 0.0), 32.0 / max(uRoughness, 0.05));
                vec3 specular = vec3(1.0) * spec * 0.8;

                vec3 finalColor = mix(refractedColor, vec3(1.0), fresnel * 0.5) + specular;
                gl_FragColor = vec4(finalColor, 1.0);
            }
        `
    },

    // -------------------------------------------------------------------------
    // 2. Película Iridescente (Thin-Film / Bolha de Sabão)
    // -------------------------------------------------------------------------
    iridescent: {
        vertexShader: `
            varying vec3 vNormal;
            varying vec3 vViewDir;
            varying vec3 vWorldPosition;

            void main() {
                vec4 worldPos = modelMatrix * vec4(position, 1.0);
                vWorldPosition = worldPos.xyz;
                vNormal = normalize(mat3(modelMatrix) * normal);
                vViewDir = normalize(cameraPosition - worldPos.xyz);
                gl_Position = projectionMatrix * viewMatrix * worldPos;
            }
        `,
        fragmentShader: `
            uniform sampler2D uSceneTexture;
            uniform vec2 uResolution;
            uniform float uTime;
            uniform float uFilmThickness;
            uniform float uNoiseScale;
            uniform float uIridescenceIntensity;
            uniform float uOpacity;

            varying vec3 vNormal;
            varying vec3 vViewDir;
            varying vec3 vWorldPosition;

            vec3 cosinePalette(float t, vec3 a, vec3 b, vec3 c, vec3 d) {
                return a + b * cos(6.2831853 * (c * t + d));
            }

            void main() {
                vec2 screenUV = gl_FragCoord.xy / uResolution.xy;
                vec3 N = normalize(vNormal);
                vec3 V = normalize(vViewDir);

                float cosTheta = max(dot(N, V), 0.0);
                float fresnel = pow(1.0 - cosTheta, 2.8);

                float noise = sin(vWorldPosition.x * uNoiseScale + uTime * 0.7) *
                              cos(vWorldPosition.y * uNoiseScale + uTime * 0.5) *
                              sin(vWorldPosition.z * uNoiseScale + uTime * 0.6);

                float opticalPath = uFilmThickness * (1.0 + noise * 0.25) / max(cosTheta, 0.15);
                
                vec3 a = vec3(0.5, 0.5, 0.5);
                vec3 b = vec3(0.5, 0.5, 0.5);
                vec3 c = vec3(1.0, 1.0, 1.0);
                vec3 d = vec3(0.0, 0.33, 0.67);
                vec3 iridColor = cosinePalette(opticalPath, a, b, c, d);

                vec2 refrUV = screenUV + N.xy * 0.035;
                vec3 bg = texture2D(uSceneTexture, refrUV).rgb;

                vec3 mixedColor = mix(bg, iridColor, fresnel * uIridescenceIntensity);
                gl_FragColor = vec4(mixedColor, uOpacity);
            }
        `
    },

    // -------------------------------------------------------------------------
    // 3. Mercúrio Líquido Cromado (Vertex Displacement + Tangent Normal Recalc)
    // -------------------------------------------------------------------------
    mercury: {
        vertexShader: `
            uniform float uTime;
            uniform float uNoiseScale;
            uniform float uNoiseSpeed;
            uniform float uDisplacement;

            varying vec3 vNormalWorld;
            varying vec3 vViewDirWorld;
            varying vec3 vWorldPosition;

            vec4 permute(vec4 x) { return mod(((x * 34.0) + 1.0) * x, 289.0); }
            vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }

            float snoise(vec3 v) {
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

                float n_ = 0.142857142857;
                vec3  ns = n_ * D.wyz - D.xzx;

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
                p0 *= norm.x;
                p1 *= norm.y;
                p2 *= norm.z;
                p3 *= norm.w;

                vec4 m = max(0.6 - vec4(dot(x0, x0), dot(x1, x1), dot(x2, x2), dot(x3, x3)), 0.0);
                m = m * m;
                return 42.0 * dot(m * m, vec4(dot(p0, x0), dot(p1, x1), dot(p2, x2), dot(p3, x3)));
            }

            float getDisplacement(vec3 p) {
                float n1 = snoise(p * uNoiseScale + vec3(0.0, uTime * uNoiseSpeed, 0.0));
                float n2 = snoise(p * (uNoiseScale * 2.1) - vec3(uTime * uNoiseSpeed * 0.8, 0.0, 0.0)) * 0.5;
                return (n1 + n2) * uDisplacement;
            }

            void main() {
                float disp = getDisplacement(position);
                vec3 displacedPos = position + normal * disp;

                float eps = 0.01;
                vec3 tangent = normalize(abs(normal.y) < 0.999 ? cross(normal, vec3(0.0, 1.0, 0.0)) : cross(normal, vec3(0.0, 0.0, 1.0)));
                vec3 bitangent = cross(normal, tangent);

                vec3 pT = position + tangent * eps;
                vec3 pB = position + bitangent * eps;

                pT += normal * getDisplacement(pT);
                pB += normal * getDisplacement(pB);

                vec3 newNormal = normalize(cross(pT - displacedPos, pB - displacedPos));

                vec4 worldPos = modelMatrix * vec4(displacedPos, 1.0);
                vWorldPosition = worldPos.xyz;
                vNormalWorld = normalize(mat3(modelMatrix) * newNormal);
                vViewDirWorld = normalize(cameraPosition - worldPos.xyz);

                gl_Position = projectionMatrix * viewMatrix * worldPos;
            }
        `,
        fragmentShader: `
            uniform sampler2D uSceneTexture;
            uniform vec2 uResolution;
            uniform float uMetalness;

            varying vec3 vNormalWorld;
            varying vec3 vViewDirWorld;
            varying vec3 vWorldPosition;

            void main() {
                vec3 N = normalize(vNormalWorld);
                vec3 V = normalize(vViewDirWorld);
                vec3 R = reflect(-V, N);

                float chromeGradient = 0.5 + 0.5 * sin(R.y * 3.5 + 0.3);
                vec3 studioSky = mix(vec3(0.05, 0.06, 0.09), vec3(0.85, 0.92, 1.0), chromeGradient);
                
                vec2 screenUV = gl_FragCoord.xy / uResolution.xy;
                vec2 reflectUV = screenUV + R.xy * 0.22;
                vec3 sceneReflect = texture2D(uSceneTexture, reflectUV).rgb;

                float fresnel = 0.65 + 0.35 * pow(1.0 - max(dot(N, V), 0.0), 3.0);
                vec3 chromeBase = mix(studioSky, sceneReflect, 0.45);

                vec3 lightDir = normalize(vec3(0.4, 0.9, 0.6));
                vec3 H = normalize(lightDir + V);
                float spec = pow(max(dot(N, H), 0.0), 128.0) * 1.5;

                vec3 finalColor = chromeBase * fresnel * uMetalness + vec3(spec);
                gl_FragColor = vec4(finalColor, 1.0);
            }
        `
    },

    // -------------------------------------------------------------------------
    // 4. Buraco Negro / Lente Gravitacional Cósmica (Gargantua Interstellar)
    // -------------------------------------------------------------------------
    blackhole: {
        vertexShader: `
            varying vec2 vUv;
            void main() {
                vUv = uv;
                gl_Position = vec4(position.xy, 0.0, 1.0);
            }
        `,
        fragmentShader: `
            uniform sampler2D uSceneTexture;
            uniform vec2 uResolution;
            uniform vec2 uCenterUV;
            uniform float uTime;
            uniform vec3 uCameraPosition;
            uniform vec3 uBlackHolePosition;
            uniform mat4 uInvViewMatrix;
            uniform mat4 uInvProjectionMatrix;

            uniform float uHorizonRadius;
            uniform float uLensingStrength;
            uniform float uPhotonRingIntensity;
            uniform float uPhotonRingThickness;
            uniform float uDiskInner;
            uniform float uDiskOuter;
            uniform float uDiskSpeed;
            uniform float uDopplerStrength;
            uniform vec3 uDiskColorCore;
            uniform vec3 uDiskColorEdge;
            uniform float uDispersion;
            uniform float uSpin;

            varying vec2 vUv;

            // Ruído procedural para turbulência do disco de acreção
            float hash(vec2 p) {
                return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
            }

            float noise(vec2 p) {
                vec2 i = floor(p);
                vec2 f = fract(p);
                vec2 u = f * f * (3.0 - 2.0 * f);
                return mix(mix(hash(i + vec2(0.0,0.0)), hash(i + vec2(1.0,0.0)), u.x),
                           mix(hash(i + vec2(0.0,1.0)), hash(i + vec2(1.0,1.0)), u.x), u.y);
            }

            float fbm(vec2 p) {
                float v = 0.0;
                float a = 0.5;
                mat2 rot = mat2(cos(0.5), sin(0.5), -sin(0.5), cos(0.5));
                for (int i = 0; i < 4; ++i) {
                    v += a * noise(p);
                    p = rot * p * 2.0 + vec2(100.0);
                    a *= 0.5;
                }
                return v;
            }

            void main() {
                vec2 screenUV = gl_FragCoord.xy / uResolution.xy;
                float aspect = uResolution.x / uResolution.y;

                // Coordenadas radiais em relação ao centro do buraco negro na tela
                vec2 toCenterScreen = screenUV - uCenterUV;
                toCenterScreen.x *= aspect;
                float distScreen = length(toCenterScreen);
                vec2 dirScreen = distScreen > 0.0001 ? toCenterScreen / distScreen : vec2(0.0);

                // Reconstrução do raio 3D em espaço de mundo (da câmera através do pixel)
                vec2 ndc = screenUV * 2.0 - 1.0;
                vec4 clip = vec4(ndc, -1.0, 1.0);
                vec4 viewRay = uInvProjectionMatrix * clip;
                viewRay = vec4(viewRay.xy, -1.0, 0.0);
                vec3 rayDir = normalize((uInvViewMatrix * viewRay).xyz);
                vec3 rayOrigin = uCameraPosition;

                // Parâmetro de impacto b no espaço 3D (distância de aproximação máxima à singularidade)
                vec3 toBH = uBlackHolePosition - rayOrigin;
                float tClosest = dot(toBH, rayDir);
                vec3 pClosest = rayOrigin + rayDir * max(0.0, tClosest);
                float b = length(pClosest - uBlackHolePosition);

                float rHorizon = uHorizonRadius;

                // 1. Deflexão Gravitacional de Einstein (Lente gravitacional do fundo FBO)
                // A deflexão decresce suavemente com a distância, sem corte abrupto de geometria!
                float deflection = (uLensingStrength * 0.18) / (max(b - rHorizon * 0.95, 0.02) + 0.08);
                float fadeOut = smoothstep(5.5, 0.8, distScreen);
                vec2 uvOffset = dirScreen * deflection * fadeOut;

                // Arrasto de referenciais Kerr (Swirl gravitacional de rotação)
                vec2 swirl = vec2(-dirScreen.y, dirScreen.x) * (uSpin * 0.025 / (distScreen + 0.15)) * fadeOut;
                uvOffset += swirl;

                // Amostragem com aberração cromática contínua
                vec2 uvR = clamp(screenUV - uvOffset * (1.0 + uDispersion), 0.0, 1.0);
                vec2 uvG = clamp(screenUV - uvOffset, 0.0, 1.0);
                vec2 uvB = clamp(screenUV - uvOffset * (1.0 - uDispersion), 0.0, 1.0);

                vec3 bgCol = vec3(
                    texture2D(uSceneTexture, uvR).r,
                    texture2D(uSceneTexture, uvG).g,
                    texture2D(uSceneTexture, uvB).b
                );

                // 2. Disco de Acreção Relativístico 3D (Equatorial e Lenteado)
                vec3 diskNormal = normalize(vec3(0.18, 1.0, 0.12));
                vec3 diskCol = vec3(0.0);

                // Intersecção do raio com o plano do disco direto
                float denom = dot(rayDir, diskNormal);
                if (abs(denom) > 0.001) {
                    float tDisk = dot(uBlackHolePosition - rayOrigin, diskNormal) / denom;
                    if (tDisk > 0.0) {
                        vec3 pDisk = rayOrigin + rayDir * tDisk;
                        float rDisk = length(pDisk - uBlackHolePosition);
                        
                        // Oclusão pelo horizonte de eventos
                        bool occluded = (tDisk > tClosest) && (b < rHorizon);
                        if (rDisk >= uDiskInner && rDisk <= uDiskOuter && !occluded) {
                            vec3 rVec = pDisk - uBlackHolePosition;
                            vec3 uDisk = normalize(cross(diskNormal, vec3(0.0, 0.0, 1.0)));
                            vec3 vDisk = cross(diskNormal, uDisk);
                            float phi = atan(dot(rVec, vDisk), dot(rVec, uDisk));

                            // Velocidade Kepleriana: omega propto 1 / sqrt(r)
                            float rotSpeed = uDiskSpeed / sqrt(max(rDisk, 0.2));
                            float phiRot = phi - uTime * rotSpeed;
                            float turb = fbm(vec2(rDisk * 3.5 - uTime * 0.4, phiRot * 3.0));

                            float rNorm = (rDisk - uDiskInner) / (uDiskOuter - uDiskInner);
                            float density = smoothstep(0.0, 0.25, rNorm) * smoothstep(1.0, 0.55, rNorm);
                            density *= (0.6 + 0.5 * turb);

                            // Relativistic Doppler Beaming
                            vec3 vRot = cross(diskNormal, rVec);
                            float beta = dot(normalize(vRot), -rayDir);
                            float doppler = pow(clamp(1.0 + beta * uDopplerStrength, 0.2, 2.8), 2.8);

                            vec3 colGrad = mix(uDiskColorCore, uDiskColorEdge, pow(rNorm, 0.65));
                            vec3 directLight = colGrad * doppler * density * 2.8;
                            if (beta > 0.0) {
                                directLight += vec3(0.1, 0.25, 0.5) * beta * doppler;
                            }
                            diskCol += directLight;
                        }
                    }
                }

                // 3. Duplo Arco Lenteado do Disco (Gargantua Halo Superior e Inferior)
                float haloR = abs(b - rHorizon * 1.35);
                float haloMask = exp(-pow(haloR / 0.38, 2.0));
                if (haloMask > 0.01 && b >= rHorizon * 0.95) {
                    vec3 haloGrad = mix(uDiskColorCore, uDiskColorEdge, 0.45);
                    float haloAngle = atan(toCenterScreen.y, toCenterScreen.x);
                    float haloNoise = fbm(vec2(b * 5.0, haloAngle * 4.0 - uTime * 0.8));
                    
                    // Doppler suave também no halo lenteado
                    float haloDoppler = 1.0 + cos(haloAngle) * 0.4 * uDopplerStrength;
                    diskCol += haloGrad * haloMask * (0.75 + 0.45 * haloNoise) * haloDoppler * 1.6;
                }

                // 4. Anel de Fótons de Einstein (Photon Sphere)
                float photonDist = abs(b - rHorizon * 1.15);
                float photonRing = exp(-pow(photonDist / max(uPhotonRingThickness, 0.005), 2.0)) * uPhotonRingIntensity;
                vec3 photonColor = vec3(1.0, 0.96, 0.88) * photonRing;

                // 5. Composição com o Horizonte de Eventos Schwarzschild
                vec3 finalColor;
                if (b < rHorizon) {
                    // Singularidade: buraco negro puro (com oclusão da porção frontal do disco)
                    finalColor = diskCol;
                } else {
                    finalColor = bgCol + diskCol + photonColor;
                }

                // Tone mapping Reinhard estendido para evitar saturação sólida branca
                finalColor = finalColor / (finalColor + vec3(1.0));
                finalColor = pow(finalColor, vec3(1.0 / 1.15));

                gl_FragColor = vec4(finalColor, 1.0);
            }
        `
    }
};
"""

# ==============================================================================
# 4. js/scene.js
# ==============================================================================
FILES["js/scene.js"] = """import * as THREE from 'three';

export function setupBackgroundScene(scene) {
    const bgGroup = new THREE.Group();
    scene.add(bgGroup);

    // 1. Grid Neon Infinito
    const gridFloor = new THREE.GridHelper(80, 50, 0x00f3ff, 0x1e293b);
    gridFloor.position.y = -6;
    bgGroup.add(gridFloor);

    const gridCeil = new THREE.GridHelper(80, 50, 0xff007f, 0x1e293b);
    gridCeil.position.y = 8;
    bgGroup.add(gridCeil);

    // 2. Anéis Orbitais Neon
    const rings = [];
    const ringConfigs = [
        { radius: 11, tube: 0.04, color: 0x00f3ff, rotSpeed: 0.12, axis: new THREE.Vector3(1, 0.3, 0) },
        { radius: 14, tube: 0.05, color: 0xff007f, rotSpeed: -0.15, axis: new THREE.Vector3(0.2, 1, 0.4) },
        { radius: 17, tube: 0.06, color: 0xffe600, rotSpeed: 0.09, axis: new THREE.Vector3(0.5, 0.2, 1) }
    ];

    ringConfigs.forEach(cfg => {
        const geom = new THREE.TorusGeometry(cfg.radius, cfg.tube, 16, 120);
        const mat = new THREE.MeshBasicMaterial({ color: cfg.color });
        const mesh = new THREE.Mesh(geom, mat);
        bgGroup.add(mesh);
        rings.push({ mesh, ...cfg });
    });

    // 3. 14 Objetos Geométricos Animados Orbitando no Fundo
    const orbiters = [];
    const geometries = [
        new THREE.BoxGeometry(1.2, 1.2, 1.2),
        new THREE.OctahedronGeometry(1.0),
        new THREE.TetrahedronGeometry(1.1),
        new THREE.TorusGeometry(0.8, 0.3, 16, 32),
        new THREE.IcosahedronGeometry(0.9),
        new THREE.DodecahedronGeometry(0.95),
        new THREE.ConeGeometry(0.8, 1.6, 16)
    ];

    const neonColors = [
        0x00f3ff, 0xff007f, 0x39ff14, 0xffe600, 0xff5f00, 0xa855f7, 0x38bdf8
    ];

    for (let i = 0; i < 14; i++) {
        const geom = geometries[i % geometries.length];
        const color = neonColors[i % neonColors.length];
        const mat = new THREE.MeshStandardMaterial({
            color: color,
            emissive: color,
            emissiveIntensity: 0.7,
            roughness: 0.2,
            metalness: 0.8
        });

        const mesh = new THREE.Mesh(geom, mat);
        bgGroup.add(mesh);

        orbiters.push({
            mesh: mesh,
            orbitRadius: 6.5 + (i * 0.75),
            orbitSpeed: (0.35 + (i * 0.05)) * (i % 2 === 0 ? 1 : -1),
            angle: (i / 14) * Math.PI * 2,
            heightOffset: Math.sin(i * 1.3) * 3.2,
            heightSpeed: 1.2 + (i * 0.2),
            rotSpeedX: 0.8 + Math.random() * 0.8,
            rotSpeedY: 0.6 + Math.random() * 0.8
        });
    }

    // 4. Campo de Estrelas Procedural
    const starCount = 1800;
    const starGeometry = new THREE.BufferGeometry();
    const starPositions = new Float32Array(starCount * 3);
    const starColors = new Float32Array(starCount * 3);

    const palette = [
        new THREE.Color(0x00f3ff),
        new THREE.Color(0xff007f),
        new THREE.Color(0xffe600),
        new THREE.Color(0xffffff),
        new THREE.Color(0x7dd3fc)
    ];

    for (let i = 0; i < starCount; i++) {
        const r = 20.0 + Math.random() * 40.0;
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos(2.0 * Math.random() - 1.0);

        starPositions[i * 3]     = r * Math.sin(phi) * Math.cos(theta);
        starPositions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
        starPositions[i * 3 + 2] = r * Math.cos(phi);

        const chosenCol = palette[Math.floor(Math.random() * palette.length)];
        starColors[i * 3]     = chosenCol.r;
        starColors[i * 3 + 1] = chosenCol.g;
        starColors[i * 3 + 2] = chosenCol.b;
    }

    starGeometry.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
    starGeometry.setAttribute('color', new THREE.BufferAttribute(starColors, 3));

    const starMaterial = new THREE.PointsMaterial({
        size: 0.15,
        vertexColors: true,
        transparent: true,
        opacity: 0.85
    });

    const starField = new THREE.Points(starGeometry, starMaterial);
    bgGroup.add(starField);

    // Iluminação
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    bgGroup.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0x00f3ff, 1.2);
    dirLight1.position.set(10, 15, 10);
    bgGroup.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0xff007f, 1.0);
    dirLight2.position.set(-10, -10, -10);
    bgGroup.add(dirLight2);

    return {
        group: bgGroup,
        rings: rings,
        orbiters: orbiters,
        starField: starField
    };
}

export function updateBackgroundScene(bgData, time, delta) {
    bgData.rings.forEach(ring => {
        ring.mesh.rotateOnAxis(ring.axis.clone().normalize(), ring.rotSpeed * delta);
    });

    bgData.orbiters.forEach(item => {
        item.angle += item.orbitSpeed * delta * 0.7;
        const x = Math.cos(item.angle) * item.orbitRadius;
        const z = Math.sin(item.angle) * item.orbitRadius;
        const y = item.heightOffset + Math.sin(time * item.heightSpeed) * 1.2;

        item.mesh.position.set(x, y, z);
        item.mesh.rotation.x += item.rotSpeedX * delta;
        item.mesh.rotation.y += item.rotSpeedY * delta;
    });

    if (bgData.starField) {
        bgData.starField.rotation.y = time * 0.02;
    }
}
"""

# ==============================================================================
# 5. js/main.js
# ==============================================================================
FILES["js/main.js"] = """import * as THREE from 'three';
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
"""

# ==============================================================================
# EXECUÇÃO DO SCRIPT DE GERAÇÃO
# ==============================================================================
print("=" * 60)
print("🚀 GERANDO ESTRUTURA COMPLETA DO SHADER PLAYGROUND")
print("=" * 60)

for filepath, content in FILES.items():
    p = Path(filepath)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  [✔] {filepath}")

print("=" * 60)
print("✨ Projeto configurado com sucesso!")
print("🌐 Para rodar localmente:")
print("   python -m http.server 3000")
print("=" * 60)