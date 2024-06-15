# Face recognition using face_recognition library

import face_recognition
import os
import numpy as np 
from datetime import datetime
    
def initialise():
    '''
    Make directory in current working directory.
    '''
    # Enhancement: Use of os.path.exists instead of try except.
    
    knownPicDir = os.path.join(os.getcwd(), "known_face")
    try:
        os.makedirs(knownPicDir)
    except FileExistsError:
        pass # directory exists.
    
    unknownPicDir = os.path.join(os.getcwd(), "unknown_face")
    try:
        os.makedirs(unknownPicDir)
    except FileExistsError:
        pass # directory exists.
    
    noFaceFoundDir = os.path.join(os.getcwd(), "face_not_found")
    try:
        os.makedirs(noFaceFoundDir)
    except FileExistsError:
        pass # directory exists.
    
    sortedDir = os.path.join(os.getcwd(), "post_run_face_match")
    try:
        os.makedirs(sortedDir)
    except FileExistsError:
        pass # directory exists.
        
    return knownPicDir, unknownPicDir, noFaceFoundDir, sortedDir
    
def isFaceFound(imageFile):
    '''
    Check the imageFile if face is found by using face_location method.
    
    Param: [Required] imageFile = image file.
    
    Return:
        True = Image found.
        False = Image not found.
    '''
    image = face_recognition.load_image_file(imageFile)
    face_locations = face_recognition.face_locations(image)
    if not face_locations:
        return False
    return True

def moveFile(filename, pathToSourceDir, pathToDestDir):
    # Move filename from pathToSourceDir to pathToDestDir    
    os.rename(os.path.join(pathToSourceDir,filename), os.path.join(pathToDestDir,filename))

def findMatchingFace(knownFaceDict, unknownFaceDict, sortedDir, unknownPicDir):
    '''
    Description: Iterate through all known faces and compare to each pictures that need to be identified/compared.

    Param:
    [Required] knownFaceDict = dictionary of all known faces encoded.
    [Required] unknownFaceDict = dictionary of all unknown faces encoded.
    [Required] sortedDir = path to directory where matching faces stored.
    [Required] unknownPicDir = path to directory where the unknown pictures are located.
    '''
    
    # Check all encodings for known faces.
    for i in knownFaceDict:
        # Get file name of known face. This will include extension.
        known_face_name = knownFaceDict[i] 
        
        # Extract filename without extension.
        known_face_filename = os.path.splitext(known_face_name)[0]
        
        # Put the encoding to a list, with assumption there is only one face.
        knownList = []
        knownList.append(np.asarray(i))
        
        # Loop through all encoded pictures within dictionary.
        for j in unknownFaceDict:
            # Get file name of known face. This will include extension.
            check_fileName = unknownFaceDict[j]
            
            # Convert the value back to ns.numpyndarray, required for compare_faces method.
            h = np.asarray(j)
            
            # Compare faces.
            result = face_recognition.compare_faces(knownList, h)
            
            # When face matches
            if True in result:
            
                # Create directory of sortedDir if directory does not exist.
                if not os.path.exists(os.path.join(sortedDir, known_face_filename)):
                    os.makedirs(os.path.join(sortedDir, known_face_filename))
                
                # Move the face to the specified directory.
                try:
                    #TESTING: the following is where the movement happens.
                    
                    #os.rename(unknownPicDir+"\\"+check_fileName, sortedDir+"\\"+known_face_filename+"\\"+check_fileName) # Move known face to their directory
                    print("File moved to {0}".format(sortedDir+"\\"+known_face_filename+"\\"+check_fileName))          
                except:
                    # Could go here if the file has been moved and the file has 2 faces?
                    print("Error: Possible that there are 2 faces on the filename: {0}.".format(check_fileName))
            

def getAllValues(dictionary):
    return list(dictionary.values())
 
def convertToFile(dictionary, filename):
    import pickle
        
    fp = open(filename, 'wb')
    pickle.dump(dictionary, fp)
    fp.close()
 

def encodeAllPics(pathToSourceDir, pathToDestDir, savedDict={}, dumpDirectory=""):
    '''
    Param:
    [Required] pathToSourceDir = Path to directory for images needed to be encoded.
    [Required] pathToDestDir = Directory where no face found is going to be stored.
    [Optional] savedDict = Saved dictionary of known faces
    [Optional] dumpDirectory = Path to directory where the encoding will be dumped every 10 pictures.

    Return: dictionary
    key: tuple of numpy.ndarray
    value: name of file
    '''
    
    returnDict = {}
    # tmpDict meant to only have up 10 entries at all time.
    tmpDict = {}
    knownFaceListName = []
    counter = 0
    
    # If we have a saved dictionary
    if(savedDict):
        returnDict = savedDict
        knownFaceListName = getAllValues(savedDict)
        
    for filename in os.listdir(pathToSourceDir):
        # Skip if filename already listed within savedDict.
        if(filename in knownFaceListName):
            print("Found {0}. Skipping..".format(filename))
            continue
            
        
        # Move image to another directory if face is not found.
        pathToFile = os.path.join(pathToSourceDir, filename)
        if not isFaceFound(pathToFile):
            moveFile(filename, pathToSourceDir, pathToDestDir)
        else:
            parsed_image = face_recognition.load_image_file(pathToFile)
            parsed_encoding = face_recognition.face_encodings(parsed_image)    
            for i in parsed_encoding:
                tuppleArr = tuple(i) 
                # Update tmpDictionary.
                tmpDict[tuppleArr] = filename
            counter += 1
            
        # After every 10 pictures & dump the result.
        if(counter % 10 == 0):
            # Get the current date and time
            current_datetime = datetime.now()

            # Format the date and time as a string
            formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
            
            # Concatenate the filename
            pathToDirectory = os.path.join(os.getcwd(), dumpDirectory)
            newDbFile = os.path.join(pathToDirectory, formatted_datetime)

            # Convert the tmpDictionary to file.
            convertToFile(tmpDict, newDbFile)
            
            # Update the main dictionary with the temporary dictionary.
            returnDict.update(tmpDict)
            
            # Reset tmpDictionary
            tmpDict = {}
            
    return returnDict


def loadFromFile(pathToFile):
    import pickle
    
    try:
        dbfile = open(pathToFile, 'rb')
        returnDict = pickle.load(dbfile)
        dbfile.close()
        return returnDict
    except:
        print("{0} not found!".format(pathToFile))
        return {}
        
def loadFromDir(directoryName):
    '''
    param: [Required] directoryName : String.
    '''
    returnDict = {}
    
    # Join the current directory path with the new directory name
    pathToDir = os.path.join(os.getcwd(), directoryName)
    
    # Check if the directory already exists
    if not os.path.exists(pathToDir):
        os.makedirs(pathToDir)
        print("{0} not found! Creating it..".format(pathToDir))

    # Read all files and combined dictionaries
    for i in os.listdir(pathToDir):
        tmpDict = loadFromFile(os.path.join(pathToDir,i))
        returnDict.update(tmpDict)
        
    return returnDict
    
def main():
    print("Running Face Recognition")
    knownPicDir, unknownPicDir, noFaceFoundDir, sortedDir = initialise()

    # Current hard-coded values for creating files and directory.
    filenameForKnownFace = "knownFaceDict.db"
    filenameForUnknownFace = "unknownFaceDict.db"
    unknownFaceDbDir = "unknownfacedb"
    
    pathToKnownDbFile = os.path.join(os.getcwd(), filenameForKnownFace)
    savedKnownFaceDict = loadFromFile(pathToKnownDbFile)
    if(not savedKnownFaceDict):
        savedKnownFaceDict = {}
        
    pathToKnownDbFile = os.path.join(os.getcwd(), filenameForUnknownFace)
    savedUnknownFaceDict = loadFromFile(pathToKnownDbFile)
    pathToKnownDbDir = os.path.join(os.getcwd(), unknownFaceDbDir)
    savedUnknownFaceDict = loadFromDir(pathToKnownDbDir)
    if(not savedUnknownFaceDict):
        savedUnknownFaceDict = {}
    
    # Encode all known pictures and store it to a file when finished.
    knownFaceDict = encodeAllPics(knownPicDir, noFaceFoundDir, savedKnownFaceDict)
    convertToFile(knownFaceDict, filenameForKnownFace) 

    # Encode all unknown pictures and store it to a file when finished.
    unknownFaceDict = encodeAllPics(unknownPicDir, noFaceFoundDir, savedUnknownFaceDict, unknownFaceDbDir)
    pathToFile = os.path.join(pathToKnownDbDir, filenameForUnknownFace)
    convertToFile(unknownFaceDict, pathToFile)
    
    # Find matching face based on the 2 encodings that we have done.
    findMatchingFace(knownFaceDict, unknownFaceDict, sortedDir, unknownPicDir)    
        
    print("Finish running.")

if __name__ == "__main__":
    main()
    
def getKeyFromVal(dictionary, value):
    key = list(dictionary.keys())[list(dictionary.values()).index(value)]
    return key