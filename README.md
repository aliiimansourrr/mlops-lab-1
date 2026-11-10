## Lab 1
## Question 1

After running uv init, the following files and folders were created:

.python-version: specifies the Python version used by the project.
pyproject.toml: contains the project metadata, dependencies, and Python configuration.
README.md: contains documentation about the project.
src/: contains the Python source code of the project.

These files create the basic structure needed to manage the Python project with uv

## Question 2

Running `dvc init` creates the files needed to initialize DVC inside the Git repository.

* `.dvc/config`: contains the DVC project configuration, such as remote storage settings.
* `.dvc/.gitignore`: prevents internal DVC files such as cache and temporary files from being tracked by Git.
* `.dvcignore`: tells DVC which files or folders it should ignore.

The configuration files should be pushed to Git because they allow other developers to reproduce the DVC setup. However, DVC cache files, temporary files, and files containing private credentials should not be pushed to Git.

## Question 3

Because the `--global` option is used, the DVC remote credentials are stored in the user's global DVC configuration, outside the Git repository.

Other configuration options include:

- `--local`: stores repository-specific configuration in `.dvc/config.local`.
- `--system`: stores configuration at the system level.
- No option: stores configuration in the project's `.dvc/config`.

Credentials should never be pushed to GitHub because they are private information such as usernames, passwords, or access tokens.

## Question 4

After running `dvc add data`, DVC added `/data` to the `.gitignore` file.

This means Git will ignore the actual dataset files because they are managed by DVC. Git will only track the DVC metadata file that represents the dataset.

## Question 5

Yes, after running `dvc add data`, a file named `data.dvc` is created.

This file is a DVC pointer file. It does not contain the dataset itself.

It contains metadata about the tracked data, such as:
- the hash of the data
- the size of the tracked data
- the path of the tracked folder

Git tracks `data.dvc`, while DVC uses the information inside it to identify the correct version of the actual data stored in the DVC cache or remote storage.

## Question 6

On the GitHub main branch, the project code is present.

The actual `data` folder is not present on GitHub because it is ignored by Git and managed by DVC instead.

The file `data.dvc` is present on GitHub. This file acts as a pointer to the version of the dataset tracked by DVC.

In my case, the actual dataset is not stored on DagsHub because I used the recommended workaround from the lab: a local DVC remote outside the Git repository.

The real data is stored in:

`C:\Users\mahmo\Desktop\mlops-lab-1-dvc-storage`

So:
- GitHub stores the code and DVC pointer files.
- The local DVC remote stores the actual dataset.

## Question 7

After cloning the GitHub repository into a new folder, the actual `data` folder is not downloaded automatically.

This happens because Git only contains the project code and the `data.dvc` pointer file, while the actual dataset is managed by DVC.

To retrieve the data, the command needed is:

`dvc pull`

In my case, `dvc pull` retrieves the dataset from the local DVC remote configured outside the Git repository.

## Question 8

After switching to the older commit that contained the previous version of `data.dvc` and running:

`dvc checkout`

the new folders:

- `food11_processed`
- `food11_processed_mini`

disappeared from the `data` folder.

Only the older tracked dataset, `food11_raw`, remained.

This shows that Git controls which version of the `data.dvc` pointer file is active, while DVC updates the actual data in the workspace to match that version.

## Lab 2 

## Question 1
After running:

`uv add mlflow torch torchvision scikit-learn`

the `pyproject.toml` file was updated with the new direct dependencies required for model training and experiment tracking:

- `mlflow`
- `torch`
- `torchvision`
- `scikit-learn`

Because this computer does not have an NVIDIA GPU, I also configured a CPU-only PyTorch package source in `pyproject.toml`.

The `uv.lock` file was also updated. It contains the exact resolved versions of the direct dependencies and all of their transitive dependencies, together with information such as package sources and hashes.

The purpose of `pyproject.toml` is mainly to describe the dependencies required by the project, while `uv.lock` locks the exact resolved dependency versions so that the environment can be reproduced consistently.

## Question 2

`--backend-store-uri` defines where MLflow stores the tracking metadata for experiments and runs.

In this lab:

`sqlite:///mlflow.db`

means that MLflow stores the tracking metadata in a local SQLite database file named `mlflow.db`.

This metadata includes information such as:
- experiment names
- run IDs
- parameters
- metrics
- tags
- timestamps
- artifact locations

`--default-artifact-root` defines where MLflow stores run artifacts.

In this lab:

`./mlruns`

means that artifacts are stored locally inside the `mlruns` folder.

The difference is that metadata describes the run and its results, while artifacts are the actual files produced by the run, such as trained models or other output files.

## Question 3

`mlflow.db` and `mlruns/` should not be tracked by Git because they are local outputs generated by MLflow during experiment tracking, not source code.

`mlflow.db` contains local tracking metadata, while `mlruns/` contains locally stored run artifacts.

They should not be tracked by DVC either because they are not versioned datasets. They are experiment-tracking outputs that MLflow manages itself.

Git is used for the project code and configuration, DVC is used for versioning datasets, and MLflow is used for experiment metadata, metrics, parameters, and artifacts.

## Question 4

The first time `mlflow.set_experiment("food11")` was called, MLflow detected that the experiment did not exist and automatically created it.

The terminal displayed:

`Experiment with name 'food11' does not exist. Creating a new experiment.`

After that, the `food11` experiment appeared in the MLflow UI and the training run was logged under it.

## Question 5

`mlflow.log_param` is used to log parameters that are fixed before or during the start of a training run, such as:

- learning rate
- batch size
- number of epochs
- dataset
- model architecture

A parameter normally has one value for the whole run.

`mlflow.log_metric` is used to log values produced during training, such as:

- training loss
- validation loss
- validation accuracy

Metrics can change during training, so `log_metric` accepts a `step` argument.

The `step` identifies when the metric was measured, for example the epoch number. This allows MLflow to plot how the metric changes over time.

Parameters do not need a `step` because they remain fixed for the run.

## Question 6

In the MLflow UI, the run shows the logged parameters, metrics, and the trained model artifact.

The parameters include:
- dataset = `mini`
- epochs = `5`
- lr = `0.001`
- batch_size = `32`
- model = `resnet18`

The logged metrics include:
- `train_loss`
- `val_loss`
- `val_accuracy`
- `test_accuracy`

For the successful run, the final values included approximately:
- `val_accuracy = 0.5648`
- `test_accuracy = 0.5703`

The trained model was also logged successfully.

Because the MLflow server was started with:

`--default-artifact-root ./mlruns`

the model artifact is stored locally under the project's `mlruns` folder.

For this run, the model artifact is located at:

`C:\Users\mahmo\Desktop\mlops-lab-1\mlruns\1\models\m-346856dd700f4374a9fdf175e0a97b55\artifacts`

and the serialized PyTorch model file is:

`C:\Users\mahmo\Desktop\mlops-lab-1\mlruns\1\models\m-346856dd700f4374a9fdf175e0a97b55\artifacts\data\model.pth`

## Question 7

After comparing the runs in the MLflow UI, the learning rate that gave the best validation accuracy was:

`lr = 0.0001`

with a validation accuracy of approximately:

`0.7153`

The higher learning rate was not always better.

For example:
- `lr = 0.01` gave a very low validation accuracy of about `0.12`
- `lr = 0.001` performed much better
- `lr = 0.0001` gave the best result among the tested learning rates

This shows that increasing the learning rate does not necessarily improve model performance.

## Question 8

The parallel coordinates plot shows that the learning rate has a strong effect on validation accuracy.

The best combination among the tested runs was:

- `lr = 0.0001`
- `batch_size = 32`

which achieved a validation accuracy of approximately `0.7153`.

With `batch_size = 32`, increasing the learning rate from `0.0001` to `0.001` reduced the validation accuracy, and increasing it further to `0.01` caused a very large drop in performance.

Changing the batch size from 32 to 64 while keeping `lr = 0.001` also changed the validation accuracy, but in these experiments the learning rate had the clearest effect.

## Question 9

After sorting the runs by `val_accuracy` in descending order, the best run was:

- Run name: `adaptable-shrimp-359`
- Run ID: `0266da079d164fe2adfb3e334b648cad`
- Learning rate: `0.0001`
- Batch size: `32`
- Best validation accuracy: approximately `0.7153`

I noted the run ID because it will be needed in the next lab.

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

## Lab 4 
## Question 1 — What happens to data when a container is removed without a volume?
Data stored only in the container's writable layer is lost when that container is removed. Data in an external volume remains independently of the container.

Evidence: We observed that docker compose down removed our containers while MLflow's registered model remained available afterward. We did not separately test deletion of a file stored exclusively in a container's writable layer.
## Question 2 — Why use a Docker named volume instead of a host bind mount?
A named volume is managed by Docker, allowing MLflow data to persist without depending on a particular Windows folder path. It is also convenient to share with recreated containers.

A bind mount exposes a specified host directory, which can be useful for direct inspection but creates a stronger dependency on host paths and permissions.

Our implementation: We used the named volume mlops-lab-1_mlflow-data for the MLflow SQLite database and artifacts.
## Question 3 — How does the inference container resolve the hostname mlflow?
Docker Compose creates a network where services can communicate using their service names.

Our inference application connects through:
http://mlflow:5000


Docker's internal DNS resolves mlflow to the MLflow service container.

Evidence: Our inference container successfully loaded the model from the MLflow service without using a manually configured container IP address.
## Question 4 — Why use the INFERENCE_URL environment variable?
An environment variable lets the frontend locate the inference API without hardcoding a service address into the application.

Our frontend uses:
INFERENCE_URL=http://inference:8000


This makes it easier to change service addresses across development and deployment environments without modifying application code.

Evidence: Our Streamlit frontend successfully sent image prediction requests to the inference service using this configuration.
## Question 5 — Why can the frontend access inference even though port 8000 is not published?
Both services are on the same Docker Compose network, so the frontend can access inference:8000 internally.

Port publishing is required for access through the host, not for ordinary communication between services on the same network.

Evidence: Our final docker compose ps -a showed:
Service	Published ports
MLflow	5000:5000
Inference	8000/tcp (internal only)
Frontend	8501:8501

Despite port 8000 not being published, the frontend successfully classified an uploaded food image.
## Question 6 — Does depends_on guarantee that MLflow is ready before inference starts?
No. Basic depends_on controls container startup order but does not guarantee application readiness.

Our inference application loads its MLflow model during startup. If MLflow is unavailable or not ready, model loading can fail and prevent inference from starting.

Evidence: During restoration, an immediate health request returned ConnectionRefusedError. After inference completed startup, the same health endpoint returned {"status":"ok"}.

This supports the importance of readiness checks, although we did not prove that MLflow readiness specifically caused that temporary refusal.
## Question 7 — What does docker compose ps show about published ports?
It displays container status, service names, and port mappings.

In our experiment, MLflow published port 5000 and Streamlit published port 8501, while inference exposed port 8000 only inside Docker's network.

This confirms that users interact with the frontend while frontend-to-inference communication remains internal.
## Question 8 — What happened after registering and promoting a new model version without restarting inference?
We registered food11 version 2 and changed the champion alias from version 1 to version 2.

The inference container remained running. Because our application loads the model at startup, changing the registry alias does not automatically reload the model already held in memory.

Actual observation: A prediction request succeeded before inference was restarted. Versions 1 and 2 used identical model artifacts, however, so the prediction itself could not distinguish them. We did not directly inspect the loaded model version inside the running inference process.
## Question 9 — Why does docker compose restart inference load the promoted model without rebuilding the image?
The inference Docker image contains the application code, while MLflow manages the registered model and its versions.

When inference restarts, serve.py executes again and loads:
models:/food11@champion


At that time, the alias pointed to version 2.

Evidence: We restarted inference without rebuilding its Docker image. The startup logs confirmed successful initialization, /health returned {"status":"ok"}, and the application produced the same prediction.

The unchanged prediction was expected because both model versions referenced identical artifacts.
## Question 10 — What is the difference between docker compose down and docker compose down -v?
We tested both commands.
Experiment	Actual observation
docker compose down	Removed containers and network
docker compose up -d afterward	Model registry still contained champion v2
docker compose down -v	Removed containers, network, and MLflow named volume
Backup attempted after deletion	Empty 86-byte archive
Recovery	Re-uploaded model artifacts and registered champion v1
Final backup	Created and verified a ~39.6 MiB archive

Conclusion: Ordinary down preserves named volumes, while down -v removes the Compose-managed volumes and their data.

The original model registry was lost after down -v; we reconstructed the working application using the original locally saved model artifacts.
## Question 11 — What is required to scale inference to three replicas and recover from MLflow host failure?
For multiple inference replicas, we would need orchestration and traffic distribution, such as Docker Swarm or Kubernetes, together with a load balancer.

Each inference replica would need access to the same registered model version and its artifacts.

For MLflow availability after a host failure, we would need persistent storage beyond a single Docker host, such as a shared database backend and durable artifact storage, plus automated service recovery.

Evidence status: Our lab demonstrated three services on one Docker host, not a multi-host or high-availability deployment. These are proposed architectural improvements rather than tested features.
