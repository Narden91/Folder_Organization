import glob
import os
import numpy as np
import pandas as pd


def subjects_code_creation(SUBJECT_FOLDER: str, ANAGRAFICA_FILE: str, CODICI_FILE: str) -> None:
    """ Create the anagrafica_crc.csv and codici_crc.csv files"""

    anagrafica_file_list = []

    # # r=root, d=directories, f = files
    # for r, d, f in os.walk(SUBJECT_FOLDER):
    #     # print(f"Root: \n {r}")
    #     # print(f"Directory: \n {d}")
    #     for file in f:
    #         if file.endswith(".txt"):
    #             anagrafica_file_list.append(os.path.join(r, file))

    # List directories in the SUBJECT_FOLDER
    dirlist = [str(item) for item in os.listdir(SUBJECT_FOLDER) if os.path.isdir(os.path.join(SUBJECT_FOLDER, item))]

    # Check if exists a text file that has Anagrafica in the name for every subject
    for subject in dirlist:
        subject_path = SUBJECT_FOLDER + subject
        subject_anagrafica_file = glob.glob(subject_path + "/*Anagrafica*.txt")

        if not subject_anagrafica_file:
            print(f"Subject {subject} doesn't have an anagrafica file!")
        elif len(subject_anagrafica_file) > 1:
            print(f"Subject {subject} has more than one anagrafica file!")
            anagrafica_file_list.append(subject_anagrafica_file[0])
        else:
            # print(f"Anagrafica file for subject {subject} found! \n {subject_anagrafica_file}")
            anagrafica_file_list.append(subject_anagrafica_file)

    anagrafica_file_list = [item for sublist in anagrafica_file_list for item in sublist]

    try:

        schema_anagrafica = {'Id': str, 'Nome': str, 'Cognome': str, 'Sesso': str, 'Data_di_Nascita': str,
                             'Mano_dominante': str, 'Classe': str}

        anagrafica_df = pd.DataFrame(columns=schema_anagrafica.keys()).astype(schema_anagrafica)

        schema_codici = {'Id': str, 'Anno_1': str, 'Anno_2': str, 'Anno_3': str}

        code_df = pd.DataFrame(columns=schema_codici.keys()).astype(schema_codici)

        # Read every anagrafica file
        for num, anagrafica in enumerate(anagrafica_file_list):
            rows = []

            num += 1

            if num < 10:
                string_num = "00" + str(num)
            elif 10 <= num < 100:
                string_num = "0" + str(num)
            else:
                string_num = str(num)

            id_subject_code = "CRC_SUBJECT_" + string_num

            if num > 0:
                with open(anagrafica) as file:
                    for row in file:
                        # row = row.replace(" ", "")
                        rows.append(row.strip())

                # Rows are:
                name = rows[1].split(":", 1)[1]
                surname = rows[2].split(":", 1)[1]
                sex = rows[3].split(":", 1)[1]
                birthdate = rows[4].split(":", 1)[1]
                hand = rows[5].split(":", 1)[1]
                sclass = rows[6].split(":", 1)[1]
                id_folder_first_year = rows[9].split(":", 1)[1]

                personal_info_row = {
                    "Id": id_subject_code,
                    "Nome": name,
                    "Cognome": surname,
                    "Sesso": sex,
                    "Data_di_Nascita": birthdate,
                    "Mano_dominante": hand,
                    "Classe": sclass
                }

                code_row = {
                    "Id": id_subject_code,
                    "Anno_1": id_folder_first_year.strip(),
                    "Anno_2": "",
                    "Anno_3": ""
                }

                anagrafica_df = pd.concat([anagrafica_df, pd.DataFrame([personal_info_row])], ignore_index=True)

                code_df = pd.concat([code_df, pd.DataFrame([code_row])], ignore_index=True)

        print(anagrafica_df.to_string())

        anagrafica_df.to_csv(ANAGRAFICA_FILE, index=False)

        # Get all yeas columns
        year_columns = [col for col in code_df.columns if 'Anno' in col]

        # Remove spaces from year columns
        for col in year_columns:
            code_df[col] = code_df[col].str.replace(" ", "")

        # Save the codici_crc.csv file
        code_df.to_csv(CODICI_FILE, index=False)

    except Exception as e:
        print(f"{e}")

    return None
