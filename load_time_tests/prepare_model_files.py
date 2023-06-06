#!/usr/bin/env python

import os
import shutil
import sys
import torch

from diffusers import StableDiffusionPipeline
from diffusers.pipelines.stable_diffusion.safety_checker import \
    StableDiffusionSafetyChecker

MODEL_ID = "stabilityai/stable-diffusion-2-1"
MODEL_CACHE = "diffusers-cache"
SAFETY_MODEL_ID = "CompVis/stable-diffusion-safety-checker"

saftey_checker = StableDiffusionSafetyChecker.from_pretrained(
    SAFETY_MODEL_ID,
    cache_dir=MODEL_CACHE,
    torch_dtype=torch.float16
)

pipe = StableDiffusionPipeline.from_pretrained(
    MODEL_ID,
    saftey_checker=saftey_checker,
    cache_dir=MODEL_CACHE,
    torch_dtype=torch.float16
)

# # Save fp16 .bin weights
print('Saving fp16 .bin weights')
saftey_checker.save_pretrained('weights/fp16/bin/safety_checker/')
pipe.save_pretrained('weights/fp16/bin/')

print('Saving fp16 .safetensors weights')
# Save fp16 .safetensor weights
saftey_checker.save_pretrained('weights/fp16/safetensors/safety_checker', safe_serialization=True)
pipe.save_pretrained('weights/fp16/safetensors/', safe_serialization=True)


## Tensorize models
from tensorizer import TensorSerializer
import json 

def ignore_bin_files(dirname, filenames):
    return [name for name in filenames if name.endswith('.bin')]

tensorized_weights_base_path = "weights/fp16/tensors/"
if os.path.exists(tensorized_weights_base_path):
    shutil.rmtree(tensorized_weights_base_path)

shutil.copytree('weights/fp16/bin/', tensorized_weights_base_path)#, ignore=ignore_bin_files)

component_map = {}
for k, component in pipe.components.items():
    if isinstance(component, torch.nn.Module):
        path = os.path.join(tensorized_weights_base_path, k, f"{k}.tensors")
        serializer = TensorSerializer(path)
        serializer.write_module(component)
        serializer.close()

        component_map[k] = {
            'path': path, 
            'cls': component.__class__.__name__,
            'module': component.__module__,
            }
        

# # Save fp16 .bin weights
# print('Saving fp16 .bin weights from cuda')
# saftey_checker = saftey_checker.to('cuda')
# saftey_checker.save_pretrained('weights/fp16/cuda/bin/safety_checker/')

# pipe = pipe.to('cuda')
# pipe.save_pretrained('weights/fp16/cuda/bin/')

# print('Saving fp16 .safetensors weights from cuda')
# # Save fp16 .safetensor weights
# saftey_checker = saftey_checker.to('cuda')
# saftey_checker.save_pretrained('weights/fp16/cuda/safetensors/safety_checker', safe_serialization=True)

# pipe = pipe.to('cuda')
# pipe.save_pretrained('weights/fp16/cuda/safetensors/', safe_serialization=True)