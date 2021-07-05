"""
Overview of commands used for testing and coverage
run commands examples
        pytest --cov=app
    --cov check if it is folder or package
    pytest --cov=fizzbuzz
    --cov-report=term-missing
        shows the terms that are missing

    --cov-branch branch
        coverage, where conditionals
        require a double  coverage

    use # pragma: no cover
        to iqnore coverage test for that code block

    pytest --cov --cov-report=term-missing

with coverage only:
    coverage run -m unittest discover
    coverage combine
    coverage xml
    coverage report -m
    coverage report -m --skip-covered

"""
