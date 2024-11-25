TAG ?= latest
RUNTIME_CONTAINER ?= manuela-runtime:$(TAG)
WORKBENCH_CONTAINER ?= manuela-workbench:$(TAG)

##@ Help-related tasks
.PHONY: help
help: ## Help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^(\s|[a-zA-Z_0-9-])+:.*?##/ { printf "  \033[36m%-35s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Build-related tasks
.PHONY: build
build: build-runtime build-workbench test ## Build the runtime and the workbench container locally

.PHONY: build-runtime
build-runtime: ## build manuela-runtime container
	cd ./container-source; buildah bud -f ./Containerfile-runtime --format docker -t $(RUNTIME_CONTAINER)

.PHONY: build-workbench
build-workbench: ## build manuela-workbench container
	cd ./container-source; buildah bud -f ./Containerfile-workbench --format docker -t $(WORKBENCH_CONTAINER)

.PHONY: test
test: ## test the built containers
	podman run -it --rm --net=host --entrypoint /bin/sh $(RUNTIME_CONTAINER) -c "jupyter --version" 
	podman run -it --rm --net=host --entrypoint /bin/sh $(WORKBENCH_CONTAINER) -c "jupyter --version" 

.PHONY: clean
clean: ## Removes any previously built artifact
	podman rmi $(RUNTIME_CONTAINER) $(WORKBENCH_CONTAINER)

.PHONY: super-linter
super-linter: ## Runs super linter locally
	rm -rf .mypy_cache
	podman run -e RUN_LOCAL=true -e USE_FIND_ALGORITHM=true	\
					-e VALIDATE_JAVASCRIPT_STANDARD=false \
					-e VALIDATE_MARKDOWN=false \
					-e VALIDATE_JAVASCRIPT_PRETTIER=false \
					-e VALIDATE_JSCPD=false \
					-e VALIDATE_JSON=false \
					-e VALIDATE_JSON_PRETTIER=false \
					-e VALIDATE_MARKDOWN_PRETTIER=false \
					-e VALIDATE_BASH=false \
					-e VALIDATE_BASH_EXEC=false \
					-e VALIDATE_CHECKOV=false \
					-e VALIDATE_CSS=false \
					-e VALIDATE_CSS_PRETTIER=false \
					-e VALIDATE_GITLEAKS=false \
					-e VALIDATE_GOOGLE_JAVA_FORMAT=false \
					-e VALIDATE_HTML=false \
					-e VALIDATE_HTML_PRETTIER=false \
					-e VALIDATE_JAVA=false \
					-e VALIDATE_KUBERNETES_KUBECONFORM=false \
					-e VALIDATE_NATURAL_LANGUAGE=false \
					-e VALIDATE_SHELL_SHFMT=false \
					-e VALIDATE_TYPESCRIPT_PRETTIER=false \
					-e VALIDATE_TYPESCRIPT_STANDARD=false \
					-e VALIDATE_YAML=false \
					-e VALIDATE_YAML_PRETTIER=false \
					-v $(PWD):/tmp/lint:rw,z \
					-w /tmp/lint \
					ghcr.io/super-linter/super-linter:slim-v7
