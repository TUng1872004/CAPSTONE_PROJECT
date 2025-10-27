import torch
from torchvision import transforms
from timm.data.constants import IMAGENET_INCEPTION_MEAN, IMAGENET_INCEPTION_STD

class Processor():
    def __init__(self, tokenizer):
        self.image_processor = transforms.Compose([
            transforms.Resize((384, 384), interpolation=3),  #type: ignore
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_INCEPTION_MEAN, std=IMAGENET_INCEPTION_STD)
        ])
        
        self.tokenizer = tokenizer
    
    def process(self, image=None, text=None):
        assert (image is not None) or (text is not None)
        language_tokens = None
        padding_mask = None
        if image is not None:
            image = self.image_processor(image)
            image = image.unsqueeze(0)
        if text is not None:
            language_tokens, padding_mask, _ = self.get_text_segment(text)
        return {'image': image, 'text_description': language_tokens, 'padding_mask': padding_mask}
            
        
    def get_text_segment(self, text, max_len=64):
        tokens = self.tokenizer.tokenize(text)
        tokens = self.tokenizer.convert_tokens_to_ids(tokens)

        if len(tokens) > max_len - 2:
            tokens = tokens[:max_len - 2]

        tokens = [self.tokenizer.bos_token_id] + tokens[:] + [self.tokenizer.eos_token_id]
        num_tokens = len(tokens)
        padding_mask = [0] * num_tokens + [1] * (max_len - num_tokens)
        language_tokens = tokens + [self.tokenizer.pad_token_id] * (max_len - num_tokens)
        return torch.tensor([language_tokens]),  torch.tensor([padding_mask]), num_tokens
    
    def process_batch(self, images):
        batch_images = [self.image_processor(img) for img in images]
        batch_images = torch.stack(batch_images, dim=0)  
        return {'image': batch_images}