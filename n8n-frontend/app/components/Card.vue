<template>
  <div :class="cardClasses">
    <slot />
  </div>
</template>

<script setup>
const props = defineProps({
  class: {
    type: String,
    default: ''
  }
})

const cardClasses = computed(() => {
  return `rounded-lg border bg-white text-gray-950 shadow-sm ${props.class}`
})
</script>
