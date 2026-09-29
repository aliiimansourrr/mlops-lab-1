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
