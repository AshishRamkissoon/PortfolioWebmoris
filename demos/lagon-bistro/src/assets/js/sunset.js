/**
 * Hero "golden hour": the sunset photo re-drawn with WebGL. The sea shimmers and glitters,
 * ripples spread from the mouse and a warm lantern glow follows it. Plain WebGL, about 4 KB.
 * The photo underneath stays as the fallback; rendering pauses off-screen and gives up below ~30 fps.
 */
const VERTEX = `
attribute vec2 aPos;
varying vec2 vUv;
void main() { vUv = aPos * 0.5 + 0.5; gl_Position = vec4(aPos, 0.0, 1.0); }`;

const FRAGMENT = `
precision highp float;
uniform sampler2D uTex;
uniform vec2 uRes, uImg, uMouse;
uniform float uTime, uStrength, uGlow, uHorizon, uShore;
varying vec2 vUv;

vec2 cover(vec2 uv) {
  float rs = uRes.x / uRes.y, ri = uImg.x / uImg.y;
  vec2 s = rs > ri ? vec2(1.0, ri / rs) : vec2(rs / ri, 1.0);
  return (uv - 0.5) * s + 0.5;
}

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }

void main() {
  float zoom = 1.0 + 0.12 * exp(-uTime * 0.14);
  vec2 uv = (vUv - 0.5) / zoom + 0.5;
  vec2 tuv = cover(uv);

  // The sea: a band between the horizon and the shore (in photo coordinates, 0 = bottom).
  float sea = smoothstep(uHorizon + 0.01, uHorizon - 0.03, tuv.y) * smoothstep(uShore - 0.04, uShore + 0.02, tuv.y);
  // Warm air above the sea wobbles very slightly.
  float haze = smoothstep(uHorizon - 0.02, uHorizon + 0.25, tuv.y) * 0.0006;

  vec2 d = vec2(
    sin(tuv.y * 160.0 + uTime * 2.2) * 0.0018 + sin(tuv.x * 30.0 + uTime * 1.1) * 0.0012,
    cos(tuv.x * 60.0 + uTime * 1.6) * 0.0009
  ) * sea;
  d.x += sin(tuv.y * 40.0 + uTime * 1.3) * haze;
  // A sea breeze: the palms and clouds sway a little, more towards the top of the picture.
  float breeze = smoothstep(uHorizon + 0.05, 1.0, tuv.y);
  d.x += (sin(uTime * 0.9 + tuv.y * 4.0) + 0.5 * sin(uTime * 2.1 + tuv.y * 9.0 + tuv.x * 3.0)) * 0.0035 * breeze;

  // Ripples spreading from the pointer.
  vec2 m = uv - uMouse;
  m.x *= uRes.x / uRes.y;
  float dist = length(m);
  float ring = sin(dist * 60.0 - uTime * 6.0) * exp(-dist * 6.0) * uStrength;
  d += (m / max(dist, 0.0001)) * ring * 0.006;

  vec3 col = texture2D(uTex, cover(uv + d)).rgb;

  // Golden glitter where light hits the water.
  float lum = dot(col, vec3(0.299, 0.587, 0.114));
  vec2 cell = floor(tuv * vec2(420.0, 220.0));
  float spark = smoothstep(0.982, 1.0, hash(cell + floor(uTime * 6.0))) * sea * smoothstep(0.25, 0.7, lum);
  col += vec3(1.0, 0.82, 0.55) * spark * 1.6;

  // A warm lantern glow that follows the pointer.
  col += vec3(1.0, 0.5, 0.22) * exp(-dist * 5.0) * 0.22 * uGlow;

  // Gentle warm grade and vignette.
  col *= vec3(1.04, 0.99, 0.94);
  col *= 1.0 - 0.35 * smoothstep(0.45, 1.05, length((vUv - 0.5) * vec2(1.2, 1.0)));
  gl_FragColor = vec4(col, 1.0);
}`;

function compile(gl, type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(shader));
  return shader;
}

export function initSunset(container) {
  const holder = document.querySelector("[data-hero-photo]");
  const photo = holder?.querySelector("img");
  if (!photo) return;

  const canvas = document.createElement("canvas");
  canvas.className = "size-full opacity-0 transition-opacity duration-[1500ms]";
  canvas.setAttribute("aria-hidden", "true");
  const gl = canvas.getContext("webgl", { antialias: false, premultipliedAlpha: false });
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
  const uniforms = {
    res: u("uRes"), img: u("uImg"), mouse: u("uMouse"), time: u("uTime"),
    strength: u("uStrength"), glow: u("uGlow"), horizon: u("uHorizon"), shore: u("uShore"),
  };
  gl.uniform1f(uniforms.horizon, parseFloat(container.dataset.horizon) || 0.5);
  gl.uniform1f(uniforms.shore, parseFloat(container.dataset.shore) || 0.25);

  const image = new Image();
  image.decoding = "async";
  image.src = photo.currentSrc || photo.src; // same origin, already cached
  image.decode().then(() => {
    const texture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, image);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.uniform2f(uniforms.img, image.naturalWidth, image.naturalHeight);
    container.append(canvas);
    start();
  });

  const resize = () => {
    const ratio = Math.min(window.devicePixelRatio, 1.5);
    canvas.width = container.clientWidth * ratio;
    canvas.height = container.clientHeight * ratio;
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.uniform2f(uniforms.res, canvas.width, canvas.height);
  };
  new ResizeObserver(resize).observe(container);

  const mouse = { x: 0.5, y: 0.4, strength: 0, target: 0, glow: 0, glowTarget: 0 };
  const hero = container.closest("[data-hero]");
  hero?.addEventListener("pointermove", (event) => {
    const box = container.getBoundingClientRect();
    mouse.x = (event.clientX - box.left) / box.width;
    mouse.y = 1 - (event.clientY - box.top) / box.height;
    mouse.target = 1;
    mouse.glowTarget = 1;
  });
  hero?.addEventListener("pointerleave", () => {
    mouse.glowTarget = 0;
  });

  let visible = true;
  let frame = 0;
  let begin = 0;
  let stopped = false;
  const probe = { frames: 0, start: 0 };
  const giveUp = () => {
    stopped = true;
    canvas.classList.replace("opacity-100", "opacity-0");
    holder.classList.add("motion-safe:animate-kenburns");
    setTimeout(() => canvas.remove(), 1600);
  };
  const render = (now) => {
    frame = 0;
    if (stopped || !visible || document.hidden) return;
    if (probe.frames === 0) probe.start = now;
    if (++probe.frames === 60 && (now - probe.start) / 59 > 33) {
      giveUp();
      return;
    }
    mouse.strength += (mouse.target - mouse.strength) * 0.06;
    mouse.target *= 0.97;
    mouse.glow += (mouse.glowTarget - mouse.glow) * 0.05;
    gl.uniform1f(uniforms.time, (now - begin) / 1000);
    gl.uniform2f(uniforms.mouse, mouse.x, mouse.y);
    gl.uniform1f(uniforms.strength, mouse.strength);
    gl.uniform1f(uniforms.glow, mouse.glow);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
    frame = requestAnimationFrame(render);
  };
  const start = () => {
    if (stopped || frame || !visible || document.hidden || !canvas.isConnected) return;
    if (!begin) {
      begin = performance.now();
      requestAnimationFrame(() => {
        canvas.classList.replace("opacity-0", "opacity-100");
        holder.classList.remove("motion-safe:animate-kenburns");
      });
    }
    frame = requestAnimationFrame(render);
  };

  new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    start();
  }).observe(container);
  document.addEventListener("visibilitychange", start);
}
