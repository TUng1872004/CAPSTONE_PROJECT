import os
import torch
import numpy as np
from typing import Optional
from tqdm.notebook import tqdm
from torch.nn import Module
import os
from .transnet_v2 import TransNetV2
from .utils import get_batches,get_frames




class AutoShot:
    def __init__(
        self,
        pretrained_path: str,
        device: Optional[str] = None
    ):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.load_model(pretrained_path=pretrained_path)
    

    def load_model(self, pretrained_path: str) -> Module:
        model = TransNetV2().eval()
        if not os.path.exists(pretrained_path):
            raise FileNotFoundError(f"Can't find the pretrained model path at {pretrained_path}")

        print(f"Loading the pretrained model from {pretrained_path}")
        state_dict = torch.load(pretrained_path, map_location=self.device, weights_only=True)
        model.load_state_dict(state_dict)
        model.eval()
        return model.to(self.device)



    def predict(self, batch: np.ndarray) -> np.ndarray:
        """
            batch: (height, width, channels, frames)
                    (27, 48, channel=3, frames = 100)
        """
        with torch.no_grad():
            tensor = torch.from_numpy(
                batch.transpose(3,0,1,2)
            ).unsqueeze(0).to(torch.uint8)

            

            tensor = tensor.to(self.device)
            one_hot = self.model(tensor)
            if isinstance(one_hot, tuple):
                one_hot = one_hot[0]
            
            return torch.sigmoid(one_hot[0]).cpu().detach().numpy()
    

    def detect_shots(self, frames: np.ndarray) -> np.ndarray:
        predictions = []

        for batch in tqdm(
            get_batches(frames=frames), desc="Detecting shots", unit='batch'
        ):
            prediction = self.predict(batch=batch)
            predictions.append(
                prediction[25:75]
            )
        
        return np.concatenate(
            predictions, axis=0
        )[: len(frames)]
    

    @staticmethod
    def predictions_to_scenes(predictions: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        predictions = (predictions > threshold).astype(np.uint8)
        scenes = []
        t, t_prev, start = -1, 0, 0
        for i, t in enumerate(predictions):
            if t_prev == 1 and t == 0:
                start = i
            if t_prev == 0 and t == 1 and i != 0:
                scenes.append([start, i])
            t_prev = t
        if t == 0:
            scenes.append([start, i]) #type:ignore

        if len(scenes) == 0:
            return np.array([[0, len(predictions) - 1]], dtype=np.int32)
        return np.array(scenes, dtype=np.int32)


    def process_video(self, video_path: str) -> list[list[int]]:

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"File not found: {video_path}")
        
        frames = get_frames(video_file_path=video_path)
        if frames is None or len(frames) == 0:
            raise ValueError(f"No frames extracted from video: {video_path}")

        predictions = self.detect_shots(frames=frames)

        scenes = AutoShot.predictions_to_scenes(predictions=predictions)

        return scenes.tolist()


    
        



