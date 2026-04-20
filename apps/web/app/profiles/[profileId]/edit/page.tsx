"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { getProfiles, updateProfile, AvatarConfig, Profile } from "@/lib/api";
import AvatarBuilder from "@/components/AvatarBuilder";
import styles from "../../../profiles/new/page.module.css";

export default function EditProfilePage() {
  const router = useRouter();
  const params = useParams();
  const { getToken } = useAuth();
  const profileId = params.profileId as string;

  const [profile, setProfile] = useState<Profile | null>(null);
  const [name, setName] = useState("");
  const [age, setAge] = useState<number>(8);
  const [interests, setInterests] = useState("");
  const [avatar, setAvatar] = useState<AvatarConfig>({
    hair: "short",
    hair_color: "brown",
    eye_color: "brown",
    skin: "medium",
    clothing: "astronaut suit",
  });
  const [loading, setLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      const token = await getToken();
      if (!token) return;
      try {
        const profiles = await getProfiles(token);
        const found = profiles.find((p) => p.id === profileId);
        if (found) {
          setProfile(found);
          setName(found.name);
          setAge(found.age);
          setInterests(found.initial_interests);
          setAvatar(found.avatar_config);
        }
      } catch {
        setError("No se pudo cargar el perfil.");
      } finally {
        setLoadingData(false);
      }
    };
    load();
  }, [profileId, getToken]);

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
      await updateProfile(token, profileId, {
        name: name.trim(),
        age,
        initial_interests: interests.trim(),
        avatar_config: avatar,
      });
      router.push("/dashboard");
    } catch {
      setError("Error al actualizar el perfil.");
    } finally {
      setLoading(false);
    }
  }

  if (loadingData) return <div style={{ padding: "3rem", textAlign: "center" }}>Cargando...</div>;
  if (!profile) return <div style={{ padding: "3rem", textAlign: "center" }}>Perfil no encontrado.</div>;

  return (
    <main className={styles.main}>
      <div className={styles.card}>
        <h1 className={styles.title}>Editar perfil: {profile.name}</h1>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label className={styles.label}>Nombre</label>
            <input
              className={styles.input}
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              maxLength={120}
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Edad (4-12)</label>
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
            <label className={styles.label}>Intereses</label>
            <input
              className={styles.input}
              type="text"
              value={interests}
              onChange={(e) => setInterests(e.target.value)}
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
              {loading ? "Guardando..." : "Guardar cambios"}
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}
