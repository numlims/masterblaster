
import sys
import yaml
import argparse
from dbcq import dbcq
from lxml.etree import tostring
from lxml.builder import E
from datetime import datetime
from traction import traction

def main():
  parser = argparse.ArgumentParser(description="generate stammdaten xml")
  parser.add_argument("what", help="sampletype|messparam|messprofil")
  # parser.add_argument("--yaml", help="read yaml", required=False)
  parser.add_argument("--db", help="db target", required=False)
  args = parser.parse_args()
  #yamlfile = "try/sample-type-nsn.yaml"
  #with open(yamlfile, "r") as file:
  #   data = yaml.safe_load(file)
  data = yaml.safe_load(sys.stdin)
  db = None
  if args.db:
    db = dbcq(args.db)
  e = None
  if args.what == "sampletype":
    e = sampletype(data)
  if args.what == "messparam":
    if db == None:
      print("error: messparam needs --db flag")
      exit
    e = messparam(data, db)
  if args.what == "messprofil":
    if db == None:
      print("error: messprofil needs --db flag")
      exit
    e = messprofil(data, db)
  if e != None:
    print(tostring(e, xml_declaration=True, encoding='utf-8', pretty_print=True).decode())
def sampletype(data):
  catalogue_data = E.CatalogueData()
  for d in data:
    # the hold-all
    item = E.SampleTypeCatalogueItem()

    # english name
    item.append(multilingual("en", d["name_en"]))

    # german name
    item.append(multilingual("de", d["name_de"]))

    # code
    item.append(E.Code(d["code"]))

    # kind
    item.append(E.Kind(d["kind"]))

    # sprec code
    item.append(E.SprecCode(d["sprec_code"]))

    # material todo fetch code from cxx
    item.append(E.MaterialCode(str(d["material_code"])))

    catalogue_data.append(item)
  return data_exchange(catalogue_data)
def messparam(data, db):
  tr = traction(db)
  vocab_by_code = tr.names_by_codes("usageentry", "de")
  groupname_by_code = tr.names_by_codes("laborvaluegroup", "de", ml_table="labval_grp_ml_name")
  item = E.FlexibleValueCatalogueItem()
  for param in data:
    kind = param["type"]
    if kind == "string":
      e = E.FlexibleStringValue()
    elif kind == "long-string":
      e = E.FlexibleLongStringValue()
    elif kind == "decimal":
      e = E.FlexibleDecimalValue()
    elif kind == "integer":
      e = E.FlexibleIntegerValue()
    elif kind == "boolean":
      e = E.FlexibleBooleanValue()
    elif kind == "date":
      e = E.FlexibleDateValue()
    elif kind == "long-date":
      e = E.FlexibleLongDateValue()
    elif kind == "enumeration":
      e = E.FlexibleEnumerationValue()
    elif kind == "optiongroup":
      e = E.FlexibleOptionGroupValue()
    elif kind == "catalog":
      e = E.FlexibleCatalogValue()
    else:
      print(f"error: type {kind} not recognized.")
      exit
    item.append(e)
    e.append(E.Code(param["code"]))
    name_en = param["name-en"] if "name-en" in param else param["code"]
    e.append(multilingual("en", name_en))
    name_de = param["name-de"] if "name-de" in param else name_en
    e.append(multilingual("de", name_de))
    if "group" in param:
      displayname = groupname_by_code[param[group]]
      e.append(E.LaborValueGroupRef(param["group"]), DisplayName=displayname)
    e.append(E.UserEntries(E.Systemwide("true")))
    if kind == "enumeration" or kind == "catalog" or kind == "optiongroup":
      if not "select" in param:
        print(f"error: kind {kind} needs a 'select' field with 'one' or 'many'")
        exit
      if param["select"] == "many":
        choicetype = "SELECTMANY"
      if param["select"] == "one":
        choicetype = "SELECTONE"
      e.append(E.ChoiseType(choicetype)) # sic ChoiseType
    if kind == "enumeration" or kind == "optiongroup":
      if not "options" in param:
        print(f"error: kind {kind} needs an 'options' field with a list of option codes.")
        exit
      for option in param["options"]:
        displayname = vocab_by_code[option]
        e.append(E.UsageEntryTypeRef(option, DisplayName=displayname))
    if kind == "catalog":
      if not "catalog" in param:
        print(f"error: kind {kind} needs a 'catalog' field with its catalog code.")
        exit
      if not "catalog-version" in param:
        print(f"error: kind {kind} needs a 'catalog-version' field with the catalog version.")
        exit

      e.append(E.UserDefinedCatalogRef(E.Code(param["catalog"]), E.Version(param["catalog-version"])))
  return data_exchange(E.CatalogueData(item))
def messprofil(data, db:dbcq):
  catalogue_data = E.CatalogueData()
  tr = traction(db)
  param_names_de = tr.names_by_codes("laborvalue", "de")
  for profil in data:
    item = E.FlexibleDataSetCatalogueItem()
    item.append(E.Code(profil["code"]))
    item.append(multilingual("en", profil["name_en"]))
    item.append(multilingual("de", profil["name_de"]))
    for section in profil["sections"]:
      for param in section["params"]:
        flexref = E.FlexibleValueComplexRefs()
        item.append(flexref)
        flexref.append(E.FlexibleValueRef(param["code"], DisplayName=param_names_de[param["code"]])) 
        required = param["required"] if "required" in param else False
        flexref.append(E.Required(boolstring(required)))
    item.append(E.Systemwide("true"))
    item.append(E.FlexibleDataSetType("MEASUREMENT"))
    item.append(E.Category("GENERAL"))
    templateref = E.CrfTemplateRef()
    templateref.append(E.Name(profil["name_de"]))
    templateref.append(E.Version("1"))
    item.append(templateref)
    catalogue_data.append(item)
    crf_template = E.CrfTemplate()
    crf_template.append(E.Name(profil["name_de"]))
    for i_section, section in enumerate(profil["sections"]):
      crfsection = E.CrfTemplateSection()
      crf_template.append(crfsection)
      # take the code as the general name?
      crfsection.append(E.Name(section["code"]))
      crfsection.append(multilingual("en", section["name_en"]))
      crfsection.append(multilingual("de", section["name_de"]))
      crfsection.append(E.Code(section["code"]))
      for i, param in enumerate(section["params"]):
        field = E.CrfTemplateField()

        # the display name german?
        field.append(E.LaborValue(param["code"], DisplayName=param_names_de[param["code"]]))

        field.append(E.LowerRow(str(i)))
        # we don't do columns, just set 0
        field.append(E.LowerColumn(str(0)))

        # what's the difference between lower and upper row?
        field.append(E.UpperRow(str(i)))
        field.append(E.UpperColumn(str(0)))

        # todo what's needed of these?
        field.append(E.Mandatory("false"))
        field.append(E.VisibleCaption("true"))

        field.append(E.FieldType("LABORVALUE"))

        # todo what's needed of these?
        field.append(E.TabIndex("0"))
        field.append(E.ReadOnly("false"))

        crfsection.append(field)
      
      n = len(section["params"])
      crfsection.append(E.Height(str(n)))
      crfsection.append(E.Width(str(1)))
      
      crfsection.append(E.Position(str(i_section)))
      
      # todo needed?
      crfsection.append(E.CrfSectionType("PLAIN"))
      crfsection.append(E.IsChangeable("true"))
    crf_template.append(E.TemplateType("LABORMETHOD"))
    crf_template.append(E.Version("1")) # same version as in CrfTemplateRef
    catalogue_data.append(crf_template)
  return data_exchange(catalogue_data)
def data_exchange(child):
  dataexchange = E.CentraXXDataExchange()
  dataexchange.attrib['xmlns'] = "http://www.kairos-med.de"
  dataexchange.append(E.Source("CENTRAXX"))
  dataexchange.append(E.SourceVersion("3.18.3.16"))
  dataexchange.append(E.ExportDate(datetime.now().astimezone().isoformat())) 
  dataexchange.append(child)
  return dataexchange
def multilingual(lang, value):
  e = E.NameMultilingualEntries()
  e.append(E.Lang(lang))
  e.append(E.Value(value))
  return e
def boolstring(b:bool):
  if not b:
    return "false"
  return "true"

sys.exit(main())
