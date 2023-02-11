# To-do

Functionality

1. ~~Proper default behaviour to NOT overwrite anything~~
1. ~~Overwrite flag to overwrite~~
1. ~~Delete flag to delete~~
1. ~~Restructure again to simplify main.py~~
1. ~~Add pylint step to workflow~~
1. ~~Enable dependabot~~
1. Write tests for proper coverage and automate them
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
