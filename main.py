import os
import pathlib
import torch
from PIL import Image

from label_studio_ml.model import LabelStudioMLBase
from transformers import OwlViTProcessor, OwlViTForObjectDetection


CLIP_CLASSES = ["a photo of a cow", "a photo of a chicken"]
CLIP_CLASSES_MAP = {"a photo of a cow": "Cow", "a photo of a chicken": "Chicken"}
SCORE_THRESHOLD = 0.3

LABEL_STUDIO_DATA_PATH = "/home/pavtiger/Docs/label-studio/mydata/media"


class DummyModel(LabelStudioMLBase):
    def __init__(self, **kwargs):
        super(DummyModel, self).__init__(**kwargs)

        from_name, schema = list(self.parsed_label_config.items())[0]
        self.from_name = from_name
        self.to_name = schema['to_name'][0]
        self.labels = schema['labels']

    def predict_clip(self, image):
        results = []
        x_shape, y_shape = image.size

        processor = OwlViTProcessor.from_pretrained("google/owlvit-base-patch32")
        model = OwlViTForObjectDetection.from_pretrained("google/owlvit-base-patch32")

        texts = [CLIP_CLASSES]
        inputs = processor(text=texts, images=image, return_tensors="pt")
        outputs = model(**inputs)
        # Target image sizes (height, width) to rescale box predictions [batch_size, 2]

        target_sizes = torch.Tensor([image.size[::-1]])
        # Convert outputs (bounding boxes and class logits) to COCO API
        model_results = processor.post_process_object_detection(outputs=outputs, target_sizes=target_sizes)
        i = 0  # Retrieve predictions for the first image for the corresponding text queries

        text = texts[i]
        boxes, scores, labels = model_results[i]["boxes"].detach().cpu().numpy(), model_results[i]["scores"].detach().cpu().numpy(), model_results[i]["labels"].detach().cpu().numpy()

        for box, score, label in zip(boxes, scores, labels):
            box = [round(i, 2) for i in box.tolist()]
            if score >= SCORE_THRESHOLD:
                print(f"Detected {text[label]} with confidence {round(score.item(), 3)} at location {box}")

                x_delta, y_delta = box[2] - box[0], box[3] - box[1]
                result = {
                    'from_name': self.from_name,
                    'to_name': self.to_name,
                    "original_width": x_shape,
                    "original_height": y_shape,
                    "image_rotation": 0,
                    'type': 'rectanglelabels',
                    'value': {
                        'rectanglelabels': [CLIP_CLASSES_MAP[text[label]]],
                        'x': (box[0] / x_shape) * 100,
                        'y': (box[1] / y_shape) * 100,
                        'width': (x_delta / x_shape) * 100,
                        'height': (y_delta / y_shape) * 100
                    },
                    'score': round(score.item(), 3),
                    'model_version': 'test123'
                }
                results.append(result)

        return results

    def predict(self, tasks, **kwargs):
        """ This is where inference happens: 
            model returns the list of predictions based on input list of tasks

            :param tasks: Label Studio tasks in JSON format
        """
        results = []
        print(len(tasks))
        for i, task in enumerate(tasks):
            print(task['data']['image'])
            image_path = pathlib.Path(task['data']['image'])
            new_path = pathlib.Path(*image_path.parts[2:])

            img = Image.open(os.path.join(LABEL_STUDIO_DATA_PATH, new_path))
            y = self.predict_clip(img)

            results.append({
                'result': y,
                'score': float(0.4)
            })

        return results

    def fit(self, completions, workdir=None, **kwargs):
        """ This is where training happens: train your model given list of completions,
            then returns dict with created links and resources
            :param completions: aka annotations, the labeling results from Label Studio 
            :param workdir: current working directory for ML backend
        """
        return NotImplementedError
