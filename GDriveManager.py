from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def print_files(drive, file_list):
    print("-----------")
    for file1 in file_list:
        print('title: %s, id: %s' % (file1['title'], file1['id'])) 

def find_file(drive, file_list, filename):
    for file1 in file_list:
        if file1['title'] == filename:
            return file1
    return None

def create_folder(drive, foldername):
    folder = drive.CreateFile({'title' : foldername, 'mimeType' : 'application/vnd.google-apps.folder'})
    folder.Upload()
    return folder

def create_file(drive, filename, parent_id):
    file1 = drive.CreateFile({'title': filename, "parents":  [{"kind": "drive#fileLink","id": parent_id}]})
    file1.Upload()
    return file1

def update_file(drive, save_file, content):
    save_file.SetContentFile(content)
    save_file.Upload()
    print("Save file was updated!")

def load_file(drive, save_file):
    save_file.GetContentFile("saved_game.json")
    print("Save file was loaded!")
    
def init_drive():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()

    # find 2048 folder and get folder id
    folder = find_file(drive, file_list, "2048_saves")
    # create 2048 folder if not found
    if folder == None:
        folder = create_folder(drive, "2048_saves")
        print("2048_saves folder created")
    folder_id = folder['id']
    print("2048_saves folder accessed")

    # find 2048 save file (saved_game.json)
    _2048_file_list = drive.ListFile({'q': "'{}' in parents and trashed=false".format(folder_id)}).GetList()
    save_file = find_file(drive, _2048_file_list, "saved_game.json")
    # create save file if not found
    if save_file == None:
        save_file = create_file(drive, "saved_game.json", folder_id)
        print("saved_game.json created")
    print("saved_game.json accessed")
    return drive, folder, save_file

if __name__ == '__main__':
    drive, folder, save_file = init_drive()



