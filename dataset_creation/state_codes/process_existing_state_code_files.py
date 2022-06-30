import zipfile
import json
import datetime
import random
try:
    import lzma as xz
except ImportError:
    import pylzma as xz
# code to parse existing states code (files taken from google drive )
# previously web scrapped files in google drive are downloaded as 4 zip files
# these zip files are processed to extract state codes in the required format

# some previously downloaded files had errors. these were filtered out
url = "https://drive.google.com/drive/folders/1pwCK380GHW-0d6C5k-CF1YdGgYXu32Hj?usp=sharing"

OUT_PATH = "./cache/"

template = "./cache/state codes-20211024T223516Z-00{n}.zip"
ZIP_FILE_NAMES = [template.format(n=n) for n in range(1, 5)]
#ZIP_FILE_NAMES = ["state codes-004.zip"] #for testing purposes use one zip at a time


# initalize list of out dictionary
processed_out_json_data_list = []
TRAIN_VAL_SPLIT = 0.75
overwrite = True
open_type = 'w' if overwrite else 'a'
train_f = xz.open("./cache/train.state_code.xz", open_type)
val_f = xz.open("./cache/validation.state_code.xz", open_type)
def _unroll(file_content_dict):
    text = ""
    if isinstance(file_content_dict, list):
        for _thing in file_content_dict:
            text += _unroll(_thing) + "\n"
    elif isinstance(file_content_dict, dict):
        for key, _thing in file_content_dict.items():
            if key == "link":
                continue
            else:
                text += _unroll(_thing) + "\n"
    else:
        text += file_content_dict + "\n"
        
    return text


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
    #     # montana uses Parts / part between chapter and section
    #     if (state_name_year.split("_")[0] == "montana"):
    #       continue
    if (state_name_year == "south-carolina_2012"):
        continue

    if (state_name_year == "south-carolina_2016"):
        continue
    if (state_name_year == "rhode-island_2015"):
        continue
    if (state_name_year == "rhode-island_2017"):
        continue    
    # virginia_2010 contains no sections etc.
    # if (state_name_year == "virginia_2010"):
    #     continue
    #       # following file appears to contain corrupt data
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

    # some existing json files have Chapters -> Sections -> section format
    # Tennesse has Chapters -> Chapter -> Sections -> section
    # some others have just Sections -> section (no Chapters)
    # alaska uses secs instead of sections 
    # TO DO: montana has  parts and part 

    # some have sects instead of sections
    all_text = _unroll(file_content_dict)

    
    # if (isinstance(file_content_dict, list)) and (isinstance(file_content_dict[0], dict)):
    #   top_keys = file_content_dict[0].keys()
    #   if "link" in top_keys:
    #     needed_link = file_content_dict[0]["link"]   # for output 
    #   if "chapters" in top_keys:
    #     # go to one level down look for sections
    #     # multiple sections - need to parse here
    #     for sect_elem in file_content_dict[0]["chapters"]:
    #       sub_keys = sect_elem.keys()
    #       if not sect_elem:
    #         print (f" *** Empty dict hit --  {ind_file}")
    #         continue
    #       if "raws" in sub_keys:
    #         to_parse_sections.append(sect_elem)
    #         continue

    #       if "sections" in sub_keys:
    #         to_parse_sections = sect_elem["sections"]
    #       elif "secs" in sub_keys:
    #         to_parse_sections = sect_elem["secs"]
    #       else:
    #         print (f"*** subkeys {sub_keys} ")
    #         print (f"*** ERROR - No Sections under Chapters in {ind_file}    ")
    #   elif "sections" in top_keys:
        # to_parse_sections = file_content_dict[0]["sections"]

      # to_parse_sections has the list of all sections, combine texts from all section elements

    # some section (especially the last one) is empty - check for these
    # for ind_sect in to_parse_sections:
    #   if ind_sect:
    #     if "raws" in ind_sect.keys():
    #       all_text = all_text + " "+ " ".join(ind_sect['raws'])

    # create dictionary for output
    out_dict = {}
    out_dict ["url"] = url   # should the key be url or link
    out_dict ["text"] = all_text
    #out_dict ["created_timestamp"] = TIME_STAMP
    out_dict ["created_timestamp"] = ind_file.split("_")[-1].replace(".json", "")
    out_dict ["downloaded_timestamp"] = datetime.date.today().strftime("%m-%d-%Y")
    out_dict ["state_year"] = state_name_year

    if random.random() > .75:
        val_f.write((json.dumps(out_dict) + "\n").encode("utf-8"))
    else:
        train_f.write((json.dumps(out_dict) + "\n").encode("utf-8"))
