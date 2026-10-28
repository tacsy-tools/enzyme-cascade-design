
if False:
  import pathlib

  # read all rules in current directory
  for file_path in pathlib.Path("./Rules").glob("*.gml"):
    if file_path.name == 'rules.gml': continue
    print(f'reading {file_path.name}')
    Rule.fromGMLFile(str(file_path))

else:
  r0 = Rule.fromGMLFile("./Rules/rules_61.gml") 
  r1 = Rule.fromGMLFile("./Rules/rules_62.gml")
  r2 = Rule.fromGMLFile("./Rules/rules_63.gml")
  r3 = Rule.fromGMLFile("./Rules/rules_64.gml")
  r4 = Rule.fromGMLFile("./Rules/rules_50.gml")
  r5 = Rule.fromGMLFile("./Rules/rules_46.gml")
  r6 = Rule.fromGMLFile("./Rules/rules_54.gml")
  r7 = Rule.fromGMLFile("./Rules/rules_6.gml")
  r8 = Rule.fromGMLFile("./Rules/rules_12.gml")
  r9 = Rule.fromGMLFile("./Rules/rules_52.gml")
  r10 = Rule.fromGMLFile("./Rules/rules_51.gml")
  r11 = Rule.fromGMLFile("./Rules/rules_56.gml")
  r12 = Rule.fromGMLFile("./Rules/rules_55.gml")
  r13 = Rule.fromGMLFile("./Rules/rules_60.gml")
  r14 = Rule.fromGMLFile("./Rules/rules_67.gml")
  r15 = Rule.fromGMLFile("./Rules/rules_68.gml")
  r16 = Rule.fromGMLFile("./Rules/ATP_regen.gml")
  r17 = Rule.fromGMLFile("./Rules/rules_70.gml")
  r18 = Rule.fromGMLFile("./Rules/rules_71.gml")
