.PHONY: clean
clean:
	@rm -rf public
	@rm .hugo_build.lock

.PHONY: run
run:
	@hugo server run
