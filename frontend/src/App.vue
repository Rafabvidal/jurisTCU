<script setup lang="ts">
import AppShell from '@/shared/components/layout/AppShell.vue';
import { useAuthStore } from '@/stores/auth';

// Revalida o token persistido (se houver) ao montar a aplicação.
useAuthStore().initialize()
</script>

<template>
  <AppShell>
    <RouterView v-slot="{ Component }">
      <Transition name="page" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
  </AppShell>
</template>
