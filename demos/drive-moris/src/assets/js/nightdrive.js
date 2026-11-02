/**
 * "Night drive": the hero road, drawn entirely in a shader (no photo, no library, ~5 KB).
 * Lane dashes rush towards you, sugarcane lines the road, sodium streetlights pass overhead
 * and the headlights light the tarmac. The mouse steers a little; scrolling speeds the car up.
 * The static SVG road underneath stays as the fallback; rendering pauses off-screen and
 * gives up below ~30 fps.
 */
const VERTEX = `
attribute vec2 aPos;
varying vec2 vUv;
void main() { vUv = aPos * 0.5 + 0.5; gl_Position = vec4(aPos, 0.0, 1.0); }`;

const FRAGMENT = `
precision mediump float;
uniform vec2 uRes;
uniform float uTime, uTravel, uSteer, uFade;
varying vec2 vUv;

const float H = 0.44;          // horizon height on screen
const float K = 0.3;           // camera height x focal length
const float SPACING = 14.0;    // distance between streetlights
const float CX = 0.63;         // the road sits right of centre, beside the headline
const vec3 SODIUM = vec3(1.0, 0.62, 0.16);

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }

// The road gently bends left and right as you drive.
float bend(float z) { return sin(uTravel * 0.018 + z * 0.012) * z * z * 0.003; }

void main() {
  vec2 uv = vUv;
  float a = uRes.x / uRes.y;
  float steer = uSteer * 0.7;
  vec3 col;

  // Where the road meets the horizon (moves with the bend and the steering).
  float vanish = CX + (-steer + bend(60.0)) / (a * 60.0);

  if (uv.y > H) {
    // Night sky: deep blue overhead, a sodium haze over the island at the horizon.
    float t = (uv.y - H) / (1.0 - H);
    col = mix(vec3(0.075, 0.09, 0.12), vec3(0.03, 0.035, 0.05), smoothstep(0.0, 0.7, t));
    col += SODIUM * 0.22 * exp(-t * 9.0) * (0.6 + 0.4 * exp(-abs(uv.x - vanish) * 3.0));
    float star = step(0.9975, hash(floor(uv * vec2(380.0 * a, 380.0)))) * smoothstep(0.15, 0.6, t);
    col += star * 0.55;
    // Sugarcane silhouette along the horizon, with a gap where the road runs out.
    float cane = H + 0.03 + 0.008 * sin(uv.x * 80.0) + 0.005 * sin(uv.x * 233.0 + 1.3) + 0.004 * hash(vec2(floor(uv.x * 400.0), 0.0));
    float gap = smoothstep(0.004, 0.016, abs(uv.x - vanish));
    if (uv.y < cane && gap > 0.5) col = vec3(0.035, 0.045, 0.035);
  } else {
    float p = H - uv.y;
    float z = K / p;                         // depth in front of the car
    float x = (uv.x - CX) * a * z + steer - bend(z);
    float zz = z + uTravel;                  // distance along the road

    float absx = abs(x);
    // Tarmac with a little grain.
    col = vec3(0.09, 0.095, 0.1) + (hash(floor(vec2(x * 24.0, zz * 24.0))) - 0.5) * 0.025;
    // Verges and sugarcane fields beyond them.
    if (absx > 1.9) {
      float rows = 0.5 + 0.5 * sin(x * 9.0 + hash(vec2(floor(zz * 2.0), sign(x))) * 2.0);
      col = mix(vec3(0.05, 0.06, 0.045), vec3(0.08, 0.11, 0.06), rows * 0.6);
      col *= smoothstep(1.9, 2.3, absx) * 0.6 + 0.4;
    }
    // Solid edge lines and the dashed centre line.
    float fw = 0.012 * z;
    col = mix(col, vec3(0.86), (1.0 - smoothstep(0.0, 0.04 + fw, abs(absx - 1.7))) * 0.75);
    float dash = step(fract(zz * 0.22), 0.42);
    col = mix(col, vec3(0.93, 0.92, 0.88), (1.0 - smoothstep(0.0, 0.035 + fw, absx)) * dash * 0.9);

    // Pools of sodium light under each streetlight (they stand on the left verge).
    float dz = mod(zz, SPACING);
    dz = min(dz, SPACING - dz);
    float pool = exp(-dz * dz * 0.07 - (x + 1.6) * (x + 1.6) * 0.18);
    col += SODIUM * pool * 0.55;
    // Headlights: bright close to the car, fading with distance.
    float beam = exp(-z * 0.09) * (1.0 - smoothstep(1.2, 3.4, abs(x - steer * 0.2)));
    col += vec3(1.0, 0.93, 0.8) * beam * 0.42;
    // Distance haze.
    col = mix(col, vec3(0.1, 0.09, 0.08) + SODIUM * 0.08, smoothstep(8.0, 70.0, z));
  }

  // Streetlight heads passing overhead.
  for (int i = 0; i < 7; i++) {
    float zi = SPACING * float(i + 1) - mod(uTravel, SPACING);
    if (zi < 1.2) continue;
    float lx = CX + (-1.75 - steer + bend(zi)) / (a * zi);
    float ly = H + 0.75 * K / zi;
    vec2 d = vec2((uv.x - lx) * a, uv.y - ly);
    float r = length(d);
    float fade = 1.0 / (1.0 + zi * 0.05);
    col += SODIUM * (exp(-r * r * 9000.0) * 1.6 + exp(-r * 22.0) * 0.28) * fade;
  }

  // Vignette and fade-in.
  vec2 v = (uv - 0.5) * vec2(1.1, 1.0);
  col *= 1.0 - 0.45 * smoothstep(0.35, 0.95, length(v));
  gl_FragColor = vec4(col * uFade, uFade);
}`;

function compile(gl, type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(shader));
  return shader;
}

export function initNightDrive(container) {
  const canvas = document.createElement("canvas");
  canvas.className = "absolute inset-0 size-full";
  canvas.setAttribute("aria-hidden", "true");
  const gl = canvas.getContext("webgl", { antialias: false, alpha: true, premultipliedAlpha: true });
  if (!gl) return;

  const program = gl.createProgram();
  gl.attachShader(program, compile(gl, gl.VERTEX_SHADER, VERTEX));
  gl.attachShader(program, compile(gl, gl.FRAGMENT_SHADER, FRAGMENT));
  gl.linkProgram(program);
  gl.useProgram(program);

  gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  const aPos = gl.getAttribLocation(program, "aPos");
  gl.enableVertexAttribArray(aPos);
  gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

  const u = (name) => gl.getUniformLocation(program, name);
  const uniforms = { res: u("uRes"), time: u("uTime"), travel: u("uTravel"), steer: u("uSteer"), fade: u("uFade") };
  container.append(canvas);

  const resize = () => {
    // Rendered at reduced resolution: the shader is soft by nature and this keeps it light.
    const ratio = Math.min(window.devicePixelRatio, 1) * 0.75;
    canvas.width = Math.round(container.clientWidth * ratio);
    canvas.height = Math.round(container.clientHeight * ratio);
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.uniform2f(uniforms.res, canvas.width, canvas.height);
  };
  new ResizeObserver(resize).observe(container);
  resize();

  const state = { steer: 0, steerTarget: 0, speed: 9, boost: 0, travel: 0, fade: 0 };
  const hero = container.closest("[data-hero]");
  hero?.addEventListener("pointermove", (event) => {
    state.steerTarget = (event.clientX / window.innerWidth - 0.5) * 1.6;
  });
  hero?.addEventListener("pointerleave", () => {
    state.steerTarget = 0;
  });
  // Scrolling presses the accelerator; the car coasts back to cruising speed.
  let lastY = window.scrollY;
  window.addEventListener(
    "scroll",
    () => {
      state.boost = Math.min(60, state.boost + Math.abs(window.scrollY - lastY) * 0.25);
      lastY = window.scrollY;
    },
    { passive: true },
  );

  let visible = true;
  let frame = 0;
  let last = 0;
  let begin = 0;
  let stopped = false;
  const probe = { frames: 0, start: 0 };
  const giveUp = () => {
    stopped = true;
    canvas.style.transition = "opacity 1s";
    canvas.style.opacity = "0";
    setTimeout(() => canvas.remove(), 1100);
  };
  const render = (now) => {
    frame = 0;
    if (stopped || !visible || document.hidden) return;
    if (probe.frames === 0) probe.start = now;
    if (++probe.frames === 60 && (now - probe.start) / 59 > 33) {
      giveUp();
      return;
    }
    const dt = Math.min(0.05, (now - (last || now)) / 1000);
    last = now;
    state.boost *= 0.95;
    state.travel += (state.speed + state.boost) * dt;
    state.steer += (state.steerTarget - state.steer) * 0.04;
    state.fade = Math.min(1, (now - begin) / 1400);
    gl.uniform1f(uniforms.time, (now - begin) / 1000);
    gl.uniform1f(uniforms.travel, state.travel);
    gl.uniform1f(uniforms.steer, state.steer);
    gl.uniform1f(uniforms.fade, state.fade);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
    frame = requestAnimationFrame(render);
  };
  const start = () => {
    if (stopped || frame || !visible || document.hidden) return;
    if (!begin) begin = performance.now();
    last = 0;
    frame = requestAnimationFrame(render);
  };
  new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    start();
  }).observe(container);
  document.addEventListener("visibilitychange", start);
  start();
}
