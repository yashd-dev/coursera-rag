import "@fontsource-variable/public-sans";
import "@fontsource-variable/jetbrains-mono";
import "./styles/globals.css";
import { createRoot } from "react-dom/client";
import { HomeDemo } from "./up/apps/docs/components/pages/home/demo";
createRoot(document.getElementById("root")!).render(
  <div className="bg-background text-foreground flex min-h-screen flex-col font-sans">
    <main className="mx-auto w-full max-w-[1440px] px-4 py-8 md:px-24">
      <HomeDemo />
    </main>
  </div>,
);
