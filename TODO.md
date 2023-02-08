# To-do

Functionality

1. Proper default behaviour to NOT overwrite anything
1. Overwrite flag to overwrite
1. Delete flag to delete

Administrative

1. Fix badge creator so it doesn't need to contain the test command - take it as an input
1. Write tests for proper coverage
1. Make sure the automated tests work
1. ~~Enable dependabot~~
1. Figure out how to combine RELEASE-PLEASE and Poetry build publish (release-please separate, then build publish 'on release')
  Make sure we have a way to increment the version
1. Make repo public -> Enable sonarcloud
1. Make repo public -> Enable CodeQL

## GH Actions snippet for build/publish

```yaml
- name: Build and publish
  run: |
    poetry config pypi-token.pypi ${{ secrets.PYPI_TOKEN }}
    poetry publish --build --no-interaction --dry-run
```
