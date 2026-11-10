## Lab 3
## Question 1

The model was registered in the MLflow Model Registry under the name:

`food11`

MLflow assigned it version:

`1`

A run's logged model artifact is the model produced by one specific training run. It belongs to that run and is stored together with the run's metrics, parameters, and artifacts.

A registered model is a separate, named model entry in the MLflow Model Registry. It can have multiple versions, where each version may come from a different training run.

This separation makes it easier to manage and promote models independently from the experiments that produced them.

## Question 2

The old built-in MLflow model stages such as `Staging` and `Production` have been replaced by aliases.

An alias is a named pointer to a specific registered model version, for example:

`champion`

The model is versioned separately from the training run because the registry manages the lifecycle of deployable models independently from the experiments that produced them.

A registered model can have several versions coming from different runs.

An alias is more flexible than a fixed stage because it can be reassigned to another model version without changing the version number itself.

For example, if a newer model becomes better, the `champion` alias can simply be moved from version 1 to the newer version.

## Question 3

Loading the model through the MLflow model URI:

`models:/food11@champion`

is better than loading a `.pth` file directly because the application does not need to know the exact model file path or version.

MLflow Model Registry manages the model versions, metadata, and aliases.

The `champion` alias points to the model version that should currently be served.

If a newer model version becomes the preferred model, I only need to move the `champion` alias to the new version. The serving code can stay unchanged because it continues loading:

`models:/food11@champion`

## Question 4

`pyproject.toml` and `uv.lock` are copied and dependencies are installed before copying the application source code because Docker caches image layers.

The dependency files usually change less often than the source code. By installing the dependencies in an earlier layer, Docker can reuse that cached layer when the dependencies have not changed.

If I only change a line in `serve.py`, Docker does not need to reinstall all the dependencies again. It can reuse the cached dependency layer and only rebuild the layers that copy the source code and come after it.

This makes rebuilds much faster.

## Question 5

I compared a naive single-stage Docker image with the multi-stage image.

The image sizes were approximately:

- Multi-stage image: `2.00 GB` disk usage, `427 MB` content size
- Naive image: `2.18 GB` disk usage, `479 MB` content size

So the multi-stage image was smaller by about:

- `180 MB` in disk usage
- `52 MB` in content size

Using `docker history`, I found that the largest layer in both images was the Python virtual environment and installed dependencies.

In the naive image, the `pip install uv` layer was also present in the final image and used about `82.4 MB`.

In the multi-stage image, `uv` and other builder-only files were left in the builder stage and were not copied into the final runtime image.

This shows how a multi-stage build can reduce the final image size by keeping build tools out of the runtime image.

## Question 6

If `.dockerignore` is missing, Docker sends unnecessary files and folders to the Docker daemon as part of the build context.

This can make the build slower because large folders such as:

- `.venv/`
- `data/`
- `mlruns/`
- `.git/`

would all be transferred even though the Dockerfile does not need them.

It can also increase disk and memory usage during the build and make Docker caching less efficient.

In this project, these folders are especially large:
- `data/` contains the Food-11 dataset
- `.venv/` contains all installed Python packages
- `mlruns/` contains MLflow artifacts and saved models

With the current Dockerfile, these folders would mainly make the build context much larger rather than automatically breaking the build, because the Dockerfile copies only specific files such as `pyproject.toml`, `uv.lock`, and `src/`.

However, if a Dockerfile used `COPY . .`, folders such as `.venv/` could cause problems because they contain environment-specific files from the host machine, and large folders such as `data/` and `mlruns/` would unnecessarily bloat the image.

## Question 7

Inside a Docker container, `127.0.0.1` refers to the container itself, not to the host computer.

Therefore, if the application inside the container tried to use:

`http://127.0.0.1:5000`

it would look for the MLflow server inside that same container.

On Windows, Docker provides the hostname:

`host.docker.internal`

This hostname resolves to the host machine from inside the container.

Therefore I used:

`http://host.docker.internal:5000`

as the `MLFLOW_TRACKING_URI`, which allowed the containerized FastAPI application to connect to the MLflow tracking server running on the host.

## Question 8

Yes, the same Docker image was able to load the model again after restarting the container without rebuilding the image.

The serving code loads the model using:

`models:/food11@champion`

The Docker image contains the API code and its dependencies, but the actual model version is resolved at runtime from the MLflow Model Registry.

I reassigned the `champion` alias from model version 1 to version 2 and then started a new container using the same `food11-api:latest` image.

The container successfully loaded the new champion model and returned a prediction.

This means the model can be updated independently from the Docker image, as long as the container can reach the MLflow tracking/artifact server.

## Question 9

The Dockerfile is versioned in Git, but the built Docker image currently exists only on my local machine.

Before another machine such as a CI runner or Kubernetes cluster could reliably run the exact image, the image would need to be pushed to a container registry such as Docker Hub, GitHub Container Registry, or another registry.

The image should also use a version-specific tag or, preferably, an immutable image digest instead of relying only on the mutable `latest` tag.

For example:

`food11-api:v1`

or an image referenced by its SHA256 digest.

This allows another machine to pull the exact same built image instead of rebuilding it from the Dockerfile and potentially getting a different result.
