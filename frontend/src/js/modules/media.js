/**
 * Alpine components for dialogs, video playback and screenshot viewing.
 * Templates only call these methods/getters: no inline JS, so the strict CSP build works.
 */

function withAutoplay(src) {
  return src + (src.includes("?") ? "&" : "?") + "autoplay=1";
}

// Only these sources may be played (defence in depth: the server already validates them).
const EMBED_ORIGINS = ["https://www.youtube-nocookie.com/embed/", "https://player.vimeo.com/video/"];
const isAllowedEmbed = (src) => EMBED_ORIGINS.some((origin) => src.startsWith(origin));
const isAllowedFile = (src) => src.startsWith("/media/");

function buildPlayer({ src, kind, title }) {
  if (kind === "embed" && isAllowedEmbed(src)) {
    const frame = document.createElement("iframe");
    frame.src = withAutoplay(src);
    frame.title = title;
    frame.allow = "autoplay; fullscreen; picture-in-picture";
    frame.allowFullscreen = true;
    frame.referrerPolicy = "strict-origin-when-cross-origin";
    frame.className = "size-full";
    return frame;
  }
  if (kind === "file" && isAllowedFile(src)) {
    const video = document.createElement("video");
    Object.assign(video, { src, controls: true, autoplay: true, playsInline: true });
    video.className = "size-full";
    return video;
  }
  return null;
}

/** Shared open/close behaviour: lock page scroll and return focus to the trigger. */
export const dialog = {
  open: false,
  _trigger: null,

  _openDialog() {
    this._trigger = document.activeElement;
    this.open = true;
    document.documentElement.style.overflow = "hidden";
    this.$nextTick(() => this.$refs.closeButton?.focus());
  },

  /** Keep Tab / Shift+Tab inside the open dialog (bind with @keydown.tab="trap($event)"). */
  trap(event) {
    const focusable = [
      ...event.currentTarget.querySelectorAll(
        'a[href], button:not([disabled]), input:not([type="hidden"]), select, textarea, iframe, [tabindex]:not([tabindex="-1"])',
      ),
    ].filter((el) => el.offsetParent !== null);
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  },

  close() {
    if (!this.open) return;
    this.open = false;
    document.documentElement.style.overflow = "";
    this._trigger?.focus();
  },
};

export function registerMediaComponents(Alpine) {
  // Listens for `open-video` events: { src, kind: "embed" | "file", title }.
  Alpine.data("videoModal", () => ({
    ...dialog,
    title: "",

    // The CSP-safe Alpine build won't bind attributes on <iframe>, so the player
    // element is built here instead (and removed on close, which stops playback).
    show({ src, kind, title }) {
      const player = buildPlayer({ src: src || "", kind: kind || "embed", title: title || "" });
      if (!player) return;
      this.title = title || "";
      this.$refs.player.replaceChildren(player);
      this._openDialog();
    },

    close() {
      this.$refs.player?.replaceChildren();
      dialog.close.call(this);
    },

    /** Open from a trigger's data-src / data-kind / data-title attributes. */
    openFrom(el) {
      this.show(el.dataset);
    },

  }));

  // Generic dialog: x-data="modal", @click="openDialog()", x-ref="closeButton".
  Alpine.data("modal", () => ({
    ...dialog,
    openDialog() {
      this._openDialog();
    },
  }));

  // Collects its [data-lightbox-item] links; arrows/Escape navigate while open.
  Alpine.data("lightbox", () => ({
    ...dialog,
    items: [],
    index: 0,

    init() {
      this.items = [...this.$el.querySelectorAll("[data-lightbox-item]")].map((link) => ({
        src: link.href,
        caption: link.dataset.caption || "",
      }));
    },

    get current() {
      return this.items[this.index] || { src: "", caption: "" };
    },

    get counter() {
      return `${this.index + 1} / ${this.items.length}`;
    },

    get hasMany() {
      return this.items.length > 1;
    },

    show(index) {
      this.index = index;
      this._openDialog();
    },

    next() {
      if (this.open) this.index = (this.index + 1) % this.items.length;
    },

    prev() {
      if (this.open) this.index = (this.index - 1 + this.items.length) % this.items.length;
    },
  }));
}
