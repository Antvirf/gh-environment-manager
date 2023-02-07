# To-do

1. Fix badge creator so it doesn't need to contain the test command - take it as an input
1. Write tests to get 100% coverage
1. Make sure the automated tests work
1. Enable dependabot
1. Figure out how to combine RELEASE-PLEASE and Poetry build publish
1. Refactor main function to reduce complexity
1. Make repo public -> Enable sonarcloud
1. Make repo public -> Enable CodeQL

## GH Actions snippet for build/publish

```yaml
- name: Build and publish
  run: |
    poetry config pypi-token.pypi ${{ secrets.PYPI_TOKEN }}
    poetry publish --build --no-interaction
```
