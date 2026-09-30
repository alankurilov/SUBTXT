<!-- ProgressSteps.vue -->
<script setup>
defineProps({
  step: { type: Number, default: 1 },
  labels: { type: Array, default: () => ['Curate', 'Style', 'Fine tune', 'Export'] },
})
</script>

<template>
  <nav class="w-full border-t border-line/70 bg-ink">
    <div class="px-1 pb-2 pt-3">
      <ol class="grid grid-cols-4 text-[14px] font-medium leading-none">
        <li
          v-for="(label, index) in labels"
          :key="label"
          :class="[
            index === 0 ? 'text-left' : index === labels.length - 1 ? 'text-right' : 'text-center',
            index + 1 <= step ? 'text-white' : 'text-faint',
          ]"
        >{{ label }}</li>
      </ol>
      <div class="mt-3 flex items-center" aria-hidden="true">
        <template v-for="(label, index) in labels" :key="label">
          <span v-if="index + 1 === step" class="grid size-4 shrink-0 place-items-center rounded-full border-2 border-brand bg-ink">
            <span class="size-1.5 rounded-full bg-brand" />
          </span>
          <span v-else-if="index + 1 < step" class="grid size-4 shrink-0 place-items-center rounded-full bg-brand">
            <span class="text-[10px] font-bold leading-none text-white">✓</span>
          </span>
          <span v-else class="size-3.5 shrink-0 rounded-full bg-[#343a44]" />
          <span
            v-if="index < labels.length - 1"
            class="mx-5 h-px flex-1"
            :class="index + 1 < step ? 'bg-brand' : 'bg-line/90'"
          />
        </template>
      </div>
    </div>
  </nav>
</template>