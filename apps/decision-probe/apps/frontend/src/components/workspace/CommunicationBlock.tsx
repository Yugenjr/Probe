"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface CommItem {
  channel: "slack" | "email" | "status_page" | string;
  message: string;
}

export interface CommunicationBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      updates?: CommItem[];
    };
  };
}

export function CommunicationBlock({ block }: CommunicationBlockProps) {
  const content = block.content || {};
  const updates = content.updates || [];

  const channelTag = (chan: string) => {
    const base = "text-micro font-bold uppercase tracking-wider px-2 py-0.5 rounded border ";
    switch (chan.toLowerCase()) {
      case "slack":
        return <span className={base + "bg-purple-500/10 text-purple-400 border-purple-500/25"}>Slack Notification</span>;
      case "email":
        return <span className={base + "bg-blue-500/10 text-blue-400 border-blue-500/25"}>Email Broadcast</span>;
      default:
        return <span className={base + "bg-amber-500/10 text-amber-400 border-amber-500/25"}>Status Page Update</span>;
    }
  };

  return (
    <Section title="Response Channel Communications" count={updates.length}>
      <div className="mx-2 rounded-xl border border-border bg-panel/30 p-5 shadow-sm">
        {updates.length > 0 ? (
          <div className="space-y-4 text-[12.5px]">
            {updates.map((item, idx) => (
              <div key={idx} className="border border-border-subtle/50 bg-raised/10 rounded-xl p-4 space-y-2">
                <div className="flex items-center justify-between border-b border-border-subtle/30 pb-2">
                  {channelTag(item.channel)}
                  <span className="text-[10px] text-fg-muted font-medium">Broadcast ready</span>
                </div>
                <p className="text-foreground/90 whitespace-pre-wrap leading-relaxed mt-2 font-mono text-[12px] bg-raised/20 border border-border-subtle/25 rounded-xl p-3.5">
                  {item.message}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-[12.5px] text-fg-muted italic">No communication notifications drafted.</p>
        )}
      </div>
    </Section>
  );
}
