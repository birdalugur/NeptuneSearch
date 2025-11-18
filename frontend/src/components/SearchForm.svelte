<script>
  import { createEventDispatcher } from "svelte";
  import TopKButtons from "./TopKButtons.svelte";
  import { selectedVideo } from "../stores/videoStore";

  export let query = "";
  export let hasResults = false;

  const dispatch = createEventDispatcher();

  let inputValue = query;

  function handleSubmit(e) {
    e.preventDefault();

    if (!$selectedVideo) {
      alert("Please upload a video first!");
      return;
    }

    if (inputValue.trim()) {
      dispatch("search", inputValue.trim());
    }
  }

  $: inputValue = query;
  $: isDisabled = !$selectedVideo;
</script>

<form on:submit={handleSubmit} class="flex flex-col gap-4 mb-12">
  <div
    class="flex justify-center items-center gap-4 flex-wrap md:flex-col md:w-full"
  >
    <input
      type="text"
      bind:value={inputValue}
      placeholder={isDisabled
        ? "Upload a video first..."
        : "Describe what you're looking for (e.g., person walking, car passing)"}
      required
      disabled={isDisabled}
      class="w-full max-w-[500px] md:max-w-full px-4 py-3 text-base rounded-xl border border-gray-300 shadow-sm
             transition-all duration-300
             focus:outline-none focus:ring-4 focus:ring-primary/20 focus:border-primary
             disabled:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-60"
    />

    <button
      type="submit"
      disabled={isDisabled}
      class="bg-primary text-white font-semibold text-base px-6 py-3 rounded-xl border-none cursor-pointer
             whitespace-nowrap transition-all duration-300
             hover:bg-primary-hover hover:-translate-y-0.5
             disabled:bg-gray-400 disabled:cursor-not-allowed disabled:transform-none
             md:w-full"
    >
      🔍 Search
    </button>
  </div>

  {#if hasResults}
    <div class="flex justify-center items-center">
      <TopKButtons on:filter />
    </div>
  {/if}

  {#if isDisabled}
    <p class="text-center text-red-600 font-semibold animate-pulse-opacity">
      ⚠️ Please upload a video before searching
    </p>
  {/if}
</form>
