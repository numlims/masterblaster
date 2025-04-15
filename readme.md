# masterblaster

masterblaster builds centraxx stammdaten xml from yaml for sampletype
(probenart), laborvalue (messparameter) and labormethod (messprofil).

usage:

```
cat fmt/sampletype-fmt.yaml | masterblaster sampletype > sample-types.xml
```

for options, see `masterblaster -h`.

## sampletype (probenart)

option: `sampletype`.

format in `fmt/sampletype-fmt.yaml`.

## labval (messparameter)

option: `messparam`.

format in `fmt/messparam-fmt.yaml`.

## method (messprofil)

option: `messprofil`.

format in `fmt/messprofil-fmt.yaml`.


## dev

compile with [ct](https://github.com/tnustrings/codetext):

```
cd masterblaster
ct main.ct
```

in the [vscode
plugin](https://marketplace.visualstudio.com/items?itemName=tnustrings.codetext) use `ct: assemble`.

build:

```
python -m build
```

## todo

in sampletype material_code zu material string und den code aus der db fischen?