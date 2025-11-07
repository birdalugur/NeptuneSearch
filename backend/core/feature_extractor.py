"""
Bu modül CLIP modelini kullanarak görsel ve metin feature'ları çıkarır.
Görsel arama için gerekli embedding'leri oluşturur.
"""

from pathlib import Path
from typing import List, Union
import numpy as np
from PIL import Image
import torch
from transformers import CLIPModel, CLIPProcessor

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class FeatureExtractor:
    """
    CLIP tabanlı feature extraction sınıfı.

    Görsel ve metin verilerinden embedding'ler çıkarır.
    """

    def __init__(self, model_name: str = None, device: str = None):
        """
        FeatureExtractor instance'ı oluşturur.

        Args:
            model_name: CLIP model ismi (varsayılan: settings'den alınır)
            device: İşlem cihazı 'cpu' veya 'cuda' (varsayılan: settings'den alınır)
        """
        self.model_name = model_name or settings.MODEL_NAME
        self.device = device or settings.DEVICE

        if self.device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

        logger.info(
            f"Initializing FeatureExtractor with model: {self.model_name} on device: {self.device}"
        )

        self.model = CLIPModel.from_pretrained(self.model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(self.model_name)

        self.model.eval()

        logger.info("FeatureExtractor initialized successfully")

    def extract_image_features(
        self, image_paths: Union[Path, List[Path]], batch_size: int = 32
    ) -> np.ndarray:
        """
        Görsel dosyalarından feature'ları çıkarır.

        Args:
            image_paths: Tek bir görsel yolu veya görsel yolları listesi
            batch_size: Batch processing için boyut

        Returns:
            Feature vektörleri numpy array (N, embedding_dim)
        """
        if isinstance(image_paths, Path):
            image_paths = [image_paths]

        logger.info(f"Extracting features from {len(image_paths)} images")

        all_features = []

        for i in range(0, len(image_paths), batch_size):
            batch_paths = image_paths[i : i + batch_size]
            batch_images = []

            # Görselleri yükle ve preprocess et
            for path in batch_paths:
                try:
                    image = Image.open(path).convert("RGB")
                    batch_images.append(image)
                except Exception as e:
                    logger.warning(f"Error loading image {path}: {e}")
                    continue

            if not batch_images:
                continue

            inputs = self.processor(
                images=batch_images, return_tensors="pt", padding=True
            )

            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                features = self.model.get_image_features(**inputs)

            features = features.cpu().numpy()
            all_features.append(features)

            if (i // batch_size + 1) % 10 == 0:
                logger.info(
                    f"Processed {i + len(batch_paths)}/{len(image_paths)} images"
                )

        if not all_features:
            raise ValueError("No features could be extracted from the provided images")

        features_array = np.vstack(all_features).astype("float32")

        logger.info(f"Feature extraction completed: shape {features_array.shape}")

        return features_array

    def extract_text_features(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Metin/metinlerden feature'ları çıkarır.

        Args:
            text: Tek bir metin veya metin listesi

        Returns:
            Feature vektörleri numpy array (N, embedding_dim)
        """
        if isinstance(text, str):
            text = [text]
            single_input = True
        else:
            single_input = False

        logger.debug(f"Extracting features from {len(text)} text(s)")

        inputs = self.processor(
            text=text, return_tensors="pt", padding=True, truncation=True
        )

        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            features = self.model.get_text_features(**inputs)

        features = features.cpu().numpy().astype("float32")

        if single_input:
            features = features.reshape(-1)

        logger.debug(f"Text feature extraction completed: shape {features.shape}")

        return features

    def get_embedding_dimension(self) -> int:
        """
        Embedding boyutunu döndürür.

        Returns:
            Embedding vektörünün boyutu
        """
        return self.model.config.projection_dim

    def normalize_features(self, features: np.ndarray) -> np.ndarray:
        """
        Feature vektörlerini L2 normalizasyonu yapar.

        Cosine similarity hesaplaması için gereklidir.

        Args:
            features: Feature vektörleri

        Returns:
            Normalize edilmiş feature vektörleri
        """
        norms = np.linalg.norm(features, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        normalized = features / norms

        return normalized.astype("float32")
