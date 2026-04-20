import Link from "next/link";
import { StoryListItem } from "@/lib/api";
import styles from "./StoryCard.module.css";

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  pending: { label: "Pendiente", color: "#f59e0b" },
  scripting: { label: "Generando guion...", color: "#6c47ff" },
  script_ready: { label: "Guion listo", color: "#22c55e" },
  approved: { label: "Aprobado", color: "#22c55e" },
  generating_images: { label: "Generando ilustraciones...", color: "#6c47ff" },
  completed: { label: "Completado", color: "#22c55e" },
  failed: { label: "Error", color: "#ef4444" },
};

const LANG_LABELS: Record<string, string> = {
  es: "Español",
  en: "English",
  mixed_es_en: "Español + English",
};

function storyHref(story: StoryListItem): string {
  switch (story.status) {
    case "script_ready":
      return `/stories/${story.id}/script`;
    case "approved":
    case "generating_images":
      return `/stories/${story.id}/progress`;
    case "completed":
      return `/stories/${story.id}/read`;
    default:
      return `/stories/${story.id}/progress`;
  }
}

export default function StoryCard({ story }: { story: StoryListItem }) {
  const statusInfo = STATUS_LABELS[story.status] || { label: story.status, color: "#6b7280" };
  const link = storyHref(story);

  return (
    <Link href={link} className={styles.card}>
      <div className={styles.top}>
        <h3 className={styles.title}>{story.title || "Historia en progreso..."}</h3>
        <span className={styles.lang}>{LANG_LABELS[story.language_target] || story.language_target}</span>
      </div>
      <div className={styles.bottom}>
        <span
          className={styles.status}
          style={{ color: statusInfo.color }}
        >
          {statusInfo.label}
        </span>
        <span className={styles.date}>
          {new Date(story.created_at).toLocaleDateString("es", {
            day: "2-digit",
            month: "short",
            year: "numeric",
          })}
        </span>
      </div>
    </Link>
  );
}
