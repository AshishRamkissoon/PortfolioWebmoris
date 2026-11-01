/**
 * Hero "living lagoon": the hero photo re-drawn with WebGL so the water gently moves,
 * and ripples spread from the mouse. Plain WebGL (no library), about 3 KB.
 * The CSS photo underneath stays as the fallback; rendering pauses off-screen.
 */
const VERTEX = `
attribute vec2 aPos;
varying vec2 vUv;
void main() { vUv = aPos * 0.5 + 0.5; gl_Position = vec4(aPos, 0.0, 1.0); }`;

const FRAGMENT = `
precision highp float;
uniform sampler2D uTex;
uniform vec2 uRes, uImg, uMouse;
uniform float uTime, uStrength;
varying vec2 vUv;

vec2 cover(vec2 uv) {
  float rs = uRes.x / uRes.y, ri = uImg.x / uImg.y;
  vec2 s = rs > ri ? vec2(1.0, ri / rs) : vec2(rs / ri, 1.0);
  return (uv - 0.5) * s + 0.5;
}

void main() {
  // Slow settle-in zoom, like a Ken Burns move.
  float zoom = 1.0 + 0.1 * exp(-uTime * 0.12);
  vec2 uv = (vUv - 0.5) / zoom + 0.5;

  // Water moves in the lower part of the photo (the lagoon).
  float water = smoothstep(0.62, 0.3, uv.y);
  vec2 d = vec2(
    sin(uv.y * 70.0 + uTime * 1.7) * 0.0016 + sin(uv.x * 22.0 + uTime * 0.9) * 0.0011,
    cos(uv.x * 45.0 + uTime * 1.3) * 0.0014
  ) * water;

  // Ripples spreading from the pointer.
  vec2 m = uv - uMouse;
  m.x *= uRes.x / uRes.y;
  float dist = length(m);
  float ring = sin(dist * 70.0 - uTime * 7.0) * exp(-dist * 7.0) * uStrength;
  d += (m / max(dist, 0.0001)) * ring * 0.007;

  gl_FragColor = texture2D(uTex, cover(uv + d));
}`;

function compile(gl, type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(shader));
  return shader;
}

export function initRipple(container) {
  const photo = document.querySelector("[data-hero-photo] img");
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

  // One triangle that covers the screen.
  gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  const aPos = gl.getAttribLocation(program, "aPos");
  gl.enableVertexAttribArray(aPos);
  gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

  const u = (name) => gl.getUniformLocation(program, name);
  const uniforms = { res: u("uRes"), img: u("uImg"), mouse: u("uMouse"), time: u("uTime"), strength: u("uStrength") };

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

  const mouse = { x: 0.5, y: 0.3, strength: 0, target: 0 };
  container.closest("[data-hero]")?.addEventListener("pointermove", (event) => {
    const box = container.getBoundingClientRect();
    mouse.x = (event.clientX - box.left) / box.width;
    mouse.y = 1 - (event.clientY - box.top) / box.height;
    mouse.target = 1;
  });

  let visible = true;
  let frame = 0;
  let begin = 0;
  let stopped = false;
  // Watchdog: if the first second averages under ~30 fps, fade out and keep the plain photo.
  const probe = { frames: 0, start: 0 };
  const giveUp = () => {
    stopped = true;
    canvas.classList.replace("opacity-100", "opacity-0");
    photo.closest("[data-hero-photo]").classList.add("motion-safe:animate-kenburns");
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
    mouse.target *= 0.97; // ripples fade when the mouse rests
    gl.uniform1f(uniforms.time, (now - begin) / 1000);
    gl.uniform2f(uniforms.mouse, mouse.x, mouse.y);
    gl.uniform1f(uniforms.strength, mouse.strength);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
    frame = requestAnimationFrame(render);
  };
  const start = () => {
    if (stopped || frame || !visible || document.hidden || !canvas.isConnected) return;
    if (!begin) {
      begin = performance.now();
      requestAnimationFrame(() => {
        canvas.classList.replace("opacity-0", "opacity-100");
        photo.closest("[data-hero-photo]").classList.remove("motion-safe:animate-kenburns");
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
