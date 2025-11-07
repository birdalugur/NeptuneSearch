<!--
Arama formu ve filtreleme kontrolleri.
-->

<script>
  import { createEventDispatcher } from 'svelte';
  import TopKButtons from './TopKButtons.svelte';
  import { uploadedVideo } from '../stores/videoStore';
  
  export let query = '';
  export let hasResults = false;
  
  const dispatch = createEventDispatcher();
  
  let inputValue = query;
  
  function handleSubmit(e) {
    e.preventDefault();
    
    if (!$uploadedVideo) {
      alert('Please upload a video first!');
      return;
    }
    
    if (inputValue.trim()) {
      dispatch('search', inputValue.trim());
    }
  }
  
  $: inputValue = query;
  $: isDisabled = !$uploadedVideo;
</script>

<form on:submit={handleSubmit}>
  <div class="search-row">
    <input 
      type="text" 
      bind:value={inputValue}
      placeholder={isDisabled ? "Upload a video first..." : "Describe what you're looking for (e.g., person walking, car passing)"}
      required
      disabled={isDisabled}
    />
    
    <button type="submit" disabled={isDisabled}>
      🔍 Search
    </button>
  </div>
  
  {#if hasResults}
    <div class="filter-row">
      <TopKButtons on:filter />
    </div>
  {/if}
  
  {#if isDisabled}
    <p class="warning">
      ⚠️ Please upload a video before searching
    </p>
  {/if}
</form>

<style>
  form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 3rem;
  }
  
  .search-row {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
  }
  
  .filter-row {
    display: flex;
    justify-content: center;
    align-items: center;
  }

  input[type="text"] {
    width: 100%;
    max-width: 500px;
    padding: 0.75rem 1rem;
    font-size: 1rem;
    border-radius: 10px;
    border: 1px solid #ccc;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    transition: box-shadow 0.3s ease, border-color 0.3s ease;
  }

  input[type="text"]:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(17, 30, 104, 0.2);
    border-color: #111e68;
  }
  
  input[type="text"]:disabled {
    background-color: #f5f5f5;
    cursor: not-allowed;
    opacity: 0.6;
  }

  button[type="submit"] {
    background-color: #111e68;
    color: white;
    font-weight: 600;
    font-size: 1rem;
    padding: 0.75rem 1.5rem;
    border-radius: 10px;
    border: none;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.2s ease;
    white-space: nowrap;
  }

  button[type="submit"]:hover:not(:disabled) {
    background-color: #1f2e9f;
    transform: translateY(-2px);
  }
  
  button[type="submit"]:disabled {
    background-color: #999;
    cursor: not-allowed;
    transform: none;
  }
  
  .warning {
    text-align: center;
    color: #dc3545;
    font-weight: 600;
    margin: 0;
    animation: pulse 2s ease-in-out infinite;
  }
  
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
  }
  
  @media (max-width: 768px) {
    .search-row {
      flex-direction: column;
      width: 100%;
    }
    
    input[type="text"] {
      max-width: 100%;
    }
    
    button[type="submit"] {
      width: 100%;
    }
  }
</style>