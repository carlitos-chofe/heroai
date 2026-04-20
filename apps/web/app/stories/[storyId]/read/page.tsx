"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { getStory, StoryDetail, assetUrl } from "@/lib/api";
import ReactionBar from "@/components/ReactionBar";
import styles from "./page.module.css";

export default function ReadPage() {
  const params = useParams();
  const router = useRouter();
  const { getToken } = useAuth();
  const storyId = params.storyId as string;

  const [story, setStory] = useState<StoryDetail | null>(null);
  const [currentPanel, setCurrentPanel] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      const token = await getToken();
      if (!token) return;
      try {
        const s = await getStory(token, storyId);
        if (s.status !== "completed") {
          router.push(`/stories/${storyId}/progress`);
          return;
        }
        // Sort panels by order
        s.panels = s.panels.sort((a, b) => a.panel_order - b.panel_order);
        setStory(s);
      } catch {
        setError("No se pudo cargar la historia.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [storyId, getToken, router]);

  if (loading) {
    return (
      <div className={styles.centered}>
        <div className={styles.spinner} />
        <p>Abriendo historia...</p>
      </div>
    );
  }

  if (error || !story || story.panels.length === 0) {
    return (
      <div className={styles.centered}>
        <p className={styles.error}>{error || "Historia no disponible."}</p>
        <button className={styles.btn} onClick={() => router.push("/dashboard")}>
          Volver al dashboard
        </button>
      </div>
    );
  }

  const panel = story.panels[currentPanel];
  const isFirst = currentPanel === 0;
  const isLast = currentPanel === story.panels.length - 1;

  return (
    <div className={styles.reader}>
      {/* Top bar */}
      <div className={styles.topBar}>
        <button className={styles.closeBtn} onClick={() => router.push("/dashboard")}>
          ← Biblioteca
        </button>
        <div className={styles.storyInfo}>
          <span className={styles.storyTitle}>{story.title || "Historia"}</span>
          <span className={styles.pageIndicator}>
            {currentPanel + 1} / {story.panels.length}
          </span>
        </div>
      </div>

      {/* Main reading area */}
      <div className={styles.content}>
        {/* Image area — 65% height */}
        <div className={styles.imageArea}>
          {panel.image_url ? (
            <img
              src={assetUrl(panel.image_url)}
              alt={`Panel ${panel.panel_order}`}
              className={styles.panelImage}
            />
          ) : (
            <div className={styles.imagePlaceholder}>
              <span>Ilustracion no disponible</span>
            </div>
          )}
        </div>

        {/* Text area — 35% height */}
        <div className={styles.textArea}>
          <div className={styles.narrative}>
            <p>{panel.narrative_text}</p>
          </div>
          {panel.dialogue && (
            <div className={styles.dialogueBubble}>
              <div className={styles.bubbleTail} />
              <p className={styles.dialogueText}>{panel.dialogue}</p>
            </div>
          )}

          {/* Reactions for completed stories */}
          <div className={styles.reactionSection}>
            <ReactionBar storyId={storyId} panelOrder={panel.panel_order} />
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className={styles.nav}>
        <button
          className={`${styles.navBtn} ${isFirst ? styles.navBtnDisabled : ""}`}
          onClick={() => setCurrentPanel((p) => Math.max(0, p - 1))}
          disabled={isFirst}
        >
          ← Anterior
        </button>

        {/* Page dots */}
        <div className={styles.dots}>
          {story.panels.map((_, i) => (
            <button
              key={i}
              className={`${styles.dot} ${i === currentPanel ? styles.dotActive : ""}`}
              onClick={() => setCurrentPanel(i)}
              aria-label={`Ir a panel ${i + 1}`}
            />
          ))}
        </div>

        <button
          className={`${styles.navBtn} ${isLast ? styles.navBtnDisabled : ""}`}
          onClick={() => setCurrentPanel((p) => Math.min(story.panels.length - 1, p + 1))}
          disabled={isLast}
        >
          Siguiente →
        </button>
      </div>
    </div>
  );
}
