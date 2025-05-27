import cv2
import numpy as np
from rembg import remove, new_session
from PIL import Image
import torch
import torchvision.transforms as transforms
from pathlib import Path

class BackgroundRemover:
    def __init__(self):
        # Initialize the rembg session with a specific model
        self.session = new_session("u2net")
        
        # Define image transformations
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                              std=[0.229, 0.224, 0.225])
        ])

    def preprocess_image(self, image):
        """Preprocess the image for better results."""
        # Convert to numpy array if PIL Image
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # Convert to RGB if grayscale
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        
        return image

    def postprocess_mask(self, mask):
        """Post-process the mask to improve edge quality."""
        # Convert to binary mask
        mask = (mask > 0.5).astype(np.uint8) * 255
        
        # Apply morphological operations to clean up the mask
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        return mask

    def remove_background(self, input_path, output_path=None):
        """Remove background from an image with enhanced processing."""
        try:
            # Read the image
            if isinstance(input_path, (str, Path)):
                image = Image.open(input_path)
            else:
                image = input_path

            # Preprocess the image
            processed_image = self.preprocess_image(image)
            
            # Remove background using rembg
            output = remove(processed_image, session=self.session)
            
            # Convert to PIL Image if numpy array
            if isinstance(output, np.ndarray):
                output = Image.fromarray(output)
            
            # Save the result if output path is provided
            if output_path:
                output.save(output_path, 'PNG')
            
            return output

        except Exception as e:
            print(f"Error in background removal: {str(e)}")
            raise

    def enhance_edges(self, image, mask):
        """Enhance the edges of the foreground object."""
        # Convert to numpy arrays
        if isinstance(image, Image.Image):
            image = np.array(image)
        if isinstance(mask, Image.Image):
            mask = np.array(mask)

        # Apply edge enhancement
        edges = cv2.Canny(mask, 100, 200)
        kernel = np.ones((2,2), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        # Combine with original image
        enhanced = cv2.bitwise_and(image, image, mask=edges)
        
        return Image.fromarray(enhanced)

    def process_batch(self, input_paths, output_dir):
        """Process multiple images in batch."""
        results = []
        for input_path in input_paths:
            output_path = Path(output_dir) / f"processed_{Path(input_path).name}"
            try:
                result = self.remove_background(input_path, output_path)
                results.append((True, output_path))
            except Exception as e:
                results.append((False, str(e)))
        return results 