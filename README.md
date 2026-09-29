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