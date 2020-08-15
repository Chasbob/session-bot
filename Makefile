ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
CONFIG_FILE          ?= $(ROOT_DIR)/config.json
MAKE_ENV        += TOKEN EVENTS_ID GUILD_ID ROLE_ID
SHELL_EXPORT    := $(foreach v,$(MAKE_ENV),$(v)='$($(v))' )

PACKAGE       		   ?= bot
DEFAULT_IMAGE 		   ?= chasbob/session-bot
VERSION       		   ?= $(shell git describe --tags --always --dirty --match="v*" 2> /dev/null || cat $(CURDIR)/.version 2> /dev/null || echo v0)
DOCKER_REGISTRY_DOMAIN ?= docker.pkg.github.com
DOCKER_REGISTRY_PATH   ?= chasbob/session-bot
DOCKER_IMAGE           ?= $(DOCKER_REGISTRY_PATH)/$(PACKAGE):$(VERSION)
DOCKER_IMAGE_DOMAIN    ?= $(DOCKER_REGISTRY_DOMAIN)/$(DOCKER_IMAGE)

.PHONY: run
run:
	source ./bin/build-config.sh && poetry run python -m session-bot

.PHONY: config
config:
	$(shell source $(ROOT_DIR)/build-config.sh)

.PHONY: watch
watch:
	reflex -r '\.py$\' -s -- sh -c 'make run'

.PHONY: docker-build
docker-build:
	docker build $(ROOT_DIR) --tag $(DOCKER_IMAGE_DOMAIN) --file $(ROOT_DIR)/Dockerfile

.PHONY: docker-run
docker-run: docker-build docker-rm
	source ./bin/build-config.sh && docker run -d --name session-bot -e CONFIG $(DOCKER_IMAGE_DOMAIN)

.PHONY: docker-rm
docker-rm:
	docker rm -f session-bot | true

.PHONY: docker-log
docker-log: docker-run
	docker logs -f session-bot