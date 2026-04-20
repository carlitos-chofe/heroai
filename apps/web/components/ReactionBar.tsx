"use client";

import { useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { postFeedback } from "@/lib/api";
import styles from "./ReactionBar.module.css";

interface ReactionBarProps {
  storyId: string;
  panelOrder: number;
}

const REACTIONS = [
  { type: "love", label: "Me encanto", emoji: "❤️" },
  { type: "funny", label: "Divertido", emoji: "😄" },
  { type: "scary", label: "Me dio miedo", emoji: "😨" },
];

export default function ReactionBar({ storyId, panelOrder }: ReactionBarProps) {
  const { getToken } = useAuth();
  const [selected, setSelected] = useState<string | null>(null);
  const [sending, setSending] = useState(false);

  async function handleReaction(reactionType: string) {
    if (selected || sending) return;
    setSending(true);
    try {
      const token = await getToken();
      if (!token) return;
      await postFeedback(token, storyId, {
        panel_order: panelOrder,
        reaction_type: reactionType,
      });
      setSelected(reactionType);
    } catch (e) {
      console.error("Error sending feedback:", e);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className={styles.bar}>
      <span className={styles.label}>¿Como te parecio esta pagina?</span>
      <div className={styles.buttons}>
        {REACTIONS.map((r) => (
          <button
            key={r.type}
            className={`${styles.btn} ${selected === r.type ? styles.selected : ""} ${selected && selected !== r.type ? styles.faded : ""}`}
            onClick={() => handleReaction(r.type)}
            disabled={!!selected || sending}
            title={r.label}
          >
            <span className={styles.emoji}>{r.emoji}</span>
            <span className={styles.reactionLabel}>{r.label}</span>
          </button>
        ))}
      </div>
      {selected && (
        <p className={styles.thanks}>Gracias por tu reaccion</p>
      )}
    </div>
  );
}
