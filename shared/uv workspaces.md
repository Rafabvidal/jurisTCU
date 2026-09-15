# Using workspaces | uv

> uv is an extremely fast Python package and project manager, written in Rust.

[Skip to content](https://docs.astral.sh/uv/concepts/projects/workspaces/#using-workspaces)

[![logo](https://docs.astral.sh/uv/assets/logo-letter.svg)](https://docs.astral.sh/uv/)

uv

Using workspaces

Type to start searching

[

uv

*   0.11.13
*   84.7k
*   3.1k



](https://github.com/astral-sh/uv)

[![logo](https://docs.astral.sh/uv/assets/logo-letter.svg)](https://docs.astral.sh/uv/)uv

[

uv

](https://github.com/astral-sh/uv)

*   [Introduction](https://docs.astral.sh/uv/)
*   [Getting started](https://docs.astral.sh/uv/getting-started/)
    
    Getting started
    
    *   [Installation](https://docs.astral.sh/uv/getting-started/installation/)
    *   [First steps](https://docs.astral.sh/uv/getting-started/first-steps/)
    *   [Features](https://docs.astral.sh/uv/getting-started/features/)
    *   [Getting help](https://docs.astral.sh/uv/getting-started/help/)
    
*   [Guides](https://docs.astral.sh/uv/guides/)
    
    Guides
    
    *   [Installing Python](https://docs.astral.sh/uv/guides/install-python/)
    *   [Running scripts](https://docs.astral.sh/uv/guides/scripts/)
    *   [Using tools](https://docs.astral.sh/uv/guides/tools/)
    *   [Working on projects](https://docs.astral.sh/uv/guides/projects/)
    *   [Publishing packages](https://docs.astral.sh/uv/guides/package/)
    *   [Migration](https://docs.astral.sh/uv/guides/migration/)
        
        Migration
        
        *   [From pip to a uv project](https://docs.astral.sh/uv/guides/migration/pip-to-project/)
        
    *   [Integrations](https://docs.astral.sh/uv/guides/integration/)
        
        Integrations
        
        *   [Docker](https://docs.astral.sh/uv/guides/integration/docker/)
        *   [Jupyter](https://docs.astral.sh/uv/guides/integration/jupyter/)
        *   [marimo](https://docs.astral.sh/uv/guides/integration/marimo/)
        *   [GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/)
        *   [GitLab CI/CD](https://docs.astral.sh/uv/guides/integration/gitlab/)
        *   [Pre-commit](https://docs.astral.sh/uv/guides/integration/pre-commit/)
        *   [PyTorch](https://docs.astral.sh/uv/guides/integration/pytorch/)
        *   [FastAPI](https://docs.astral.sh/uv/guides/integration/fastapi/)
        *   [Azure Artifacts](https://docs.astral.sh/uv/guides/integration/azure/)
        *   [Google Artifact Registry](https://docs.astral.sh/uv/guides/integration/google/)
        *   [AWS CodeArtifact](https://docs.astral.sh/uv/guides/integration/aws/)
        *   [JFrog Artifactory](https://docs.astral.sh/uv/guides/integration/jfrog/)
        *   [Renovate](https://docs.astral.sh/uv/guides/integration/renovate/)
        *   [Dependabot](https://docs.astral.sh/uv/guides/integration/dependabot/)
        *   [AWS Lambda](https://docs.astral.sh/uv/guides/integration/aws-lambda/)
        *   [Coiled](https://docs.astral.sh/uv/guides/integration/coiled/)
        
    
*   [Concepts](https://docs.astral.sh/uv/concepts/)
    
    Concepts
    
    *   [Projects](https://docs.astral.sh/uv/concepts/projects/)
        
        Projects
        
        *   [Structure and files](https://docs.astral.sh/uv/concepts/projects/layout/)
        *   [Creating projects](https://docs.astral.sh/uv/concepts/projects/init/)
        *   [Managing dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/)
        *   [Running commands](https://docs.astral.sh/uv/concepts/projects/run/)
        *   [Locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/)
        *   [Configuring projects](https://docs.astral.sh/uv/concepts/projects/config/)
        *   [Building distributions](https://docs.astral.sh/uv/concepts/projects/build/)
        *   [Exporting lockfiles](https://docs.astral.sh/uv/concepts/projects/export/)
        *   Using workspaces[Using workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/)
            
            Table of contents
            
            *   [Getting started](https://docs.astral.sh/uv/concepts/projects/workspaces/#getting-started)
            *   [Workspace sources](https://docs.astral.sh/uv/concepts/projects/workspaces/#workspace-sources)
            *   [Workspace layouts](https://docs.astral.sh/uv/concepts/projects/workspaces/#workspace-layouts)
            *   [When (not) to use workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/#when-not-to-use-workspaces)
            
        
    *   [Tools](https://docs.astral.sh/uv/concepts/tools/)
    *   [Python versions](https://docs.astral.sh/uv/concepts/python-versions/)
    *   [Configuration files](https://docs.astral.sh/uv/concepts/configuration-files/)
    *   [Package indexes](https://docs.astral.sh/uv/concepts/indexes/)
    *   [Resolution](https://docs.astral.sh/uv/concepts/resolution/)
    *   [Build backend](https://docs.astral.sh/uv/concepts/build-backend/)
    *   [Authentication](https://docs.astral.sh/uv/concepts/authentication/)
        
        Authentication
        
        *   [The auth CLI](https://docs.astral.sh/uv/concepts/authentication/cli/)
        *   [HTTP credentials](https://docs.astral.sh/uv/concepts/authentication/http/)
        *   [Git credentials](https://docs.astral.sh/uv/concepts/authentication/git/)
        *   [TLS certificates](https://docs.astral.sh/uv/concepts/authentication/certificates/)
        *   [Third-party services](https://docs.astral.sh/uv/concepts/authentication/third-party/)
        
    *   [Caching](https://docs.astral.sh/uv/concepts/cache/)
    *   [Preview features](https://docs.astral.sh/uv/concepts/preview/)
    *   [The pip interface](https://docs.astral.sh/uv/pip/)
        
        The pip interface
        
        *   [Using environments](https://docs.astral.sh/uv/pip/environments/)
        *   [Managing packages](https://docs.astral.sh/uv/pip/packages/)
        *   [Inspecting environments](https://docs.astral.sh/uv/pip/inspection/)
        *   [Declaring dependencies](https://docs.astral.sh/uv/pip/dependencies/)
        *   [Locking environments](https://docs.astral.sh/uv/pip/compile/)
        *   [Compatibility with pip](https://docs.astral.sh/uv/pip/compatibility/)
        
    
*   [Reference](https://docs.astral.sh/uv/reference/)
    
    Reference
    
    *   [Commands](https://docs.astral.sh/uv/reference/cli/)
    *   [Settings](https://docs.astral.sh/uv/reference/settings/)
    *   [Environment variables](https://docs.astral.sh/uv/reference/environment/)
    *   [Storage](https://docs.astral.sh/uv/reference/storage/)
    *   [Installer options](https://docs.astral.sh/uv/reference/installer/)
    *   [Troubleshooting](https://docs.astral.sh/uv/reference/troubleshooting/)
        
        Troubleshooting
        
        *   [Build failures](https://docs.astral.sh/uv/reference/troubleshooting/build-failures/)
        *   [Reproducible examples](https://docs.astral.sh/uv/reference/troubleshooting/reproducible-examples/)
        
    *   [Internals](https://docs.astral.sh/uv/reference/internals/)
        
        Internals
        
        *   [Resolver](https://docs.astral.sh/uv/reference/internals/resolver/)
        *   [Workspace Metadata](https://docs.astral.sh/uv/reference/internals/metadata/)
        
    *   [Benchmarks](https://docs.astral.sh/uv/reference/benchmarks/)
    *   [Policies](https://docs.astral.sh/uv/reference/policies/)
        
        Policies
        
        *   [Versioning](https://docs.astral.sh/uv/reference/policies/versioning/)
        *   [Platform support](https://docs.astral.sh/uv/reference/policies/platforms/)
        *   [Python support](https://docs.astral.sh/uv/reference/policies/python/)
        *   [Rust support](https://docs.astral.sh/uv/reference/policies/rust/)
        *   [License](https://docs.astral.sh/uv/reference/policies/license/)
        
    

Table of contents

*   [Getting started](https://docs.astral.sh/uv/concepts/projects/workspaces/#getting-started)
*   [Workspace sources](https://docs.astral.sh/uv/concepts/projects/workspaces/#workspace-sources)
*   [Workspace layouts](https://docs.astral.sh/uv/concepts/projects/workspaces/#workspace-layouts)
*   [When (not) to use workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/#when-not-to-use-workspaces)

1.  [Introduction](https://docs.astral.sh/uv/)
2.  [Concepts](https://docs.astral.sh/uv/concepts/)
3.  [Projects](https://docs.astral.sh/uv/concepts/projects/)

# [Using workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/#using-workspaces)

Inspired by the[Cargo](https://doc.rust-lang.org/cargo/reference/workspaces.html)concept of the same name, a workspace is "a collection of one or more packages, called_workspace members_, that are managed together."

Workspaces organize large codebases by splitting them into multiple packages with common dependencies. Think: a FastAPI-based web application, alongside a series of libraries that are versioned and maintained as separate Python packages, all in the same Git repository.

In a workspace, each package defines its own`pyproject.toml`, but the workspace shares a single lockfile, ensuring that the workspace operates with a consistent set of dependencies.

As such,`uv lock`operates on the entire workspace at once, while`uv run`and`uv sync`operate on the workspace root by default, though both accept a`--package`argument, allowing you to run a command in a particular workspace member from any workspace directory.

## [Getting started](https://docs.astral.sh/uv/concepts/projects/workspaces/#getting-started)

To create a workspace, add a`tool.uv.workspace`table to a`pyproject.toml`, which will implicitly create a workspace rooted at that package.

Tip

By default, running`uv init`inside an existing package will add the newly created member to the workspace, creating a`tool.uv.workspace`table in the workspace root if it doesn't already exist.

In defining a workspace, you must specify the`members`(required) and`exclude`(optional) keys, which direct the workspace to include or exclude specific directories as members respectively, and accept lists of globs:

pyproject.toml```
[project]name="albatross"version="0.1.0"requires-python=">=3.12"dependencies=["bird-feeder","tqdm>=4,<5"][tool.uv.sources]bird-feeder={workspace=true}[tool.uv.workspace]members=["packages/*"]exclude=["packages/seeds"]
```

Every directory included by the`members`globs (and not excluded by the`exclude`globs) must contain a`pyproject.toml`file. However, workspace members can be_either_[applications](https://docs.astral.sh/uv/concepts/projects/init/#applications)or[libraries](https://docs.astral.sh/uv/concepts/projects/init/#libraries); both are supported in the workspace context.

Every workspace needs a root, which is_also_a workspace member. In the above example,`albatross`is the workspace root, and the workspace members include all projects under the`packages`directory, except`seeds`.

By default,`uv run`and`uv sync`operates on the workspace root. For example, in the above example,`uv run`and`uv run --package albatross`would be equivalent, while`uv run --package bird-feeder`would run the command in the`bird-feeder`package.

## [Workspace sources](https://docs.astral.sh/uv/concepts/projects/workspaces/#workspace-sources)

Within a workspace, dependencies on workspace members are facilitated via[`tool.uv.sources`](https://docs.astral.sh/uv/concepts/projects/dependencies/), as in:

pyproject.toml```
[project]name="albatross"version="0.1.0"requires-python=">=3.12"dependencies=["bird-feeder","tqdm>=4,<5"][tool.uv.sources]bird-feeder={workspace=true}[tool.uv.workspace]members=["packages/*"][build-system]requires=["uv_build>=0.11.13,<0.12"]build-backend="uv_build"
```

In this example, the`albatross`project depends on the`bird-feeder`project, which is a member of the workspace. The`workspace = true`key-value pair in the`tool.uv.sources`table indicates the`bird-feeder`dependency should be provided by the workspace, rather than fetched from PyPI or another registry.

Note

Dependencies between workspace members are editable.

Any`tool.uv.sources`definitions in the workspace root apply to all members, unless overridden in the`tool.uv.sources`of a specific member. For example, given the following`pyproject.toml`:

pyproject.toml```
[project]name="albatross"version="0.1.0"requires-python=">=3.12"dependencies=["bird-feeder","tqdm>=4,<5"][tool.uv.sources]bird-feeder={workspace=true}tqdm={git="https://github.com/tqdm/tqdm"}[tool.uv.workspace]members=["packages/*"][build-system]requires=["uv_build>=0.11.13,<0.12"]build-backend="uv_build"
```

Every workspace member would, by default, install`tqdm`from GitHub, unless a specific member overrides the`tqdm`entry in its own`tool.uv.sources`table.

Note

If a workspace member provides`tool.uv.sources`for some dependency, it will ignore any`tool.uv.sources`for the same dependency in the workspace root, even if the member's source is limited by a[marker](https://docs.astral.sh/uv/concepts/projects/dependencies/#platform-specific-sources)that doesn't match the current platform.

## [Workspace layouts](https://docs.astral.sh/uv/concepts/projects/workspaces/#workspace-layouts)

The most common workspace layout can be thought of as a root project with a series of accompanying libraries.

For example, continuing with the above example, this workspace has an explicit root at`albatross`, with two libraries (`bird-feeder`and`seeds`) in the`packages`directory:

```
albatross├── packages│ ├── bird-feeder│ │ ├── pyproject.toml│ │ └── src│ │ └── bird_feeder│ │ ├── __init__.py│ │ └── foo.py│ └── seeds│ ├── pyproject.toml│ └── src│ └── seeds│ ├── __init__.py│ └── bar.py├── pyproject.toml├── README.md├── uv.lock└── src└── albatross└── main.py
```

Since`seeds`was excluded in the`pyproject.toml`, the workspace has two members total:`albatross`(the root) and`bird-feeder`.

## [When (not) to use workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/#when-not-to-use-workspaces)

Workspaces are intended to facilitate the development of multiple interconnected packages within a single repository. As a codebase grows in complexity, it can be helpful to split it into smaller, composable packages, each with their own dependencies and version constraints.

Workspaces help enforce isolation and separation of concerns. For example, in uv, we have separate packages for the core library and the command-line interface, enabling us to test the core library independently of the CLI, and vice versa.

Other common use cases for workspaces include:

*   A library with a performance-critical subroutine implemented in an extension module (Rust, C++, etc.).
*   A library with a plugin system, where each plugin is a separate workspace package with a dependency on the root.

Workspaces are_not_suited for cases in which members have conflicting requirements, or desire a separate virtual environment for each member. In this case, path dependencies are often preferable. For example, rather than grouping`albatross`and its members in a workspace, you can always define each package as its own independent project, with inter-package dependencies defined as path dependencies in`tool.uv.sources`:

pyproject.toml```
[project]name="albatross"version="0.1.0"requires-python=">=3.12"dependencies=["bird-feeder","tqdm>=4,<5"][tool.uv.sources]bird-feeder={path="packages/bird-feeder"}[build-system]requires=["uv_build>=0.11.13,<0.12"]build-backend="uv_build"
```

This approach conveys many of the same benefits, but allows for more fine-grained control over dependency resolution and virtual environment management (with the downside that`uv run --package`is no longer available; instead, commands must be run from the relevant package directory).

Finally, uv's workspaces enforce a single`requires-python`for the entire workspace, taking the intersection of all members'`requires-python`values. If you need to support testing a given member on a Python version that isn't supported by the rest of the workspace, you may need to use`uv pip`to install that member in a separate virtual environment.

Note

As Python does not provide dependency isolation, uv can't ensure that a package uses its declared dependencies and nothing else. For workspaces specifically, uv can't ensure that packages don't import dependencies declared by another workspace member.

May 11, 2026

Back to top

[

Previous

Exporting lockfiles



](https://docs.astral.sh/uv/concepts/projects/export/)[

Next

Tools

](https://docs.astral.sh/uv/concepts/tools/)

Made with[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)

[](https://github.com/astral-sh/uv)[](https://discord.com/invite/astral-sh)[](https://pypi.org/project/uv/)[](https://x.com/astral_sh)

Human readable version: https://docs.astral.sh/uv/concepts/projects/workspaces/#when-not-to-use-workspaces