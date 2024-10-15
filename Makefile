.PHONY: clean
clean:
	@rm -rf public/ resources/
	@rm .hugo_build.lock

.PHONY: run
run:
	@hugo server run
# @open http://localhost:1313/ && hugo server run
