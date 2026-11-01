/**
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
