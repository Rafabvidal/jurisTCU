<script setup lang="ts">
import BaseCard from '@/shared/components/ui/BaseCard.vue'
import { useSettingsStore } from '@/stores/settings'
import { Bell, Globe2, Scale, ShieldCheck } from 'lucide-vue-next'

const settings = useSettingsStore()
</script>

<template>
  <section class="page-stack">
    <header>
      <h1>Configuracoes</h1>
      <p>Preferencias essenciais para experiencia juridica personalizada.</p>
    </header>

    <BaseCard>
      <h2><Globe2 :size="16" /> Idioma</h2>
      <select v-model="settings.language">
        <option value="pt-BR">Portugues (Brasil)</option>
        <option value="en-US">English (US)</option>
      </select>
    </BaseCard>

    <BaseCard>
      <h2><Scale :size="16" /> Métrica de Similaridade</h2>
      <p class="description-text">Selecione o algoritmo para cálculo de similaridade entre petições e processos.</p>
      <select v-model="settings.metrica">
        <option value="cosseno">Cosseno (Padrão)</option>
        <option value="euclidiana">Euclidiana</option>
        <option value="manhattan">Manhattan</option>
        <option value="jaccard">Jaccard (Texto)</option>
        <option value="levenshtein">Levenshtein (Texto)</option>
      </select>
    </BaseCard>

    <BaseCard>
      <h2><Bell :size="16" /> Notificacoes</h2>
      <label>
        <input v-model="settings.notifications" type="checkbox" />
        Receber alertas de mudanca jurisprudencial nas buscas salvas.
      </label>
    </BaseCard>

    <BaseCard>
      <h2><ShieldCheck :size="16" /> Privacidade visual</h2>
      <label>
        <input v-model="settings.highContrast" type="checkbox" />
        Ativar contraste elevado para leitura de documentos extensos.
      </label>
    </BaseCard>
  </section>
</template>

<style scoped>
.page-stack {
  display: grid;
  gap: 0.95rem;
}

h1,
h2 {
  margin: 0;
  font-family: var(--font-display);
  color: var(--text-strong);
}

header p {
  margin: 0.3rem 0 0;
  color: var(--text-muted);
}

h2 {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 1rem;
}

.description-text {
  margin: 0.25rem 0 0;
  font-size: 0.86rem;
  color: var(--text-muted);
}

select {
  margin-top: 0.65rem;
  min-width: 240px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  min-height: 40px;
  padding: 0 0.75rem;
}

label {
  margin-top: 0.65rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-body);
}
</style>

