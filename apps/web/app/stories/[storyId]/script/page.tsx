"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { getStoryScript, approveStory, regenerateStoryScript, deleteStory, StoryScript } from "@/lib/api";
import styles from "./page.module.css";

export default function ScriptPage() {
  const params = useParams();
  const router = useRouter();
  const { getToken } = useAuth();
  const storyId = params.storyId as string;

  const [script, setScript] = useState<StoryScript | null>(null);
  const [loading, setLoading] = useState(true);
  const [approving, setApproving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      const token = await getToken();
      if (!token) return;
      try {
        const s = await getStoryScript(token, storyId);
        setScript(s);
      } catch {
        setError("No se pudo cargar el guion. Puede que todavía esté generándose.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [storyId, getToken]);

  async function handleApprove() {
    setApproving(true);
    try {
      const token = await getToken();
      if (!token) throw new Error("No session");
      await approveStory(token, storyId);
      router.push(`/stories/${storyId}/progress`);
    } catch {
      setError("Error al aprobar el guion.");
      setApproving(false);
    }
  }

  async function handleRegenerate() {
    setRegenerating(true);
    try {
      const token = await getToken();
      if (!token) throw new Error("No session");
      await regenerateStoryScript(token, storyId);
      router.push(`/stories/${storyId}/progress`);
    } catch {
      setError("Error al solicitar una nueva versión.");
      setRegenerating(false);
    }
  }

  async function handleDelete() {
    if (!window.confirm("¿Estás seguro de que quieres eliminar esta historia? Esta acción no se puede deshacer.")) {
      return;
    }
    setDeleting(true);
    try {
      const token = await getToken();
      if (!token) throw new Error("No session");
      await deleteStory(token, storyId);
      router.push("/dashboard");
    } catch {
      setError("Error al eliminar la historia.");
      setDeleting(false);
    }
  }

  if (loading) {
    return (
      <div className={styles.centered}>
        <div className={styles.spinner} />
        <p>Cargando guion...</p>
      </div>
    );
  }

  if (error || !script) {
    return (
      <div className={styles.centered}>
        <p className={styles.error}>{error || "Guion no disponible."}</p>
        <button className={styles.btnSecondary} onClick={() => router.back()}>Volver</button>
      </div>
    );
  }

  return (
    <main className={styles.main}>
      <div className={styles.header}>
        <button className={styles.backBtn} onClick={() => router.push("/dashboard")}>
          ← Dashboard
        </button>
        <div className={styles.headerRight}>
          <span className={styles.langBadge}>{script.language_target}</span>
        </div>
      </div>

      <h1 className={styles.title}>{script.title || "Historia sin título"}</h1>
      <p className={styles.subtitle}>Revisa el guion antes de aprobar. Una vez aprobado se generarán las ilustraciones.</p>

      <div className={styles.panels}>
        {script.panels.map((panel) => (
          <div key={panel.panel_order} className={styles.panel}>
            <div className={styles.panelHeader}>
              <span className={styles.panelNum}>Panel {panel.panel_order}</span>
            </div>
            <div className={styles.panelBody}>
              <div className={styles.panelSection}>
                <span className={styles.sectionLabel}>Escena visual</span>
                <p className={styles.sectionText}>{panel.scene_description}</p>
              </div>
              <div className={styles.panelSection}>
                <span className={styles.sectionLabel}>Narración</span>
                <p className={styles.sectionText}>{panel.narrative_text}</p>
              </div>
              <div className={styles.panelSection}>
                <span className={styles.sectionLabel}>Dialogo</span>
                <p className={`${styles.sectionText} ${styles.dialogue}`}>{panel.dialogue}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className={styles.footer}>
        <div className={styles.footerLeft}>
          <button
            className={`${styles.btnSecondary} ${styles.btnDanger}`}
            onClick={handleDelete}
            disabled={approving || deleting || regenerating}
          >
            {deleting ? "Eliminando..." : "Eliminar"}
          </button>
        </div>
        <div className={styles.footerRight}>
          <button
            className={styles.btnSecondary}
            onClick={handleRegenerate}
            disabled={approving || deleting || regenerating}
          >
            {regenerating ? "Generando..." : "Nueva versión"}
          </button>
          <button
            className={styles.btnApprove}
            onClick={handleApprove}
            disabled={approving || deleting || regenerating}
          >
            {approving ? "Aprobando..." : "Aprobar y generar ilustraciones"}
          </button>
        </div>
      </div>
    </main>
  );
}
