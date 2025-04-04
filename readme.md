# masterblaster

masterblaster builds centraxx stammdaten xml from yaml for sampletype
(probenart), messparameters and messprofil.

usage:

```
cat try/sampletype-fmt.yaml | masterblaster sampletype > sample-types.xml
```

for options, see `masterblaster -h`.

## sampletype (probenart)

option: `sampletype`.

format in `try/sampletype-fmt.yaml`.

## messparameter

option: `messparam`.

format in `try/messparam-fmt.yaml`.

## messprofil

option: `messprofil`.

format in `try/messprofil-fmt.yaml`.


## dev

compile with [ct](https://github.com/tnustrings/codetext):

```
cd masterblaster
ct main.ct
```

there is also a [vscode
plugin](https://marketplace.visualstudio.com/items?itemName=tnustrings.codetext)
for ct.

build:

```
python -m build
```

## todo

in sampletype material_code zu material string und den code aus der db fischen?