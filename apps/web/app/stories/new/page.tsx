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

import { Suspense } from "react";
import NewStoryForm from "./NewStoryForm";

export default function NewStoryPage() {
  return (
    <Suspense fallback={<div style={{ padding: "3rem", textAlign: "center" }}>Cargando página...</div>}>
      <NewStoryForm />
    </Suspense>
  );
}
