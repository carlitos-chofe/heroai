import Link from "next/link";
import { Profile } from "@/lib/api";
import styles from "./ProfileCard.module.css";

function avatarEmoji(avatar: Profile["avatar_config"]): string {
  // Simple visual hint from avatar config
  const clothing = avatar.clothing.toLowerCase();
  if (clothing.includes("astronaut")) return "👨‍🚀";
  if (clothing.includes("doctor")) return "👩‍⚕️";
  if (clothing.includes("scientist")) return "👩‍🔬";
  if (clothing.includes("chef")) return "👨‍🍳";
  if (clothing.includes("artist")) return "👩‍🎨";
  if (clothing.includes("superhero")) return "🦸";
  return "🧒";
}

export default function ProfileCard({ profile }: { profile: Profile }) {
  return (
    <div className={styles.card}>
      <div className={styles.avatar}>{avatarEmoji(profile.avatar_config)}</div>
      <div className={styles.info}>
        <h3 className={styles.name}>{profile.name}</h3>
        <p className={styles.age}>{profile.age} años</p>
        <p className={styles.interests}>{profile.initial_interests}</p>
      </div>
      <div className={styles.actions}>
        <Link href={`/profiles/${profile.id}/edit`} className={styles.editBtn}>
          Editar
        </Link>
        <Link href={`/stories/new?profile=${profile.id}`} className={styles.storyBtn}>
          Nueva historia
        </Link>
      </div>
    </div>
  );
}
