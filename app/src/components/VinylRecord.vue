<script setup lang="ts">
defineProps<{ spinning: boolean }>()
</script>

<template>
  <div class="vinyl-wrap">
    <div class="vinyl" :class="{ spinning }">
      <div class="label">
        <span class="question">?</span>
      </div>
    </div>
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
  background:
    radial-gradient(circle at center, transparent 18%, #1a1410 18.5%),
    repeating-radial-gradient(
      circle at center,
      #2a2318 0px,
      #2a2318 2px,
      #1c1810 2px,
      #1c1810 6px
    );
  box-shadow:
    0 0 0 1px #3d3528,
    0 4px 24px rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.vinyl.spinning {
  animation: spin 3s linear infinite;
}

.label {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: radial-gradient(circle at 40% 40%, #c8954a, #8a5e28);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.4);
  z-index: 1;
}

.question {
  font-size: 20px;
  font-weight: 800;
  color: #1a1410;
  line-height: 1;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
</style>
