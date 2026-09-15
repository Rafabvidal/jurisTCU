<script setup lang="ts">
import AppNavbar from './AppNavbar.vue';
</script>

<template>
  <div class="app-shell">
    <AppNavbar />
    <main class="content-wrap">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
}

.content-wrap {
  width: min(1220px, 100% - 2.5rem);
  margin: 1.4rem auto 2.2rem;
}

@media (max-width: 700px) {
  .content-wrap {
    width: calc(100% - 1.4rem);
  }
}
</style>
