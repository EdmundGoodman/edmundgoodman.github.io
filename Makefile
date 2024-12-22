MAKEFLAGS += --warn-undefined-variables
SHELL := bash

.PHONY: clean
clean:
	rm -rf public/ resources/
	rm .hugo_build.lock

.PHONY: draft
draft:
	hugo server run -D

.PHONY: run
run:
	hugo server run
