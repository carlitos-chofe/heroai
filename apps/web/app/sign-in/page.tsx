import { SignIn } from "@clerk/nextjs";
import styles from "./page.module.css";

export default function SignInPage() {
  return (
    <div className={styles.container}>
      <div className={styles.hero}>
        <h1 className={styles.title}>Hero Adventure AI</h1>
        <p className={styles.subtitle}>Crea cómics educativos personalizados para tus niños</p>
      </div>
      <SignIn routing="hash" />
    </div>
  );
}
