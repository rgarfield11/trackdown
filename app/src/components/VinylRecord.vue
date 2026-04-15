<script setup lang="ts">
defineProps<{ spinning: boolean }>()
</script>

<template>
  <div class="vinyl-wrap">
    <img src="/vinyl.svg" alt="Vinyl record" class="vinyl" :class="{ spinning }" />
  </div>
</template>

<style scoped>
.vinyl-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 8px 0;
}

.vinyl {
  width: 130px;
  height: 130px;
  border-radius: 50%;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.6);
}

.vinyl.spinning {
  animation: spin 3s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
</style>
