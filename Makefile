# Constants
APP_IMAGE = rachel-app
APP_DOCKERFILE = docker/Dockerfile.app
TRAIN_IMAGE = rachel-train
TRAIN_DOCKERFILE = docker/Dockerfile.train
DATA_MOUNT = $(PWD)/data
APP_MOUNT = $(PWD)/src

# ------- APP -------
build-app:
	docker build -f $(APP_DOCKERFILE) -t $(APP_IMAGE) .

start:
	docker run --rm -it \
		-v $(PWD):/app \
		-e RACHEL_CONFIG=/app/config.yaml \
		-e PYTHONPATH=/app/src \
		$(APP_IMAGE) python3 -m rachel.api.main


shell:
	docker run --rm -it \
		-v $(PWD):/app \
		-e RACHEL_CONFIG=/app/config.yaml \
		-e PYTHONPATH=/app/src \
		$(APP_IMAGE) bash

# ------- TRAIN -------
train:
	docker build -f $(TRAIN_DOCKERFILE) -t $(TRAIN_IMAGE) .
	docker run --rm --gpus all \
		-v $(DATA_MOUNT):/app/data \
		-v $(APP_MOUNT):/app/src \
		-e RACHEL_CONFIG=/app/src/config.yaml \
		$(TRAIN_IMAGE) train

shell-train:
	docker run --rm --gpus all -it \
		-v $(DATA_MOUNT):/app/data \
		-v $(APP_MOUNT):/app/src \
		-e RACHEL_CONFIG=/app/src/config.yaml \
		$(TRAIN_IMAGE) bash

# ------- Native Training (no Docker) -------
train-native:
	python3 -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install ".[train]"
	PYTHONPATH=./src venv/bin/python -m training.train_hf
