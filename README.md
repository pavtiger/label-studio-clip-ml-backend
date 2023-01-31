# label-studio-clip-ml-backend

This project creates simple [ML backend](https://github.com/heartexlabs/label-studio-ml-backend) for [label-studio](https://github.com/heartexlabs/label-studio) that assists you in annotating a new dataset using CLIP, specifically [OWL-ViT](https://huggingface.co/docs/transformers/model_doc/owlvit). As CLIP is trained on a dataset with annotated text captions, it is not needed to train any models like yolo, you just have to declare text classes, which is very convenient. For example `["a photo of a cow", "a photo of a chicken"]`


https://user-images.githubusercontent.com/36619129/215835296-845cbf8c-f788-4aa1-99d7-a311c22d5b14.mp4


Clone repostory with submodules
```shell
git clone git@github.com:pavtiger/label-studio-clip-ml-backend.git --recursive
```
or just clone as usual and pull submodules with this command
```shell
git submodule update --init --recursive
```

## Installation
### It is suggested to use python `venv` for libraries installation
Activate venv
```shell
mkdir venv
python -m venv ./venv
source venv/bin/activate
```

Install requirements
```shell
pip install transformers  # CLIP
pip install -U -e label-studio-ml-backend  # install label studio backend
pip install redis rq  # additional libraries for the backend
```

## Running backend
```shell
label-studio-ml init ml_backend --script ./main.py --force
label-studio-ml start ml_backend
```
The ML backend server becomes available at http://localhost:9090

You can also specify port for the webserver
```shell
label-studio-ml start ml_backend --port 8080 
```

## Connecting to ML backend
Add an ML backend using the Label Studio UI

* In the Label Studio UI, open the project that you want to use with your ML backend.
* Click Settings > Machine Learning.
* Click Add Model.
* Type a Title for the model and provide the URL for the ML backend. For example, http://localhost:9090.
* (Optional) Type a description.
* (Optional) Select Use for interactive preannotation. See Get interactive pre-annotations for more.
* Click Validate and Save.

Instructions to connect taken from [label studio website](https://labelstud.io/guide/ml.html)
