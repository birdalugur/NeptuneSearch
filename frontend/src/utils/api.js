/**
 * Backend API ile iletişim için yardımcı fonksiyonlar.
 */

const API_BASE_URL = 'http://localhost:8000/api';

/**
 * @param {File} file - Yüklenecek video dosyası
 * @param {Function} onProgress - Progress callback (0-100 arası değer alır)
 * @returns {Promise<Object>} Upload sonucu
 */
export async function uploadVideo(file, onProgress = null) {
  const formData = new FormData();
  formData.append('file', file);

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    // Progress tracking
    if (onProgress) {
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const percentComplete = (e.loaded / e.total) * 100;
          onProgress(percentComplete);
        }
      });
    }

    // Load (tamamlandığında)
    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText);
          resolve(response);
        } catch (error) {
          reject(new Error('Invalid response from server'));
        }
      } else {
        reject(new Error(`Upload failed: ${xhr.statusText}`));
      }
    });

    // Error
    xhr.addEventListener('error', () => {
      reject(new Error('Network error during upload'));
    });

    // Abort
    xhr.addEventListener('abort', () => {
      reject(new Error('Upload aborted'));
    });

    xhr.open('POST', `${API_BASE_URL}/upload`);
    xhr.send(formData);
  });
}

/**
 * Arama fonksiyonu
 * 
 * @param {string} query - Arama sorgusu
 * @param {number} k - Maksimum sonuç sayısı
 * @param {number} similarityThreshold - Minimum benzerlik eşiği
 * @returns {Promise<Object>} Arama sonuçları
 */
export async function search(query, k = 30, similarityThreshold = 0.1) {
  const formData = new FormData();
  formData.append('query', query);
  formData.append('k', k.toString());
  formData.append('similarity_threshold', similarityThreshold.toString());

  const response = await fetch(`${API_BASE_URL}/search`, {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Search failed');
  }

  return response.json();
}

/**
 * Video segment bilgilerini alır
 * 
 * @param {string} videoId - Video ID
 * @param {number} timestamp - Frame timestamp'i
 * @returns {Promise<Object>} Video segment bilgileri
 */
export async function getVideoSegment(videoId, timestamp) {
  const response = await fetch(`${API_BASE_URL}/video-segment`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      video_id: videoId,
      timestamp: timestamp
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get video segment');
  }

  return response.json();
}

/**
 * Health check fonksiyonu
 * 
 * @returns {Promise<Object>} Health status
 */
export async function healthCheck() {
  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) {
    throw new Error('Health check failed');
  }

  return response.json();
}

/**
 * Video listesini alır
 * 
 * @returns {Promise<Object>} Video listesi
 */
export async function listVideos() {
  const response = await fetch(`${API_BASE_URL}/videos`);

  if (!response.ok) {
    throw new Error('Failed to fetch videos');
  }

  return response.json();
}

/**
 * Frame thumbnail URL'ini oluşturur
 * 
 * @param {string} thumbnailUrl - API'den dönen thumbnail path
 * @returns {string} Tam URL
 */
export function getFrameUrl(thumbnailUrl) {
  return `http://localhost:8000${thumbnailUrl}`;
}

/**
 * Video URL'ini oluşturur
 * 
 * @param {string} path - API'den dönen video path
 * @returns {string} Tam URL
 */
export function getVideoUrl(path) {
  // backend /video/<filename> olarak servis ediyorsa:
  return `${API_BASE_URL}${path}`;
}