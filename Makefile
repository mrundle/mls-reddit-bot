all: test ldist

build:
	python3 setup.py build

clean:
	python3 setup.py clean --all
	rm -rf build dist

# make .zip file for lambda layer
# there's some race condition bug in setuptools' WorkingSet.resolve()
#     used by lambda-setuptools, and it will just fail sometimes with
#     errno 17 (file exists). So here, just do a dumb retry up to
#     five attempts. Would be nice to understand and fix the root problem upstream. 
ldist:
	export DISTUTILS_DEBUG=1; \
	for i in $$(seq 1 5); do \
		if python3 setup.py ldist --build-layer=True --layer-dir=python/lib/python3.9/site-packages; then \
			echo "SUCCESS: lambda layer .zip created"; \
			exit 0; \
		fi; \
	done; \
	echo "ERROR: all attempts failed"; exit 1

dist:
	python3 setup.py sdist

.PHONY: test
test:
	#python3 setup.py test
	python3 -m pytest tests/
