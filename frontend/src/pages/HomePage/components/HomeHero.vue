<script setup lang="ts">
import { Scale } from 'lucide-vue-next';
</script>

<template>
  <section class="hero">
    <div class="hero-icon">
      <Scale :size="42" />
    </div>
    <h1>JusTRT6 Search</h1>
    <p>Busca semantica para precedentes trabalhistas do TRT6 com foco em jornada de trabalho.</p>
  </section>
</template>

<style scoped>
.hero {
  text-align: center;
  margin-bottom: 1.2rem;
}

.hero-icon {
  width: 78px;
  height: 78px;
  margin: 0 auto 0.8rem;
  border-radius: 24px;
  border: 1px solid var(--line);
  color: var(--brand);
  display: grid;
  place-items: center;
  background: linear-gradient(140deg, rgba(230, 240, 255, 0.9), rgba(220, 248, 243, 0.65));
}

h1 {
  margin: 0;
  font-family: var(--font-display);
  color: var(--text-strong);
  font-size: clamp(1.7rem, 2.6vw, 2.4rem);
  letter-spacing: -0.03em;
}

p {
  margin: 0.55rem auto 0;
  max-width: 700px;
  color: var(--text-muted);
}
</style>
