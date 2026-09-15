<template>
  <article class="base-card">
    <slot />
  </article>
</template>

<style scoped>
.base-card {
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  border: 1px solid var(--line);
  box-shadow: var(--shadow-card);
  padding: 1rem;
}
</style>
