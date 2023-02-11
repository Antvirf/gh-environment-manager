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

## Test levels

1. Separate out test flow, run on Windows, Mac and Linux
1. Unit tests (use pycov to track)
1. Functional tests
  Scenario combinations
    read
      flags: none
    fetch
      flags: output
      combinations: 2
    update
      flags: overwrite, delete-nonexisting, delete-nonexisting-without-prompt
      combinations: 2x2x2 = 8

### Option combinations for `update`

scenario|overwrite flag? |delete flag? |delete-without-prompt flag?|Expected outcome after run
|--|--|--|--|--|
1 | ❌ | ❌ | ❌ | DEFAULT BEHAVIOUR: GH env updated ONLY for entities in YAML that are NOT in GH. No deletions.
2 | ❌ | ✅ | ❌ | GH env updated ONLY for entities in YAML that are NOT in GH. Entities not in YAML are deleted, WITH a prompt.
3 | ❌ | ❌ | ✅ | GH env updated ONLY for entities in YAML that are NOT in GH. Entities not in YAML are deleted, WITHOUT prompt.
4 | ❌ | ✅ | ✅ | Same as #3, though somewhat nonsensical to provide both deletion flags.
5 | ✅ | ✅ | ✅ | GH env == YAML env, WITHOUT a prompt. (i.e. full sync + delete what's not there)
6 | ✅ | ❌ | ❌ | GH env updated for each entity in YAML. Entities NOT in YAML are NOT changed, and NOT deleted.
7 | ✅ | ✅ | ❌ | GH env updated for each entity in YAML. Entities NOT in YAML are overwritten, WITH a prompt.
8 | ✅ | ❌ | ✅ | GH env updated for each entity in YAML. Entities NOT in YAML are overwritten, WITHOUT a prompt.
