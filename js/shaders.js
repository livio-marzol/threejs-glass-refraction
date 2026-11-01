/**
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
