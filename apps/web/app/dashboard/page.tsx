"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import Link from "next/link";
import { getProfiles, getStories, Profile, StoryListItem } from "@/lib/api";
import ProfileCard from "@/components/ProfileCard";
import StoryCard from "@/components/StoryCard";
import styles from "./page.module.css";

export default function DashboardPage() {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [stories, setStories] = useState<StoryListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoaded || !isSignedIn) return;

    const load = async () => {
      try {
        const token = await getToken();
        if (!token) return;
        const [p, s] = await Promise.all([
          getProfiles(token),
          getStories(token),
        ]);
        setProfiles(p);
        setStories(s);
      } catch (e: unknown) {
        setError("Error cargando datos. Verifica tu conexión.");
        console.error(e);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [isLoaded, isSignedIn, getToken]);

  if (!isLoaded || loading) {
    return (
      <div className={styles.centered}>
        <div className={styles.spinner} />
        <p>Cargando...</p>
      </div>
    );
  }

  if (error) {
    return <div className={styles.centered}><p className={styles.error}>{error}</p></div>;
  }

  return (
    <main className={styles.main}>
      <header className={styles.header}>
        <h1 className={styles.title}>Hero Adventure AI</h1>
        <div className={styles.headerActions}>
          <Link href="/profiles/new" className={styles.btnPrimary}>
            + Nuevo Perfil
          </Link>
          <Link href="/stories/new" className={styles.btnSecondary}>
            + Nueva Historia
          </Link>
        </div>
      </header>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Perfiles</h2>
        {profiles.length === 0 ? (
          <div className={styles.empty}>
            <p>No tienes perfiles aún.</p>
            <Link href="/profiles/new" className={styles.btnPrimary}>
              Crear primer perfil
            </Link>
          </div>
        ) : (
          <div className={styles.grid}>
            {profiles.map((p) => (
              <ProfileCard key={p.id} profile={p} />
            ))}
          </div>
        )}
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Biblioteca Magica</h2>
        {stories.length === 0 ? (
          <div className={styles.empty}>
            <p>No tienes historias aún.</p>
            {profiles.length > 0 && (
              <Link href="/stories/new" className={styles.btnPrimary}>
                Crear primera historia
              </Link>
            )}
          </div>
        ) : (
          <div className={styles.storyGrid}>
            {stories.map((s) => (
              <StoryCard key={s.id} story={s} />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
