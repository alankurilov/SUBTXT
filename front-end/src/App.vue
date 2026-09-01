<script setup>
import { computed, ref } from 'vue'

const screen = ref('landing')
const file = ref(null)
const isProcessing = ref(false)
const recommendedOnly = ref(true)
const activeMoment = ref(null)
const exportOpen = ref(false)

const moments = ref([
  { id: 1, term: 'AOC', time: '1:35', type: 'People', quote: 'AOC made the case for a more direct response.', detail: 'Alexandria Ocasio-Cortez is a U.S. representative known for progressive policy advocacy.', selected: true, approved: null, gradient: 'from-[#617389] via-[#29303a] to-[#141619]' },
  { id: 2, term: 'Goldwater Rule', time: '4:12', type: 'Culture', quote: 'That is a straight-up Goldwater Rule violation.', detail: 'An ethics guideline barring psychiatrists from diagnosing public figures they have not examined.', selected: true, approved: null, gradient: 'from-[#805e54] via-[#332a2c] to-[#161719]' },
  { id: 3, term: 'Overton window', time: '8:46', type: 'Politics', quote: 'The Overton window has moved dramatically.', detail: 'The range of policy ideas considered politically acceptable at a given time.', selected: true, approved: null, gradient: 'from-[#345c68] via-[#243239] to-[#111417]' },
  { id: 4, term: 'Sunk cost fallacy', time: '12:18', type: 'Concepts', quote: 'We should not let sunk costs decide the outcome.', detail: 'A tendency to continue an effort because of prior investment rather than future value.', selected: false, approved: null, gradient: 'from-[#6d5c45] via-[#312d28] to-[#141517]' },
  { id: 5, term: 'Jevons paradox', time: '16:02', type: 'Concepts', quote: 'Efficiency can increase total consumption — Jevons paradox.', detail: 'Efficiency improvements can lead to increased, rather than reduced, use of a resource.', selected: false, approved: null, gradient: 'from-[#465e4e] via-[#29332d] to-[#141715]' },
  { id: 6, term: 'Dunning–Kruger effect', time: '20:33', type: 'Psychology', quote: 'It is a classic Dunning–Kruger effect.', detail: 'A cognitive bias in which people with limited expertise overestimate their ability.', selected: false, approved: null, gradient: 'from-[#655671] via-[#302d38] to-[#151419]' }
])

const visibleMoments = computed(() => recommendedOnly.value ? moments.value.filter(m => m.selected) : moments.value)
const selectedMoments = computed(() => moments.value.filter(m => m.selected))
const pendingEdits = computed(() => selectedMoments.value.filter(m => m.approved === null).length)

function go(next) { screen.value = next }
function selectFile(event) {
  file.value = event.target.files?.[0] || { name: 'podcast-episode.mp4', size: 264000000 }
}
function beginAnalysis() {
  isProcessing.value = true
  window.setTimeout(() => { isProcessing.value = false; go('curate') }, 1800)
}
function startCaptions() {
  isProcessing.value = true
  go('captioning')
  window.setTimeout(() => { isProcessing.value = false; go('edit') }, 1800)
}
function toggleMoment(moment) { moment.selected = !moment.selected; moment.approved = null }
function fmtSize(bytes) { return `${(bytes / 1_000_000).toFixed(0)} MB` }
</script>

<template>
  <main class="min-h-screen bg-ink text-slate-100">
    <header v-if="screen === 'landing'" class="sticky top-0 z-20 border-b border-line/90 bg-ink/90 backdrop-blur">
      <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <button class="flex items-center gap-2 font-display text-lg font-bold tracking-[.22em]" aria-label="SUBTXT home" @click="go('landing')"><span class="grid size-6 place-items-center rounded-full bg-[#1b455f] text-xs tracking-normal text-[#7aceff]">✦</span>SUBTXT</button>
        <div class="flex gap-3"><button class="rounded-md border border-line px-4 py-2 text-sm text-muted">Pricing</button><button class="rounded-lg bg-brand px-4 py-2 text-sm font-semibold" @click="go('upload')">Get started</button></div>
      </div>
    </header>

    <section v-if="screen === 'landing'">
      <div class="mx-auto max-w-7xl px-6 pt-24 pb-16"><h1 class="max-w-3xl font-display text-4xl leading-tight font-bold tracking-tight sm:text-6xl">Your video conversations are full of references casual viewers won’t catch.</h1><p class="mt-7 max-w-2xl text-xl leading-relaxed text-muted">SUBTXT automatically adds contextual captions, so every viewer can follow along.</p><button class="mt-8 rounded-lg bg-brand px-7 py-4 font-display font-semibold hover:brightness-110" @click="go('upload')">Get started</button></div>
      <div class="mr-0 h-[360px] overflow-hidden rounded-r-3xl bg-[#95abba] sm:mr-8 sm:h-[440px]"><div class="relative mx-auto flex h-full max-w-7xl items-end px-6"><div class="z-10 mb-16 max-w-md rounded-lg bg-[#142c3b] shadow-2xl"><div class="px-5 py-3 font-display font-semibold">✦ Electoral College</div><p class="rounded-b-lg bg-[#4d5d6b] px-5 py-4 text-sm leading-relaxed">The US system where each state's votes for president are decided by electors, not the national popular vote.</p></div><img class="pointer-events-none absolute bottom-0 right-5 h-[96%] max-w-[54%] object-contain object-bottom" src="/hero-host.png" alt="Podcast host speaking into a microphone" /></div></div>
    </section>

    <section v-else-if="screen === 'upload'" class="mx-auto max-w-[1440px] px-6 py-8 sm:px-12">
      <div class="flex items-center justify-between"><ProgressSteps class="mb-0 flex-1" :step="1" /><button class="ml-6 shrink-0 text-sm text-muted hover:text-white" @click="go('landing')">← Back to home</button></div>
      <div class="mx-auto mt-28 max-w-3xl"><h2 class="font-display text-4xl font-bold tracking-tight">Upload your conversation</h2><p class="mt-4 text-xl text-muted">Long-form video works best — podcasts, interviews, panels.</p>
      <label class="mt-10 flex h-62 min-h-60 cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed border-[#39414d] p-8 text-center transition hover:border-brand hover:bg-brand/5"><span class="grid size-10 place-items-center rounded-full bg-faint/20 text-2xl text-muted">↑</span><span class="mt-5 text-lg font-semibold">Choose a video file</span><span class="mt-2 text-sm text-faint">or drag it here · MP4, MOV, or a YouTube link</span><input class="hidden" type="file" accept="video/*" @change="selectFile" /></label>
      <div v-if="file" class="mt-6 flex items-center gap-4 rounded-xl border border-line border-l-4 border-l-brand bg-panel p-4"><div class="grid size-14 place-items-center rounded-lg bg-slate-800 text-xl">▶</div><div class="min-w-0 flex-1"><p class="truncate font-medium">{{ file.name }}</p><p class="text-sm text-faint">{{ fmtSize(file.size) }} · Ready to analyse</p></div><button class="text-sm text-muted" @click="file = null">Remove</button></div>
      <div class="mt-7 flex justify-end"><button class="rounded-lg bg-brand px-7 py-3 font-display font-semibold disabled:cursor-not-allowed disabled:opacity-40" :disabled="!file" @click="beginAnalysis">Analyse video</button></div></div>
    </section>

    <section v-else-if="screen === 'processing' || screen === 'captioning'" class="mx-auto flex min-h-screen max-w-xl items-center px-6">
      <div class="w-full rounded-2xl border border-line bg-panel p-8 sm:p-10"><p class="font-display text-lg font-bold tracking-[.2em]">SUBTXT</p><h2 class="mt-6 font-display text-3xl font-bold">{{ screen === 'processing' ? 'Finding the context that matters.' : 'Preparing your captions.' }}</h2><div class="my-7 border-t border-line" /><div class="space-y-5"><div v-for="item in (screen === 'processing' ? ['Identifying concepts your audience may not know', 'Detecting unexplained references', 'Prioritising the moments worth captioning'] : ['Generating contextual captions', 'Clipping moments', 'Determining optimal positioning'])" :key="item" class="flex items-center gap-3 text-muted"><span class="size-5 animate-spin rounded-full border-2 border-line border-t-brand" /><span>{{ item }}</span></div></div></div>
    </section>

    <section v-else-if="screen === 'curate'" class="mx-auto max-w-7xl px-6 pb-36 pt-10">
      <ProgressSteps :step="2" /><h2 class="font-display text-3xl font-bold">Choose which references to caption.</h2><p class="mt-3 text-muted">SUBTXT found these moments your audience may miss. Select the ones you’d like to explain.</p><div class="mt-8 border-t border-line pt-7"><div class="inline-flex rounded-full border border-line bg-panel p-1"><button class="rounded-full px-5 py-2 text-sm font-semibold" :class="recommendedOnly ? 'bg-brand text-white' : 'text-muted'" @click="recommendedOnly = true">Recommended</button><button class="rounded-full px-5 py-2 text-sm font-semibold" :class="!recommendedOnly ? 'bg-brand text-white' : 'text-muted'" @click="recommendedOnly = false">All</button></div></div>
      <div class="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3"><article v-for="moment in visibleMoments" :key="moment.id" class="overflow-hidden rounded-lg border-2 bg-panel transition" :class="moment.selected ? 'border-brand/70 bg-brand/10' : 'border-line'" ><button class="relative block aspect-[4/3] w-full bg-gradient-to-br text-left" :class="moment.gradient" @click="toggleMoment(moment)"><span v-if="moment.selected" class="absolute right-3 top-3 grid size-6 place-items-center rounded-full bg-brand text-sm">✓</span><span class="absolute inset-x-4 bottom-4 font-display text-xl font-bold text-white">{{ moment.term }}<small class="mt-1 block font-sans text-xs font-medium text-white/65">{{ moment.type }} · {{ moment.time }}</small></span></button><div class="flex justify-between p-3"><button class="text-sm text-muted hover:text-white" @click="activeMoment = moment">Why this?</button><span class="text-xs text-faint">{{ moment.selected ? 'Included' : 'Not included' }}</span></div></article></div>
      <footer class="fixed inset-x-0 bottom-0 border-t border-line bg-[#101216]/95 backdrop-blur"><div class="mx-auto flex max-w-7xl items-center justify-between gap-4 px-6 py-4"><p class="text-sm text-muted"><b class="text-white">{{ selectedMoments.length }}</b> references selected</p><div class="flex gap-3"><button class="rounded-lg border border-line px-4 py-2 text-sm text-muted" @click="go('upload')">← Back</button><button class="rounded-lg bg-brand px-5 py-2 font-display text-sm font-semibold disabled:opacity-40" :disabled="!selectedMoments.length" @click="startCaptions">Generate captions</button></div></div></footer>
    </section>

    <section v-else-if="screen === 'edit'" class="mx-auto max-w-5xl px-6 pb-32 pt-10"><ProgressSteps :step="3" /><h2 class="font-display text-3xl font-bold">Review each caption</h2><p class="mt-3 text-muted">Check wording, placement and timing before continuing.</p><div class="mt-8 space-y-4"><article v-for="moment in selectedMoments" :key="moment.id" class="rounded-xl border border-line bg-panel p-5"><div class="flex flex-col gap-5 sm:flex-row"><div class="grid aspect-video w-full shrink-0 place-items-center rounded-lg bg-gradient-to-br sm:w-48" :class="moment.gradient"><span class="rounded-full border border-white/30 bg-black/30 px-3 py-2 text-sm">▶ Preview</span></div><div class="min-w-0 flex-1"><p class="text-xs font-bold tracking-widest text-faint">{{ moment.time }}</p><input v-model="moment.term" class="mt-2 w-full bg-transparent font-display text-xl font-bold outline-none" /><textarea v-model="moment.detail" rows="3" class="mt-3 w-full resize-none rounded-lg border border-line bg-ink p-3 text-sm leading-relaxed text-muted outline-none focus:border-brand" /><div class="mt-4 flex flex-wrap gap-2"><button class="rounded-md border px-3 py-2 text-sm" :class="moment.approved === true ? 'border-brand bg-brand/15 text-white' : 'border-line text-muted'" @click="moment.approved = true">✓ Approve</button><button class="rounded-md border px-3 py-2 text-sm" :class="moment.approved === false ? 'border-red-400 bg-red-400/10 text-red-300' : 'border-line text-muted'" @click="moment.approved = false">Remove</button></div></div></div></article></div><footer class="fixed inset-x-0 bottom-0 border-t border-line bg-[#101216]/95 backdrop-blur"><div class="mx-auto flex max-w-5xl items-center justify-between px-6 py-4"><p class="text-sm text-muted">{{ pendingEdits ? `${pendingEdits} captions need review` : 'All captions reviewed' }}</p><button class="rounded-lg bg-brand px-5 py-2 font-display text-sm font-semibold disabled:opacity-40" :disabled="pendingEdits > 0" @click="exportOpen = true">Continue to export</button></div></footer></section>

    <div v-if="activeMoment" class="fixed inset-0 z-30 grid place-items-center bg-black/80 p-6 backdrop-blur-sm" @click.self="activeMoment = null"><div class="w-full max-w-md overflow-hidden rounded-xl border border-line bg-panel"><div class="relative aspect-video bg-gradient-to-br" :class="activeMoment.gradient"><button class="absolute right-3 top-3 rounded border border-white/30 bg-black/40 px-2 py-1" @click="activeMoment = null">×</button></div><div class="p-6"><h3 class="font-display text-xl font-bold">{{ activeMoment.term }}</h3><p class="mt-4 border-l-2 border-line pl-3 italic text-muted">“{{ activeMoment.quote }}”</p><p class="mt-5 text-sm leading-relaxed text-muted">{{ activeMoment.detail }}</p></div></div></div>
    <div v-if="exportOpen" class="fixed inset-0 z-30 grid place-items-center bg-black/80 p-6" @click.self="exportOpen = false"><div class="w-full max-w-md rounded-xl border border-line bg-panel p-7"><h3 class="font-display text-2xl font-bold">Export — next in the build</h3><p class="mt-3 text-muted">Your reviewed captions are ready for the export workflow.</p><button class="mt-6 rounded-lg bg-brand px-5 py-3 font-semibold" @click="exportOpen = false">Back to review</button></div></div>
  </main>
</template>

<script>
const ProgressSteps = {
  props: { step: Number },
  template: `<nav class="mb-10 flex items-center gap-3 text-sm font-display font-semibold"><template v-for="(label, index) in ['Upload', 'Curate', 'Edit', 'Export']" :key="label"><span :class="index + 1 < step ? 'text-muted' : index + 1 === step ? 'text-white' : 'text-faint'">{{ index + 1 < step ? '✓ ' : index + 1 + '. ' }}{{ label }}</span><span v-if="index < 3" class="h-px flex-1 bg-line" /></template></nav>`
}
export default { components: { ProgressSteps } }
</script>
