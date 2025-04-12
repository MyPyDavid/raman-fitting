# Default recipe to display help information
default:
  @just --list

[group('pytest')]
pytest:
  pytest tests/

[group('pytest')]
pytest-all:
  pytest -m "slow" tests/

[group('pytest')]
pytest-debug:
  pytest -s -v --pdb --log-level=DEBUG -m "slow" tests/


[group('docker')]
docker-build:
  docker build -t raman-fitting-image .

[group('docker')]
docker-run:
  docker run -it raman-fitting-image

[group('docker')]
docker-run-cli +args:
  docker run -it raman-fitting-image {{args}}

[group('docker')]
docker-debug:
  docker run -it --entrypoint /bin/bash raman-fitting-image
