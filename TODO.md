# To-do

1. Improve test coverage of `main.py`
1. Move all common test fixtures to `conftest.py` and streamline test code

## Test scenarios/ combinations for `update` command

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
