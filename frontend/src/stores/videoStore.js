/** 
 * Video state yönetimi için Svelte store.
 * Yüklenen video bilgilerini ve seçili video'yu saklar.
 */

import { writable } from 'svelte/store';

/**
 * Yüklenen video bilgileri
 * @type {Object|null}
 */
export const uploadedVideo = writable(null);


export const selectedVideo = writable(null);

/**
 * Video yükleme durumu
 */
export const isUploading = writable(false);

/**
 * Video upload progress (0-100)
 */
export const uploadProgress = writable(0);

/**
 * Oynatılacak video segment bilgileri
 */
export const videoSegment = writable(null);

/**
 * Video store fonksiyonları
 */
export const videoStore = {
  /**
   * Video bilgilerini ayarlar
   */
  setVideo: (videoInfo) => {
    uploadedVideo.set(videoInfo);
  },

  /**
   * Video'yu temizler
   */
  clearVideo: () => {
    uploadedVideo.set(null);
    videoSegment.set(null);
  },

  /**
   * Upload durumunu ayarlar
   */
  setUploading: (status) => {
    isUploading.set(status);
  },

  /**
   * Upload progress günceller
   */
  updateProgress: (progress) => {
    uploadProgress.set(progress);
  },

  /**
   * Video segment bilgilerini ayarlar
   */
  setSegment: (segment) => {
    videoSegment.set(segment);
  }
};