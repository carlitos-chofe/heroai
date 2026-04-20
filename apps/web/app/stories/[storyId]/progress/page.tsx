"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { getStoryStatus, StoryStatus } from "@/lib/api";
import styles from "./page.module.css";

const STATUS_MESSAGES: Record<string, string> = {
  pending: "Preparando tu historia...",
  scripting: "Generando el guion con inteligencia artificial...",
  script_ready: "Guion listo para revision.",
  approved: "Guion aprobado. Preparando ilustraciones...",
  generating_images: "Generando ilustraciones...",
  completed: "Historia completada.",
  failed: "Ocurrio un error.",
};

export default function ProgressPage() {
  const params = useParams();
  const router = useRouter();
  const { getToken } = useAuth();
  const storyId = params.storyId as string;

  const [storyStatus, setStoryStatus] = useState<StoryStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  const checkStatus = useCallback(async () => {
    const token = await getToken();
    if (!token) return;
    try {
      const s = await getStoryStatus(token, storyId);
      setStoryStatus(s);

      if (s.status === "script_ready") {
        router.push(`/stories/${storyId}/script`);
      } else if (s.status === "completed") {
        router.push(`/stories/${storyId}/read`);
      } else if (s.status === "failed") {
        setError(s.error_message || "La historia falló en procesarse.");
      }
    } catch {
      setError("Error consultando el estado de la historia.");
    }
  }, [storyId, getToken, router]);

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 4000);
    return () => clearInterval(interval);
  }, [checkStatus]);

  const progress = storyStatus
    ? storyStatus.status === "generating_images"
      ? Math.round((storyStatus.generated_panels / storyStatus.total_panels) * 100)
      : storyStatus.status === "completed"
      ? 100
      : storyStatus.status === "scripting"
      ? 30
      : storyStatus.status === "script_ready" || storyStatus.status === "approved"
      ? 50
      : 10
    : 0;

  return (
    <main className={styles.main}>
      <div className={styles.card}>
        <div className={styles.icon}>
          {error ? "❌" : storyStatus?.status === "completed" ? "✅" : "✨"}
        </div>
        <h1 className={styles.title}>
          {error
            ? "Error en la historia"
            : storyStatus
            ? STATUS_MESSAGES[storyStatus.status] || storyStatus.status
            : "Iniciando..."}
        </h1>

        {!error && storyStatus && (
          <>
            <div className={styles.progressContainer}>
              <div className={styles.progressBar} style={{ width: `${progress}%` }} />
            </div>
            <p className={styles.progressText}>{progress}%</p>

            {storyStatus.status === "generating_images" && (
              <p className={styles.detail}>
                Ilustracion {storyStatus.generated_panels} de {storyStatus.total_panels}
              </p>
            )}
          </>
        )}

        {error && (
          <div className={styles.errorBox}>
            <p className={styles.errorText}>{error}</p>
            <button className={styles.btn} onClick={() => router.push("/dashboard")}>
              Volver al dashboard
            </button>
          </div>
        )}

        {!error && (
          <p className={styles.hint}>
            Esta pagina se actualiza automaticamente cada 4 segundos.
          </p>
        )}
      </div>
    </main>
  );
}
