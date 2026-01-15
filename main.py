import functions as f
import pandas as pd
import re
from datetime import datetime

input_csv = r"path/to/addresses/.csv" #path to csv
output_csv = r"path/to/output/.csv"
delimiter = ';' #define delimiter that is used in csv file
df = pd.read_csv(input_csv, sep = delimiter) #read csv into dataframe
postcode_column = 'postcode' #name of postal code column in csv
housenumber_column = 'hsn_number' #name of housenumber column in csv
houseletter_column = 'hsn_letter' #None if doesn't exist
houseaddition_column = None #None if doesnt exist


x_list = [] #initialize empty list to store address x coordinates
y_list= [] #initialize empty list to store address y coordinates
address_count = len(df)
count = 0
notfound_count = 0
start_time = datetime.now()
for index,row in df.iterrows():
    count += 1
    postcode = row[postcode_column]
    postcode = postcode.replace(" ", "")

    
    #try housenumber conversion to integer, else look for address without housenumber
    try: housenumber = int(row[housenumber_column])
    except: housenumber = None #set housenumber to "None" so the address search will not return results and coordinates will be set to "Not found"
    
    #try to find houseletter if column is specified
    if houseletter_column is not None:
        houseletter = row[houseletter_column]
        if str(houseletter) == 'nan':
            houseletter = ''
    else: houseletter = ''
    
    #try to find houseaddition if column is specified
    if houseaddition_column is not None:
        houseaddition = row[houseaddition_column]
        if str(houseaddition) == 'nan':
            houseaddition = ''
    else: houseaddition = ''  

    #print progress
    if count % 10 == 0:
        print(f'Fetching coords for address {count} / {address_count}')
        if count % 100 == 0:
            end_time = datetime.now()
            remaining_time = ((end_time - start_time) * (len(df) - count) / 100)
            print(f'Estimated time remaining: {str(remaining_time).split(".")[0]}')
            start_time = datetime.now()
    
    ###########SEARCH BLOCK###############
    #first search with all columns specified
    coords = f.get_coordinates(postcode, housenumber, houseletter, houseaddition)
    #if address is not found and houseaddition exists, search again without houseaddition (so only housenumber + houseletter(if it exists))
    if coords == False and houseaddition != '':
        print('houseaddition not found, retrying search without houseaddition')
        houseaddition_empty = ''
        coords = f.get_coordinates(postcode, housenumber, houseletter, houseaddition_empty)
    
    #if address is still  not found and both houseletter and houseaddition exists, search without houseletter but with addition
    if coords == False and houseletter != '' and houseaddition != '':
        print('houseletter not found, retrying search without houseletter but with houseaddition')
        houseletter_empty = ''
        coords = f.get_coordinates(postcode, housenumber, houseletter_empty, houseaddition)
    
    #if address is still not found and houseletter exists, search only based on housenumber (not letter/addition)
    if coords == False and houseletter != '':
        print('houseletter not found, retrying with only housenumber')
        houseletter_empty = ''
        houseaddition_empty = ''
        coords = f.get_coordinates(postcode, housenumber, houseletter_empty, houseaddition_empty)

    ###########SEARCH BLOCK END###############

    #if address is still not found, append 'NOT FOUND' to x and y coordinate lists
    if coords == False:
        print(f'Address {postcode} {housenumber} not found')
        x_list.append('NOT FOUND')
        y_list.append('NOT FOUND')
        notfound_count +=1
    #if address is found, regular expressions search for the RD coordinates and append them to the x/y lists
    else:
        match = re.search(r"POINT\(([-\d.]+) ([-\d.]+)\)", coords) #rd (not WGS84) is specified in coordinate fetch function, no need to specify here
        x, y = map(float, match.groups())
        x_list.append(x)
        y_list.append(y)


print(f'Amount of addresses found: {count-notfound_count}')
print(f'Amount of addresses not found: {notfound_count}')
df['X'], df['Y'] = x_list,y_list

df.to_csv(output_csv,sep=';',index=False)



print("done")
