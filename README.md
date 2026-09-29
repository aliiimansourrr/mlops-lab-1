Question 1

After running uv init, the following files and folders were created:

.python-version: specifies the Python version used by the project.
pyproject.toml: contains the project metadata, dependencies, and Python configuration.
README.md: contains documentation about the project.
src/: contains the Python source code of the project.

These files create the basic structure needed to manage the Python project with uv

Question 2

Running `dvc init` creates the files needed to initialize DVC inside the Git repository.

* `.dvc/config`: contains the DVC project configuration, such as remote storage settings.
* `.dvc/.gitignore`: prevents internal DVC files such as cache and temporary files from being tracked by Git.
* `.dvcignore`: tells DVC which files or folders it should ignore.

The configuration files should be pushed to Git because they allow other developers to reproduce the DVC setup. However, DVC cache files, temporary files, and files containing private credentials should not be pushed to Git.

Question 3

Because the `--global` option is used, the DVC remote credentials are stored in the user's global DVC configuration, outside the Git repository.

Other configuration options include:

- `--local`: stores repository-specific configuration in `.dvc/config.local`.
- `--system`: stores configuration at the system level.
- No option: stores configuration in the project's `.dvc/config`.

Credentials should never be pushed to GitHub because they are private information such as usernames, passwords, or access tokens.

Question 4

After running `dvc add data`, DVC added `/data` to the `.gitignore` file.

This means Git will ignore the actual dataset files because they are managed by DVC. Git will only track the DVC metadata file that represents the dataset.

Question 5

Yes, DVC created a `data.dvc` file.

This file contains metadata about the tracked `data` directory, such as its hash, size, number of files, and path.

The hash identifies the exact version of the dataset. The `data.dvc` file is tracked by Git, while the actual dataset is stored and versioned by DVC.
