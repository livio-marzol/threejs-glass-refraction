import * as THREE from 'three';

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
