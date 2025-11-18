<script>
  import { createEventDispatcher } from "svelte";
  import TopKButtons from "./TopKButtons.svelte";
  import { selectedVideo } from "../stores/videoStore";

  export let query = "";
  export let hasResults = false;

  const dispatch = createEventDispatcher();

  let inputValue = query;
  let isFocused = false;

  function handleSubmit(e) {
    e.preventDefault();
    if (!$selectedVideo) return;
    if (inputValue.trim()) {
      dispatch("search", inputValue.trim());
    }
  }

  function handleKeydown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }

  $: inputValue = query;
  $: isDisabled = !$selectedVideo;
  $: placeholder = isDisabled
    ? "Please upload or select a video first..."
    : "Describe what you're looking for (e.g., 'person walking', 'car passing by', 'someone wearing red')";
</script>

<div class="mb-8">
  <form on:submit={handleSubmit} class="space-y-4">
    <div class="relative">
      <div class="relative flex items-center">
        <input
          type="text"
          bind:value={inputValue}
          {placeholder}
          required
          disabled={isDisabled}
          on:keydown={handleKeydown}
          on:focus={() => (isFocused = true)}
          on:blur={() => (isFocused = false)}
          class="w-full px-6 py-4 text-lg rounded-2xl border-2 border-gray-200 bg-white shadow-sm
                 transition-all duration-300
                 focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100
                 disabled:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-60
                 placeholder-gray-400"
        />

        <button
          type="submit"
          disabled={isDisabled}
          class="absolute right-2 bg-blue-600 text-white font-semibold text-base px-6 py-3 rounded-xl
                 transition-all duration-300 flex items-center gap-2
                 hover:bg-blue-700 hover:shadow-lg hover:scale-105
                 disabled:bg-gray-400 disabled:cursor-not-allowed disabled:transform-none
                 active:scale-95"
        >
          <span class="text-lg">🔍</span>
          Search
        </button>
      </div>

      {#if isFocused && !isDisabled}
        <div
          class="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg p-3 z-10"
        >
          <p class="text-sm text-gray-600 mb-2 font-medium">
            Search suggestions:
          </p>
          <div class="space-y-1">
            <div class="text-sm text-gray-500">• "person walking"</div>
            <div class="text-sm text-gray-500">• "car passing by"</div>
            <div class="text-sm text-gray-500">• "someone wearing red"</div>
          </div>
        </div>
      {/if}
    </div>

    {#if hasResults}
      <div class="flex justify-center">
        <TopKButtons on:filter />
      </div>
    {/if}

    {#if isDisabled}
      <div
        class="text-center p-4 bg-yellow-50 border border-yellow-200 rounded-xl"
      >
        <p
          class="text-yellow-800 font-medium flex items-center justify-center gap-2"
        >
          <span class="text-lg">📹</span>
          Please upload or select a video to start searching
        </p>
      </div>
    {/if}
  </form>
</div>
