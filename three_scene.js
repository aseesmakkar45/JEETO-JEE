document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('hero-canvas');
    if (!canvas) return;

    // SCENE SETUP
    const scene = new THREE.Scene();

    // Camera
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 5;

    // Renderer
    const renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        alpha: true, // transparent background
        antialias: true
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    // MOUSE INTERACTION
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    const windowHalfX = window.innerWidth / 2;
    const windowHalfY = window.innerHeight / 2;

    document.addEventListener('mousemove', (event) => {
        mouseX = (event.clientX - windowHalfX);
        mouseY = (event.clientY - windowHalfY);
    });

    // OBJECTS

    // 1. MAIN PLANET (Dark, rocky)
    const planetGeometry = new THREE.SphereGeometry(2, 64, 64);

    // Create a noise-like texture procedurally (simplified) or use standard material with bump
    // For a "Quantum" look: Dark material, rim light (fresnel)
    const planetMaterial = new THREE.MeshStandardMaterial({
        color: 0x121212, // Dark base
        roughness: 0.8,
        metalness: 0.2,
        flatShading: false,
    });

    const planet = new THREE.Mesh(planetGeometry, planetMaterial);
    scene.add(planet);

    // 2. ATMOSPHERE / GLOW (Lime Green #D9F96A)
    // Using a slightly larger sphere with a custom shader or additive blending
    const atmosphereGeometry = new THREE.SphereGeometry(2.2, 64, 64);
    const atmosphereMaterial = new THREE.MeshBasicMaterial({
        color: 0xD9F96A,
        transparent: true,
        opacity: 0.15,
        side: THREE.BackSide // Render on inside to create glow effect or just behind?
        // Actually for a rim glow, standard BackSide approach is common in Three.js demos
    });

    // Better glow approach: Sprite or specific shader. 
    // Let's stick to a simple transparent shell for now to avoid complex shader code errors.
    const atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
    scene.add(atmosphere);

    // 3. FLOATING ROCKS (Asteroids)
    const rockGeometry = new THREE.IcosahedronGeometry(0.1, 0); // Low poly ish
    const rockMaterial = new THREE.MeshPhongMaterial({
        color: 0x333333,
        shininess: 10,
        flatShading: true
    });

    const rocks = [];
    const rockCount = 50;

    for (let i = 0; i < rockCount; i++) {
        const rock = new THREE.Mesh(rockGeometry, rockMaterial);

        // Random position spread
        const u = Math.random();
        const v = Math.random();
        const theta = 2 * Math.PI * u;
        const phi = Math.acos(2 * v - 1);
        const radius = 3 + Math.random() * 2; // Distance from center

        const x = radius * Math.sin(phi) * Math.cos(theta);
        const y = radius * Math.sin(phi) * Math.sin(theta);
        const z = radius * Math.cos(phi);

        rock.position.set(x, y, z);

        // Random rotation
        rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);

        // Random scale
        const scale = 0.5 + Math.random() * 0.8;
        rock.scale.set(scale, scale, scale);

        rock.userData = {
            rotationSpeed: (Math.random() - 0.5) * 0.02,
            orbitSpeed: (Math.random() * 0.005) + 0.001,
            orbitAxis: new THREE.Vector3(Math.random(), Math.random(), Math.random()).normalize()
        };

        scene.add(rock);
        rocks.push(rock);
    }

    // LIGHTING

    // Ambient Light (Simulate space ambient)
    const ambientLight = new THREE.AmbientLight(0x404040, 2); // Soft white light
    scene.add(ambientLight);

    // Directional Light (Sun/Star source)
    const directionalLight = new THREE.DirectionalLight(0xffffff, 2);
    directionalLight.position.set(5, 3, 5);
    scene.add(directionalLight);

    // Rim Light (Lime Green Accent)
    const rimLight = new THREE.PointLight(0xD9F96A, 3, 10);
    rimLight.position.set(-2, 2, -2); // Backlight
    scene.add(rimLight);


    // ANIMATION LOOP
    const animate = () => {
        requestAnimationFrame(animate);

        targetX = mouseX * 0.001;
        targetY = mouseY * 0.001;

        // Rotate Planet
        planet.rotation.y += 0.002;
        planet.rotation.x += 0.0005;

        // Mouse interaction eases
        planet.rotation.y += 0.05 * (targetX - planet.rotation.y);
        planet.rotation.x += 0.05 * (targetY - planet.rotation.x);

        // Animate Atmosphere
        atmosphere.rotation.y += 0.002;

        // Animate Rocks
        rocks.forEach(rock => {
            rock.rotation.x += rock.userData.rotationSpeed;
            rock.rotation.y += rock.userData.rotationSpeed;

            // Simple orbit logic (rotate position around center)
            rock.position.applyAxisAngle(rock.userData.orbitAxis, rock.userData.orbitSpeed);
        });

        renderer.render(scene, camera);
    };

    animate();


    // HANDLE RESIZE
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

});
