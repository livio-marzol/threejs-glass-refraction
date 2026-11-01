// Repositório Central de Shaders em GLSL (Shader Playground)

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
