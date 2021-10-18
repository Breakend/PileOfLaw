# code to parse existing states code (files taken from google drive )
# previously web scrapped files in google drive are downloaded as 4 zip files
# these zip files are processed to extract state codes in the required format

# some previously downloaded files had errors. these were filtered out


OUT_PATH = "./state_codes_processed"

ZIP_FILE_NAMES = ["state codes-001.zip", "state codes-002.zip", "state codes-003.zip", "state codes-004.zip" ]
#ZIP_FILE_NAMES = ["state codes-004.zip"] #for testing purposes use one zip at a time

TIME_STAMP = "SEP 19 2021"  # check the format

# initalize list of out dictionary
processed_out_json_data_list = []
TRAIN_VAL_SPLIT = 0.75

for zfile in ZIP_FILE_NAMES:
  print (f'$$$ Processing {zfile} $$$ ')
  zip_obj = zipfile.ZipFile(zfile, "r")
  file_list = zip_obj.namelist()
  # process each json file. Some state directories are empty. Check for such empty dirs
  for ind_file in file_list:
    # check if it is a json file (indirect check for empty dirs)
    # utah seems to have docx file
    if (ind_file.split(".")[-1] != "json"):
      print (f"** ERROR - NOT JSON FILE {ind_file}")
      continue

    # Process and EXTRACT data from valid json files
    # parse state + year from file name (included in the output json)
    print(f" #### Processing File  {ind_file}  ")
    state_name_year = ind_file.split("/")[-1].split(".")[0]

    ## FOLLOWING FILES HAVE BAD JSON DATA
    # TEMP FIX - VERMON JSON files cause problems
    if (state_name_year.split("_")[0] == "vermont"):
      continue
    # montana uses Parts / part between chapter and section
    if (state_name_year.split("_")[0] == "montana"):
      continue
    if (state_name_year == "south-carolina_2012"):
      continue

    if (state_name_year == "south-carolina_2016"):
      continue
    if (state_name_year == "rhode-island_2015"):
      continue
    if (state_name_year == "rhode-island_2017"):
      continue    
    # virginia_2010 contains no sections etc.
    if (state_name_year == "virginia_2010"):
      continue
      # following file appears to contain corrupt data
    if (state_name_year == "new-jersey_2009"):
      continue
    # following error: JSONDecodeError: Extra data: line 91677 column 82 (char 53145327)
    if (state_name_year == "nevada_2017"):
      continue
   # following error: JSONDecodeError: Extra data: line 78290 column 960 (char 55217349)
    if (state_name_year == "arkansas_2014"):
      continue

    # following error: JSONDecodeError: Expecting value: line 25394 column 17 (char 17952954)
    if (state_name_year == "minnesota_2013"):
      continue
    if (state_name_year == "alabama_2012"):
      continue
    # following error: JSONDecodeError: Extra data: line 73520 column 33 (char 52552334)

    # read the content of the json file
    file_content = zip_obj.read(ind_file).decode("utf-8")
    # in python (nested) dictionary format
    file_content_dict = json.loads(file_content)
    # all_text holds all the text into a single long string (for output json)
    all_text = ""

    # some existing json files have Chapters -> Sections -> section format
    # Tennesse has Chapters -> Chapter -> Sections -> section
    # some others have just Sections -> section (no Chapters)
    # alaska uses secs instead of sections 
    # TO DO: montana has  parts and part 

    # some have sects instead of sections
    if (isinstance(file_content_dict, list)) and (isinstance(file_content_dict[0], dict)):
      top_keys = file_content_dict[0].keys()
      if "link" in top_keys:
        needed_link = file_content_dict[0]["link"]   # for output 
      if "chapters" in top_keys:
        # go to one level down look for sections
        # multiple sections - need to parse here
        for sect_elem in file_content_dict[0]["chapters"]:
          sub_keys = sect_elem.keys()
          if not sect_elem:
            print (f" *** Empty dict hit --  {ind_file}")
            continue
          if "raws" in sub_keys:
            to_parse_sections.append(sect_elem)
            continue

          if "sections" in sub_keys:
            to_parse_sections = sect_elem["sections"]
          elif "secs" in sub_keys:
            to_parse_sections = sect_elem["secs"]
          else:
            print (f"*** subkeys {sub_keys} ")
            print (f"*** ERROR - No Sections under Chapters in {ind_file}    ")
      elif "sections" in top_keys:
        to_parse_sections = file_content_dict[0]["sections"]

      # to_parse_sections has the list of all sections, combine texts from all section elements

    # some section (especially the last one) is empty - check for these
    for ind_sect in to_parse_sections:
      if ind_sect:
        if "raws" in ind_sect.keys():
          all_text = all_text + " "+ " ".join(ind_sect['raws'])

    # create dictionary for output

    out_dict = {}
    out_dict ["url"] = needed_link   # should the key be url or link
    out_dict ["text"] = all_text
    #out_dict ["created_timestamp"] = TIME_STAMP
    out_dict ["created_timestamp"] = datetime.date.today().strftime("%m-%d-%Y")
    out_dict ["downloaded_timestamp"] = datetime.date.today().strftime("%m-%d-%Y")
    out_dict ["state_year"] = state_name_year
    processed_out_json_data_list.append(out_dict)

## split test and train
splitting_index = int(len(processed_out_json_data_list) * TRAIN_VAL_SPLIT)
train = processed_out_json_data_list [ :splitting_index]
val = processed_out_json_data_list [splitting_index: ]

train_file_name = os.path.join(OUT_PATH, "train.states_code.jsonl")
val_file_name = os.path.join(OUT_PATH, "val.states_code.jsonl")
# writes to current directory on the drive for testing
#train_file_name = "train.states_code.jsonl"
#val_file_name = "val.states_code.jsonl"

with open(train_file_name, "w") as out_file:
    for o in train: 
        out_file.write(json.dumps(o) + "\n")
print(f"Written {len(train)} documents to {train_file_name}")

with open(val_file_name, "w") as out_file:
    for o in val: 
        out_file.write(json.dumps(o) + "\n")
print(f"Written {len(val)} documents to {val_file_name}")
