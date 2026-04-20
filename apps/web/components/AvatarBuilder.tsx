"use client";

import { AvatarConfig } from "@/lib/api";
import styles from "./AvatarBuilder.module.css";

const HAIR_OPTIONS = ["short", "long", "curly", "braids", "afro", "bald"];
const HAIR_COLOR_OPTIONS = ["black", "brown", "blonde", "red", "gray", "white"];
const EYE_COLOR_OPTIONS = ["brown", "black", "blue", "green", "hazel", "gray"];
const SKIN_OPTIONS = ["light", "medium", "tan", "dark", "deep"];
const CLOTHING_OPTIONS = [
  "astronaut suit",
  "superhero cape",
  "doctor coat",
  "scientist lab coat",
  "chef uniform",
  "artist smock",
  "explorer outfit",
  "school uniform",
];

interface AvatarBuilderProps {
  value: AvatarConfig;
  onChange: (config: AvatarConfig) => void;
}

function SelectField({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: string[];
  onChange: (v: string) => void;
}) {
  return (
    <div className={styles.field}>
      <label className={styles.label}>{label}</label>
      <select
        className={styles.select}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {opt.charAt(0).toUpperCase() + opt.slice(1)}
          </option>
        ))}
      </select>
    </div>
  );
}

export default function AvatarBuilder({ value, onChange }: AvatarBuilderProps) {
  function update(key: keyof AvatarConfig, val: string) {
    onChange({ ...value, [key]: val });
  }

  return (
    <div className={styles.container}>
      <h3 className={styles.title}>Apariencia del personaje</h3>
      <div className={styles.grid}>
        <SelectField
          label="Cabello"
          value={value.hair}
          options={HAIR_OPTIONS}
          onChange={(v) => update("hair", v)}
        />
        <SelectField
          label="Color de cabello"
          value={value.hair_color}
          options={HAIR_COLOR_OPTIONS}
          onChange={(v) => update("hair_color", v)}
        />
        <SelectField
          label="Color de ojos"
          value={value.eye_color}
          options={EYE_COLOR_OPTIONS}
          onChange={(v) => update("eye_color", v)}
        />
        <SelectField
          label="Tono de piel"
          value={value.skin}
          options={SKIN_OPTIONS}
          onChange={(v) => update("skin", v)}
        />
        <SelectField
          label="Ropa / traje"
          value={value.clothing}
          options={CLOTHING_OPTIONS}
          onChange={(v) => update("clothing", v)}
        />
      </div>
    </div>
  );
}
