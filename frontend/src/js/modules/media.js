/** Alpine components for video playback and screenshot viewing. */

function withAutoplay(src) {
  return src + (src.includes("?") ? "&" : "?") + "autoplay=1";
}

/** Shared open/close behaviour: lock page scroll and return focus to the trigger. */
const dialog = {
  open: false,
  _trigger: null,

  _openDialog() {
    this._trigger = document.activeElement;
    this.open = true;
    document.documentElement.style.overflow = "hidden";
    this.$nextTick(() => this.$refs.closeButton?.focus());
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
    src: "",
    kind: "embed",
    title: "",

    get embedSrc() {
      return this.src ? withAutoplay(this.src) : "";
    },

    show({ src, kind, title }) {
      if (!src) return;
      Object.assign(this, { src, kind: kind || "embed", title: title || "" });
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
