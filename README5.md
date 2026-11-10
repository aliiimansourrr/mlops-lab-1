# Lab 5 — CI/CD with GitHub Actions: Questions and Answers

These answers reflect the Food-11 project experiments performed during Lab 5. Where a behavior was not directly observed, the answer distinguishes the expected mechanism from the measured result.

## Question 1

**Why is it a bad idea for a unit test to load the real model from your MLflow server? List at least two ways the test could fail even though your code is correct.**

A unit test should isolate application logic. Loading the real model from MLflow adds external dependencies and makes tests slow and unreliable. The test could fail because (1) the MLflow server is offline or inaccessible from a CI runner; (2) the `champion` alias, model artifacts, or network are unavailable; or (3) an incompatible model dependency prevents deserialization. None of these failures necessarily means the function under test is incorrect. In this lab, `SKIP_MODEL=1` prevented model loading during tests, and a fake model isolated API behavior.

## Question 2

**The fake model always answers "Bread" with 0.90 confidence. What exactly does `test_predict_returns_valid_json` prove, and what does it not prove?**

It proves that the FastAPI `/predict` endpoint accepts an uploaded image, invokes the model interface, and returns a successful HTTP response containing the expected JSON fields and valid output values. The test exercises the request/response path without depending on MLflow. It does **not** establish that the trained Food-11 classifier recognizes real food correctly, that its confidence is calibrated, or that MLflow can load the production model. Those require separate integration and model-evaluation tests.

## Question 3

**Which check caught the intentional duplicate? Why is a train/test duplicate more dangerous than a corrupted image, even though the corrupted image makes the training script crash and the duplicate does not?**

The **cross-split duplicate-content check**, using MD5 hashes of image bytes, caught the image copied from `training/Bread` into `evaluation/Bread`. The validator reported `FAIL` and exited with status code `1`. After removing the deliberately copied file, it passed again on the cleaned temporary validation dataset. The original mini dataset also contained 43 groups of byte-identical images across splits; the original DVC-tracked dataset was not modified.

A corrupted image is typically an obvious failure because loading or training crashes. A duplicate between training and evaluation can go unnoticed while leaking previously seen examples into the test set. This can inflate the reported accuracy and mislead model-selection decisions, which is more insidious than a visible crash.

## Question 4

**Your CI runner cannot see your data (it is in DVC, and maybe in a local remote). Where in your workflow should `validate_data.py` run so that it still protects you? Give two places.**

1. **Locally before committing or pushing**, after the developer has retrieved the DVC-tracked data; a pre-push hook or a documented local verification command can enforce the check.
2. **In an environment with access to the dataset**, such as a self-hosted CI runner configured with the DVC remote, or a CI job that first authenticates to an accessible remote and executes `dvc pull` before running validation.

A standard GitHub-hosted runner cannot validate files it has not downloaded. The completed lab ran the data validation locally; the cloud CI workflow ran Ruff, pytest, and a Docker smoke test, not a validation of the unavailable complete DVC dataset.

## Question 5

**The `smoke` job has `needs: test`. What happens to it if a unit test fails? What would happen without `needs`?**

When `test` fails, `smoke` is skipped because its dependency did not succeed. We observed precisely that behavior in the deliberately failing pull-request experiment. Without `needs: test`, GitHub Actions could schedule `smoke` independently and in parallel; it might build and test a container even though the unit tests already failed, wasting CI resources and weakening the intended quality-gate order.

## Question 6

**How long did the whole run take? Run it a second time (push an empty commit with `git commit --allow-empty -m "ci"`) and compare. Which step got faster, and why?**

The first CI run took **2 minutes 12 seconds**, and its `test` job took **26 seconds**. The second run, triggered by an empty commit, took **2 minutes 13 seconds**, while its `test` job took **24 seconds**. Thus, the test job was **2 seconds faster**, but the full workflow was **1 second slower**. The second run's `smoke` job took approximately **1 minute 43 seconds**.

Dependency caching from `setup-uv` can reduce repeated downloads and setup work, and Docker layer caching can reduce rebuild work when configured and cache hits occur. However, the measured two-second improvement does not prove which individual operation benefited from caching; runner variability and other job timings also matter. There was **no overall speedup** in these two runs.

## Question 7

**Why tag with the commit SHA rather than `latest`? Describe a concrete situation where `latest` leads two machines to run different code.**

A Git commit SHA is an immutable identifier for the source revision used to produce a particular image. It supports reproducibility, traceability, and rollback. A mutable `latest` tag can be moved to a new image at any time. For example, machine A pulls `latest` on Monday (commit X), while machine B pulls `latest` on Tuesday after another release (commit Y). Both machines say they run `latest`, yet they execute different code. In this lab, the GHCR image was successfully published and pulled using the full commit SHA `f0676cc843903584ba386c763fa34aa956e420f2`.

## Question 8

**Why does the `push` job declare `permissions:` explicitly? What could a compromised step do with a token that had write access to everything in the repo?**

The job applies the principle of least privilege: `contents: read` allows checking out source code, and `packages: write` permits publishing the image to GitHub Container Registry. A broadly privileged `GITHUB_TOKEN` in a compromised step could potentially alter or delete repository content, interfere with workflows, change issues or pull requests, or abuse other write-enabled API capabilities. Limiting token permissions reduces the blast radius. The exact actions possible depend on token scopes and repository protections.

## Question 9

**What does the pull request page show? Could you still merge? What does that change for a team compared to "everybody runs the tests on their laptop before pushing"?**

We intentionally changed the eleven-class assertion to expect 12 classes and opened **Pull Request #1** from `lab5-failing-test`. The `test` check failed and `smoke` was skipped. GitHub reported the pull request as blocked, so it was not ready for merging under the configured required checks. We restored the assertion to 11, pushed commit `272d67a`, observed the required `test` and `smoke` checks pass, and merged the pull request. The resulting merge commit on `main` was `939cc12`.

For a team, centrally enforced checks provide a consistent, reviewable gate on the exact code being merged. They do not rely solely on each developer remembering to run tests or having an identically configured laptop.

## Question 10

**For each candidate, what did the gate decide, and with which numbers? With your test-set size, how many accuracy points does `2 * se` represent?**

The restored champion, **Food-11 version 1**, was evaluated on **1,096** images: **836 correct**, giving `test_accuracy = 836 / 1096 = 0.7627737226277372` (76.2774%). This post-restoration measurement was explicitly logged to its MLflow run because the restored run initially had no metrics.

The quality-gate calculation was:

```text
n                  = 1096
p (champion)       = 0.7627737226277372
SE = sqrt(p(1-p)/n)= 0.012849137645251014
2 * SE             = 0.025698275290502028
Promotion threshold= 0.7884719979182393
```

Thus, **2 × SE is approximately 2.57 percentage points**, and a candidate needed at least **78.85%** test accuracy to replace champion v1.

| Model | Version | Training configuration | Test accuracy | Gate decision |
|---|---:|---|---:|---|
| Existing champion | 1 | Restored model; evaluated after restoration | 0.7627737226 (76.28%) | Stays `champion` |
| Candidate 1 | 2 | Mini dataset; 3 epochs; learning rate 0.0001; batch size 32 | 0.7563868613 (75.64%) | **REJECTED**, assigned `challenger` |
| Candidate 2 | 3 | Mini dataset; 5 epochs; learning rate 0.0003; batch size 32 | 0.7500000000 (75.00%) | **REJECTED**, assigned `challenger` |

Candidate 1 was below the threshold (`0.756387 < 0.788472`), and candidate 2 was also below it (`0.750000 < 0.788472`). The final MLflow aliases were **`champion` → version 1** and **`challenger` → version 3**; version 2 retained its `REJECTED` decision tags, but no longer held the `challenger` alias. Both rejections and stored thresholds were verified through MLflow.

**Limitation:** the original mini dataset had cross-split duplicate images, so these numbers are useful for testing the promotion workflow but may overstate generalization performance. Neither of the two experiments exercised the *successful-promotion* branch.

## Question 11

**`promote.py` needs to reach your MLflow server, so it cannot run in GitHub's cloud runners while MLflow lives on your laptop. Name two ways to make it run automatically after training.**

1. **Use a self-hosted runner or local orchestration process** on the same computer/network as the MLflow server. After training and registration finish, that runner or process invokes `promote.py` with the new registered version.
2. **Host MLflow on a reachable service**, such as DagsHub-hosted MLflow or a secured cloud MLflow deployment. Then a GitHub Actions job (triggered after training/model registration) can authenticate with stored secrets and run the promotion command over the network.

In this lab, training, registration, and promotion were performed manually. These are proposed ways to automate them, not automation already implemented.

## Question 12

**Draw (in `lab/lab5.md`) the pipeline you now have, from `git push` to a running container. Mark which steps are automatic, which still need a human, and where the code version and the model version are decided.**

The Mermaid pipeline diagram is in **[`lab/lab5.md`](lab/lab5.md)**. Its CI/CD path shows push/PR events, automated Ruff and pytest checks, the dependent Docker smoke test (which starts a model-free container and probes `/health`), branch protection and manual PR merge, followed by automated GHCR publishing on `main`. The **code version** is the Git commit SHA used in the GHCR image tag.

The diagram also shows the separate **manual model lifecycle**: training and MLflow logging, registration, running the statistical promotion gate, and eventually deploying/reloading a selected model. The **model version** is decided in the MLflow registry by the registered `food11` version and its `champion` or `challenger` alias. Image publishing does not by itself retrain, promote, or deploy the model. The container was proven to start in CI with `SKIP_MODEL=1`; deploying a newly promoted model remains a separate step.
