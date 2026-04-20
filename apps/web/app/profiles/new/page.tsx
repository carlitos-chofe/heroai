"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { createProfile, AvatarConfig } from "@/lib/api";
import AvatarBuilder from "@/components/AvatarBuilder";
import styles from "./page.module.css";

const DEFAULT_AVATAR: AvatarConfig = {
  hair: "short",
  hair_color: "brown",
  eye_color: "brown",
  skin: "medium",
  clothing: "astronaut suit",
};

export default function NewProfilePage() {
  const router = useRouter();
  const { getToken } = useAuth();

  const [name, setName] = useState("");
  const [age, setAge] = useState<number>(8);
  const [interests, setInterests] = useState("");
  const [avatar, setAvatar] = useState<AvatarConfig>(DEFAULT_AVATAR);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (age < 4 || age > 12) {
      setError("La edad debe estar entre 4 y 12 años.");
      return;
    }
    setLoading(true);
    try {
      const token = await getToken();
      if (!token) throw new Error("No session");
      await createProfile(token, {
        name: name.trim(),
        age,
        initial_interests: interests.trim(),
        avatar_config: avatar,
      });
      router.push("/dashboard");
    } catch (e: unknown) {
      const err = e as { detail?: { detail?: { message?: string } } };
      setError(err?.detail?.detail?.message || "Error al crear el perfil.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className={styles.main}>
      <div className={styles.card}>
        <h1 className={styles.title}>Crear nuevo perfil</h1>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label className={styles.label}>Nombre del niño o niña</label>
            <input
              className={styles.input}
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ej: Luna"
              required
              maxLength={120}
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Edad (4-12 años)</label>
            <input
              className={styles.input}
              type="number"
              value={age}
              onChange={(e) => setAge(Number(e.target.value))}
              min={4}
              max={12}
              required
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Intereses e intereses</label>
            <input
              className={styles.input}
              type="text"
              value={interests}
              onChange={(e) => setInterests(e.target.value)}
              placeholder="Ej: dinosaurios, espacio, cuentos de hadas"
              required
            />
          </div>

          <AvatarBuilder value={avatar} onChange={setAvatar} />

          {error && <p className={styles.error}>{error}</p>}

          <div className={styles.actions}>
            <button type="button" className={styles.btnSecondary} onClick={() => router.back()}>
              Cancelar
            </button>
            <button type="submit" className={styles.btnPrimary} disabled={loading}>
              {loading ? "Creando..." : "Crear perfil"}
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}
