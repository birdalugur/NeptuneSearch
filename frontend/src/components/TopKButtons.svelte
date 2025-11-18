<script>
  import { createEventDispatcher } from "svelte";
  import { maxResults } from "../stores/filterStore";

  const dispatch = createEventDispatcher();

  let activeK = 10;

  function filterResults(k) {
    activeK = k;
    maxResults.set(k);
    dispatch("filter", k);
  }
</script>

<div class="flex gap-2">
  <button
    type="button"
    class={`bg-[#111e68] text-white font-semibold text-base py-3 px-6 rounded-[10px] cursor-pointer transition-all duration-300 ease-in-out hover:bg-[#1f2e9f] hover:-translate-y-0.5
      ${activeK === 5 ? "bg-[#0d1548]" : ""}`}
    on:click={() => filterResults(5)}
  >
    Top 5
  </button>

  <button
    type="button"
    class={`bg-[#111e68] text-white font-semibold text-base py-3 px-6 rounded-[10px] cursor-pointer transition-all duration-300 ease-in-out hover:bg-[#1f2e9f] hover:-translate-y-0.5
      ${activeK === 10 ? "bg-[#0d1548]" : ""}`}
    on:click={() => filterResults(10)}
  >
    Top 10
  </button>

  <button
    type="button"
    class={`bg-[#111e68] text-white font-semibold text-base py-3 px-6 rounded-[10px] cursor-pointer transition-all duration-300 ease-in-out hover:bg-[#1f2e9f] hover:-translate-y-0.5
      ${activeK === 30 ? "bg-[#0d1548]" : ""}`}
    on:click={() => filterResults(30)}
  >
    Top 30
  </button>
</div>
