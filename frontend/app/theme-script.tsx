
"use client";

import { useEffect } from "react";

export function ThemeScript() {
  useEffect(() => {
    
    const enforceDarkMode = () => {
      const html = document.documentElement;
      html.classList.add("dark");
      html.classList.remove("light");
      html.setAttribute("data-theme", "dark");
      
      // Set color-scheme meta tag
      let meta = document.querySelector('meta[name="color-scheme"]');
      if (!meta) {
        meta = document.createElement("meta");
        meta.setAttribute("name", "color-scheme");
        document.head.appendChild(meta);
      }
      meta.setAttribute("content", "dark");

      // Prevent theme switching via MutationObserver
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.type === "attributes" && mutation.attributeName === "class") {
            const target = mutation.target as HTMLElement;
            if (target.classList.contains("light")) {
              target.classList.remove("light");
              target.classList.add("dark");
            }
            if (!target.classList.contains("dark")) {
              target.classList.add("dark");
            }
          }
        });
      });

      observer.observe(html, {
        attributes: true,
        attributeFilter: ["class"],
      });

      return () => observer.disconnect();
    };

    const cleanup = enforceDarkMode();

    // Re-enforce on any potential theme changes
    const interval = setInterval(() => {
      enforceDarkMode();
    }, 1000);

    return () => {
      clearInterval(interval);
      if (cleanup) cleanup();
    };
  }, []);

  return null;
}

