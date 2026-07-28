import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Explorer } from "@/components/dv/Explorer";
import { Workspace } from "@/components/dv/Workspace";
import { CommandCenter } from "@/components/dv/CommandCenter";

export const Route = createFileRoute("/")({
  component: DecisionVerse,
});

function DecisionVerse() {
  const [selected, setSelected] = useState("INC-2043");
  return (
    <div className="dark flex h-screen w-screen overflow-hidden bg-background text-foreground">
      <div className="hidden md:block shrink-0 border-r border-border-subtle" style={{ width: 240 }}>
        <Explorer selectedId={selected} onSelect={setSelected} />
      </div>
      <div className="min-w-0 flex-1">
        <Workspace />
      </div>
      <div className="hidden lg:block shrink-0 border-l border-border-subtle" style={{ width: 380 }}>
        <CommandCenter />
      </div>
    </div>
  );
}
