<script setup lang="ts">
import { LoaderCircle, Search } from 'lucide-vue-next';
import { ref, watch } from 'vue';

const props = withDefaults(
  defineProps<{ modelValue: string; loading?: boolean }>(),
  { loading: false },
)
const emit = defineEmits<{
  'update:modelValue': [string]
  submit: [string]
}>()

const localValue = ref(props.modelValue)

watch(
  () => props.modelValue,
  (value) => {
    localValue.value = value
  },
)

function updateValue(value: string) {
  localValue.value = value
  emit('update:modelValue', value)
}

function onSubmit() {
  const trimmed = localValue.value.trim()
  if (!trimmed) return
  emit('submit', trimmed)
}
</script>

<template>
  <div class="search-shell">
    <label class="search-input-wrap">
      <Search :size="20" class="search-icon" />
      <input
        :value="localValue"
        placeholder="Descreva o caso (ex: trabalhei 12h sem intervalo em Recife)"
        @input="updateValue(($event.target as HTMLInputElement).value)"
        @keydown.enter.prevent="onSubmit"
      />
    </label>
    <button type="button" :disabled="props.loading" @click="onSubmit">
      <LoaderCircle v-if="props.loading" :size="16" class="spin" />
      <span v-else>Analisar</span>
    </button>
  </div>
</template>

<style scoped>
.search-shell {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 0.7rem;
  width: 100%;
}

.search-input-wrap {
  position: relative;
  display: block;
}

.search-icon {
  position: absolute;
  left: 0.95rem;
  top: 50%;
  translate: 0 -50%;
  color: var(--text-muted);
}

input {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  color: var(--text-strong);
  padding: 0.95rem 1rem 0.95rem 2.8rem;
  font-size: 0.98rem;
  transition: border-color 220ms ease, box-shadow 220ms ease;
}

input:focus {
  outline: none;
  border-color: var(--brand);
  box-shadow: 0 0 0 3px rgba(22, 61, 119, 0.15);
}

button {
  border: 0;
  border-radius: var(--radius-md);
  background: var(--brand);
  color: white;
  min-width: 120px;
  padding: 0 1.2rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 220ms ease, transform 220ms ease;
}

button:hover {
  background: var(--brand-strong);
  transform: translateY(-1px);
}

button:disabled {
  cursor: wait;
  background: #6c80a4;
}

.spin {
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 680px) {
  .search-shell {
    grid-template-columns: 1fr;
  }

  button {
    min-height: 46px;
  }
}
</style>
