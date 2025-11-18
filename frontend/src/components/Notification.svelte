<script>
  import { createEventDispatcher, onMount } from "svelte";

  export let notification;
  const dispatch = createEventDispatcher();

  let progress = 100;
  let timer;

  onMount(() => {
    timer = setInterval(() => {
      progress -= 2;
      if (progress <= 0) {
        clearInterval(timer);
        dispatch("close");
      }
    }, 100);
  });

  function handleClose() {
    clearInterval(timer);
    dispatch("close");
  }

  const icons = {
    success: "✅",
    error: "❌",
    warning: "⚠️",
    info: "ℹ️",
  };

  const styles = {
    success: "bg-green-50 border-green-200 text-green-800",
    error: "bg-red-50 border-red-200 text-red-800",
    warning: "bg-yellow-50 border-yellow-200 text-yellow-800",
    info: "bg-blue-50 border-blue-200 text-blue-800",
  };
</script>

<div class="relative">
  <div
    class={`p-4 rounded-lg border-2 shadow-lg transform transition-all duration-300 ${styles[notification.type]} animate-slide-in-right`}
    role="alert"
  >
    <div class="flex items-start gap-3">
      <span class="text-lg flex-shrink-0">{icons[notification.type]}</span>
      <p class="flex-1 text-sm font-medium">{notification.message}</p>
      <button
        on:click={handleClose}
        class="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
      >
        ✕
      </button>
    </div>
    <div
      class="absolute bottom-0 left-0 h-1 bg-current opacity-20 transition-all duration-100"
      style={`width: ${progress}%`}
    ></div>
  </div>
</div>

<style>
  @keyframes slide-in-right {
    from {
      opacity: 0;
      transform: translateX(100%);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  .animate-slide-in-right {
    animation: slide-in-right 0.3s ease-out;
  }
</style>
