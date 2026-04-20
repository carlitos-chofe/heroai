"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { getProfiles, createStory, Profile, LanguageTarget } from "@/lib/api";
import styles from "./page.module.css";

const LANG_OPTIONS: { value: LanguageTarget; label: string; desc: string }[] = [
  { value: "es", label: "Español", desc: "Todo el texto en español" },
  { value: "en", label: "English", desc: "All text in English" },
  { value: "mixed_es_en", label: "Español + English", desc: "Narración en español, diálogo bilingüe" },
];

export default function NewStoryPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { getToken } = useAuth();

  const defaultProfile = searchParams.get("profile") || "";

  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [profileId, setProfileId] = useState(defaultProfile);
  const [content, setContent] = useState("");
  const [language, setLanguage] = useState<LanguageTarget>("es");
  const [loading, setLoading] = useState(false);
  const [loadingProfiles, setLoadingProfiles] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      const token = await getToken();
      if (!token) return;
      try {
        const p = await getProfiles(token);
        setProfiles(p);
        if (!defaultProfile && p.length > 0) setProfileId(p[0].id);
      } catch {
        setError("No se pudieron cargar los perfiles.");
      } finally {
        setLoadingProfiles(false);
      }
    };
    load();
  }, [getToken, defaultProfile]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (content.trim().length < 200) {
      setError("El texto debe tener al menos 200 caracteres.");
      return;
    }
    if (content.length > 20000) {
      setError("El texto no puede superar los 20,000 caracteres.");
      return;
    }
    if (!profileId) {
      setError("Selecciona un perfil.");
      return;
    }
    setLoading(true);
    try {
      const token = await getToken();
      if (!token) throw new Error("No session");
      const result = await createStory(token, {
        profile_id: profileId,
        content: content.trim(),
        language_target: language,
      });
      router.push(`/stories/${result.story_id}/progress`);
    } catch (e: unknown) {
      const err = e as { detail?: { detail?: { message?: string } } };
      setError(err?.detail?.detail?.message || "Error al crear la historia.");
    } finally {
      setLoading(false);
    }
  }

  if (loadingProfiles) return <div style={{ padding: "3rem", textAlign: "center" }}>Cargando perfiles...</div>;

  if (profiles.length === 0) {
    return (
      <main className={styles.main}>
        <div className={styles.card}>
          <h1 className={styles.title}>Nueva historia</h1>
          <p style={{ color: "var(--color-text-muted)", marginBottom: "1rem" }}>
            Necesitas crear un perfil infantil antes de crear una historia.
          </p>
          <button className={styles.btnPrimary} onClick={() => router.push("/profiles/new")}>
            Crear perfil
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className={styles.main}>
      <div className={styles.card}>
        <h1 className={styles.title}>Nueva historia</h1>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label className={styles.label}>Perfil del niño</label>
            <select
              className={styles.select}
              value={profileId}
              onChange={(e) => setProfileId(e.target.value)}
              required
            >
              {profiles.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.age} años)
                </option>
              ))}
            </select>
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Idioma de la historia</label>
            <div className={styles.langOptions}>
              {LANG_OPTIONS.map((opt) => (
                <label key={opt.value} className={`${styles.langOption} ${language === opt.value ? styles.langSelected : ""}`}>
                  <input
                    type="radio"
                    name="language"
                    value={opt.value}
                    checked={language === opt.value}
                    onChange={() => setLanguage(opt.value)}
                    style={{ display: "none" }}
                  />
                  <span className={styles.langLabel}>{opt.label}</span>
                  <span className={styles.langDesc}>{opt.desc}</span>
                </label>
              ))}
            </div>
          </div>

          <div className={styles.field}>
            <label className={styles.label}>
              Texto educativo fuente{" "}
              <span className={styles.hint}>({content.length}/20000 caracteres, mínimo 200)</span>
            </label>
            <textarea
              className={styles.textarea}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Pega aquí el texto educativo que quieres convertir en historia..."
              rows={12}
              required
            />
          </div>

          {error && <p className={styles.error}>{error}</p>}

          <div className={styles.actions}>
            <button type="button" className={styles.btnSecondary} onClick={() => router.back()}>
              Cancelar
            </button>
            <button type="submit" className={styles.btnPrimary} disabled={loading}>
              {loading ? "Generando guion..." : "Crear historia"}
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}
