/**
 * Home hero: an animated particle wave (Three.js), loaded as a separate chunk only on
 * capable devices (see canRenderHero in main.js). The CSS glow behind it is the fallback.
 * Rendering pauses when the hero is off-screen or the tab is hidden.
 */
import {
  AdditiveBlending,
  BufferAttribute,
  BufferGeometry,
  Color,
  PerspectiveCamera,
  Points,
  Scene,
  ShaderMaterial,
  WebGLRenderer,
} from "three";

const COLS = 140;
const ROWS = 70;
const SPACING = 0.22;

const vertexShader = /* glsl */ `
  uniform float uTime;
  uniform vec2 uPointer;
  attribute float aMix;
  varying float vMix;
  varying float vHeight;

  void main() {
    vec3 p = position;
    float wave = sin(p.x * 0.55 + uTime * 0.9) * 0.45
               + cos(p.z * 0.75 + uTime * 0.6) * 0.35
               + sin((p.x + p.z) * 0.3 + uTime * 0.4) * 0.25;
    // Gentle bulge following the pointer.
    float d = distance(p.xz, uPointer * vec2(12.0, 6.0));
    wave += exp(-d * d * 0.05) * 0.9;
    p.y += wave;
    vMix = aMix;
    vHeight = wave;
    vec4 mv = modelViewMatrix * vec4(p, 1.0);
    gl_PointSize = (2.2 + wave * 1.2) * (12.0 / -mv.z);
    gl_Position = projectionMatrix * mv;
  }
`;

const fragmentShader = /* glsl */ `
  uniform vec3 uCyan;
  uniform vec3 uViolet;
  varying float vMix;
  varying float vHeight;

  void main() {
    float r = length(gl_PointCoord - 0.5);
    if (r > 0.5) discard;
    vec3 color = mix(uViolet, uCyan, vMix);
    float alpha = smoothstep(0.5, 0.0, r) * (0.35 + clamp(vHeight, 0.0, 1.0) * 0.6);
    gl_FragColor = vec4(color, alpha);
  }
`;

export function initHero3D(container) {
  const renderer = new WebGLRenderer({ antialias: false, alpha: true, powerPreference: "low-power" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
  renderer.domElement.setAttribute("aria-hidden", "true");
  container.append(renderer.domElement);

  const scene = new Scene();
  const camera = new PerspectiveCamera(55, 1, 0.1, 100);
  camera.position.set(0, 4.2, 9);
  camera.lookAt(0, 0, 0);

  const count = COLS * ROWS;
  const positions = new Float32Array(count * 3);
  const mixes = new Float32Array(count);
  for (let i = 0; i < count; i += 1) {
    const col = i % COLS;
    const row = Math.floor(i / COLS);
    positions[i * 3] = (col - COLS / 2) * SPACING;
    positions[i * 3 + 2] = (row - ROWS / 2) * SPACING;
    mixes[i] = col / COLS;
  }
  const geometry = new BufferGeometry();
  geometry.setAttribute("position", new BufferAttribute(positions, 3));
  geometry.setAttribute("aMix", new BufferAttribute(mixes, 1));

  const uniforms = {
    uTime: { value: 0 },
    uPointer: { value: [0, 0] },
    uCyan: { value: new Color("#22e3ff") },
    uViolet: { value: new Color("#8b5cf6") },
  };
  const material = new ShaderMaterial({
    uniforms,
    vertexShader,
    fragmentShader,
    transparent: true,
    depthWrite: false,
    blending: AdditiveBlending,
  });
  scene.add(new Points(geometry, material));

  const resize = () => {
    const { clientWidth: width, clientHeight: height } = container;
    renderer.setSize(width, height, false);
    camera.aspect = width / Math.max(height, 1);
    camera.updateProjectionMatrix();
  };
  resize();
  new ResizeObserver(resize).observe(container);

  // Pointer target, eased toward each frame.
  const target = [0, 0];
  window.addEventListener(
    "pointermove",
    (event) => {
      target[0] = (event.clientX / window.innerWidth) * 2 - 1;
      target[1] = (event.clientY / window.innerHeight) * 2 - 1;
    },
    { passive: true },
  );

  let visible = true;
  let frame = 0;
  let last = performance.now();
  const loop = (now) => {
    frame = 0;
    if (!visible || document.hidden) return;
    uniforms.uTime.value += Math.min((now - last) / 1000, 0.05);
    last = now;
    const pointer = uniforms.uPointer.value;
    pointer[0] += (target[0] - pointer[0]) * 0.05;
    pointer[1] += (target[1] - pointer[1]) * 0.05;
    renderer.render(scene, camera);
    frame = requestAnimationFrame(loop);
  };
  const start = () => {
    if (!frame && visible && !document.hidden) {
      last = performance.now();
      frame = requestAnimationFrame(loop);
    }
  };

  new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    start();
  }).observe(container);
  document.addEventListener("visibilitychange", start);

  start();
  container.classList.add("is-ready"); // fades the canvas in over the CSS fallback
}
