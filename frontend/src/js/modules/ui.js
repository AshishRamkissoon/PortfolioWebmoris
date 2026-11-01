/** Small Alpine components used by the layout (header menu, tabs). */

export function registerUiComponents(Alpine) {
  // Mobile navigation: x-data="menu".
  Alpine.data("menu", () => ({
    open: false,
    toggle() {
      this.open = !this.open;
    },
    close() {
      this.open = false;
    },
    get expanded() {
      return String(this.open);
    },
  }));

  // Desktop / mobile screenshot tabs: x-data="tabs" data-initial-tab="desktop".
  Alpine.data("tabs", () => ({
    tab: "",
    init() {
      this.tab = this.$el.dataset.initialTab || "desktop";
    },
    select(name) {
      this.tab = name;
    },
    get isDesktop() {
      return this.tab === "desktop";
    },
    get isMobile() {
      return this.tab === "mobile";
    },
  }));
}
