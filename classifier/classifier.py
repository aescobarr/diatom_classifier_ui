import shutil
import tempfile
import zipfile

import torch
from torchvision import models
import torchvision.transforms as T
import torch.nn as nn
from classifier.transform_classes import ResizeWithReplicatePadding
from classifier.models import ClassificationModel
from PIL import Image
from django.conf import settings
import os
from datetime import datetime


def create_summary(classification_result: dict) -> str:
    items = []
    total = 0
    for key in classification_result:
        n_pictures = len(classification_result[key])
        total = total + n_pictures
        items.append(f"{key} : {n_pictures}")
    items.append(f"total: {total}")
    return ",".join(items)

def create_temp_dir() -> tempfile.TemporaryDirectory:
    return tempfile.TemporaryDirectory()


def create_results_dir(results_dir_root: str, classification_result: dict, classes: list) -> None:
    prepare_results_dir(results_dir_root, classes)
    for key in classification_result:
        pictures = classification_result[key]
        for picture in pictures:
            shutil.copy(picture, os.path.join( results_dir_root, key ))


def prepare_results_dir(results_dir_root: str, classes: list) -> None:
    os.mkdir(results_dir_root)
    for c in classes:
        os.mkdir( os.path.join( results_dir_root, c ) )


def create_results_zip(results_dir_root: str) -> str:
    now = datetime.now()
    output_filename = now.strftime("results-%Y-%m-%d-%H-%M-%S")
    output_filename_path = os.path.join(settings.OUTPUTS_DIR,output_filename)
    shutil.make_archive(str(output_filename_path), 'zip', results_dir_root)
    return output_filename


def unzip_to_dir(zipfile_path : str, directory_to_explode: str) -> None:
    with zipfile.ZipFile(zipfile_path, 'r') as zip_ref:
        zip_ref.extractall(directory_to_explode)


def init_resnet(n_classes: int) -> models.resnet50:
    resnet = models.resnet50(weights='IMAGENET1K_V1')
    # Modify the final classifier with dropout for regularization
    resnet.fc = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(resnet.fc.in_features, 512),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(512, n_classes)
    )

    # Fine-tune more layers for diatom-specific features
    # Unfreeze the last two residual blocks
    for param in resnet.parameters():
        param.requires_grad = False

    # Unfreeze layer4 (last residual block) and fc
    for param in resnet.layer4.parameters():
        param.requires_grad = True
    for param in resnet.fc.parameters():
        param.requires_grad = True

    return resnet


def init_transform() -> T.Compose:
    return T.Compose([
            ResizeWithReplicatePadding(target_size=224),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

def classify(weights_file: str, pictures_dir: str, classes: list) -> dict:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = init_resnet(n_classes=len(classes))
    transform = init_transform()
    state_file = torch.load(weights_file)
    model.load_state_dict(state_file)
    model.eval()

    classification = {}
    for c in classes:
        classification[c] = []

    dir = os.listdir(pictures_dir)

    for img_wo_path in dir:
        img_w_path = os.path.join(pictures_dir,img_wo_path)
        img = Image.open(img_w_path)
        img_tensor = transform(img)
        img_tensor = torch.stack([img_tensor])
        img_tensor = img_tensor.to(device)
        with torch.no_grad():
            output = model(img_tensor)
            _, preds = torch.max(output, dim=1)
            classification[ classes[preds.item()] ].append( str(img_w_path) )
    return classification


