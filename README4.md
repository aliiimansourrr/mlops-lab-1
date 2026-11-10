## Lab 4 
## Question 1 â€” What happens to data when a container is removed without a volume?
Data stored only in the container's writable layer is lost when that container is removed. Data in an external volume remains independently of the container.

Evidence: We observed that docker compose down removed our containers while MLflow's registered model remained available afterward. We did not separately test deletion of a file stored exclusively in a container's writable layer.
## Question 2 â€” Why use a Docker named volume instead of a host bind mount?
A named volume is managed by Docker, allowing MLflow data to persist without depending on a particular Windows folder path. It is also convenient to share with recreated containers.

A bind mount exposes a specified host directory, which can be useful for direct inspection but creates a stronger dependency on host paths and permissions.

Our implementation: We used the named volume mlops-lab-1_mlflow-data for the MLflow SQLite database and artifacts.
## Question 3 â€” How does the inference container resolve the hostname mlflow?
Docker Compose creates a network where services can communicate using their service names.

Our inference application connects through:
http://mlflow:5000


Docker's internal DNS resolves mlflow to the MLflow service container.

Evidence: Our inference container successfully loaded the model from the MLflow service without using a manually configured container IP address.
## Question 4 â€” Why use the INFERENCE_URL environment variable?
An environment variable lets the frontend locate the inference API without hardcoding a service address into the application.

Our frontend uses:
INFERENCE_URL=http://inference:8000


This makes it easier to change service addresses across development and deployment environments without modifying application code.

Evidence: Our Streamlit frontend successfully sent image prediction requests to the inference service using this configuration.
## Question 5 â€” Why can the frontend access inference even though port 8000 is not published?
Both services are on the same Docker Compose network, so the frontend can access inference:8000 internally.

Port publishing is required for access through the host, not for ordinary communication between services on the same network.

Evidence: Our final docker compose ps -a showed:
Service	Published ports
MLflow	5000:5000
Inference	8000/tcp (internal only)
Frontend	8501:8501

Despite port 8000 not being published, the frontend successfully classified an uploaded food image.
## Question 6 â€” Does depends_on guarantee that MLflow is ready before inference starts?
No. Basic depends_on controls container startup order but does not guarantee application readiness.

Our inference application loads its MLflow model during startup. If MLflow is unavailable or not ready, model loading can fail and prevent inference from starting.

Evidence: During restoration, an immediate health request returned ConnectionRefusedError. After inference completed startup, the same health endpoint returned {"status":"ok"}.

This supports the importance of readiness checks, although we did not prove that MLflow readiness specifically caused that temporary refusal.
## Question 7 â€” What does docker compose ps show about published ports?
It displays container status, service names, and port mappings.

In our experiment, MLflow published port 5000 and Streamlit published port 8501, while inference exposed port 8000 only inside Docker's network.

This confirms that users interact with the frontend while frontend-to-inference communication remains internal.
## Question 8 â€” What happened after registering and promoting a new model version without restarting inference?
We registered food11 version 2 and changed the champion alias from version 1 to version 2.

The inference container remained running. Because our application loads the model at startup, changing the registry alias does not automatically reload the model already held in memory.

Actual observation: A prediction request succeeded before inference was restarted. Versions 1 and 2 used identical model artifacts, however, so the prediction itself could not distinguish them. We did not directly inspect the loaded model version inside the running inference process.
## Question 9 â€” Why does docker compose restart inference load the promoted model without rebuilding the image?
The inference Docker image contains the application code, while MLflow manages the registered model and its versions.

When inference restarts, serve.py executes again and loads:
models:/food11@champion


At that time, the alias pointed to version 2.

Evidence: We restarted inference without rebuilding its Docker image. The startup logs confirmed successful initialization, /health returned {"status":"ok"}, and the application produced the same prediction.

The unchanged prediction was expected because both model versions referenced identical artifacts.
## Question 10 â€” What is the difference between docker compose down and docker compose down -v?
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
## Question 11 â€” What is required to scale inference to three replicas and recover from MLflow host failure?
For multiple inference replicas, we would need orchestration and traffic distribution, such as Docker Swarm or Kubernetes, together with a load balancer.

Each inference replica would need access to the same registered model version and its artifacts.

For MLflow availability after a host failure, we would need persistent storage beyond a single Docker host, such as a shared database backend and durable artifact storage, plus automated service recovery.

Evidence status: Our lab demonstrated three services on one Docker host, not a multi-host or high-availability deployment. These are proposed architectural improvements rather than tested features.
