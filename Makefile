install: git-init
.PHONY: install

git-init:
	git submodule init
	git submodule update
.PHONY: git-init
