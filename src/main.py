# Face recognition using face_recognition library

import face_recognition
import os
import numpy as np 
    
def initialise():
    '''
    Make directory if not found.
    
    Tested on Windows 10.
    
    Enhancement:
    1. Ensure this is also working on Linux.
    '''
    currentWorkingDirectory = os.getcwd()
    
    knownPicDir = currentWorkingDirectory + "\\known_face"
    try:
        os.makedirs(knownPicDir)
    except FileExistsError:
        pass # directory exists.
    
    unknownPicDir = currentWorkingDirectory + "\\unknown_face"
    try:
        os.makedirs(unknownPicDir)
    except FileExistsError:
        pass # directory exists.
    
    noFaceFoundDir = currentWorkingDirectory + "\\face_not_found"
    try:
        os.makedirs(noFaceFoundDir)
    except FileExistsError:
        pass # directory exists.
    
    sortedDir = currentWorkingDirectory + "\\post_run_face_match"
    try:
        os.makedirs(sortedDir)
    except FileExistsError:
        pass # directory exists.
        
    return knownPicDir, unknownPicDir, noFaceFoundDir, sortedDir
    
def isFaceFound(imageFile):
    '''
    Check the imageFile if face is found by using face_location method.
    
    Param: imageFile = image file.
    
    Return:
        True = Image found.
        False = Image not found.
    '''
    image = face_recognition.load_image_file(imageFile)
    face_locations = face_recognition.face_locations(image)
    if not face_locations:
        return False
    return True

def removeFaceless(filename, unknownPicDir, noFaceFoundDir):
    '''
    Check if face is found on the chosen file. If face is not found, move it to directory called noFaceFoundDir.
    '''
    os.rename(unknownPicDir+"\\"+filename, noFaceFoundDir+"\\"+filename)
    #print("Move the file: "+ filename)

def findMatchingFace(knownFaceDict, unknownFaceDict, sortedDir, unknownPicDir):
    '''
    face_recognition.compare_faces(List x, numpy.ndarray y)
    x is List of numpy.ndarray
    y is numpy.ndarray
    
    To convert list to numpy.ndarray:
    array1 = np.asarray(list1)
    
    Currently, faceFilenameDict keys are tuples.
    So, change tuples to list.
    Then convert list to numpy.ndarray.
    
    Possible enhancement:
    1. Recognition of face that is found but not known yet then add it to the known face.
    2. Skip iterate over file that already loaded from json file.
    '''
    for i in knownFaceDict:
        known_face_name = knownFaceDict[i] # Get file name of known face. This will include extension.
        known_face_filename = os.path.splitext(known_face_name)[0] # extract just the filename withotu extension.
        knownList = []
        knownList.append(np.asarray(i)) # Assume there is only one face.
        for j in unknownFaceDict:
            fileMovedFlag = False
            check_fileName = unknownFaceDict[j]
            myList = []
            myList.append(np.asarray(j))
            for h in myList:
                result = face_recognition.compare_faces(knownList, h)
                if True in result:
                    try:
                        os.makedirs(sortedDir+"\\"+known_face_filename)
                    except FileExistsError:
                        pass # directory exists.
                    #print('Filename: {0} have the result: {1}.'.format(knownPic_filename, result)) # testing purposes.
                    os.rename(unknownPicDir+"\\"+check_fileName, sortedDir+"\\"+known_face_filename+"\\"+check_fileName) # Move known face to their directory
                    print("File moved to {0}".format(sortedDir+"\\"+known_face_filename+"\\"+check_fileName))          
                    fileMovedFlag = True
                    break
                    
            '''
            if fileMovedFlag: # With assumption that there are pictures with multiple faces in it.
                # Delete all dictionary entry that have the value as check_fileName
                # use of dict comprehension
                unknownFaceDict = {key:val for key, val in unknownFaceDict.items() if val != check_fileName}
            '''

def encodeAllPics(checkDir, noFaceFoundDir):
    '''
    Param:
    checkDir = Directory that is going to be checked.
    noFaceFoundDir = Directory where no face found is going to be stored.

    Return: dictionary
    key: tuple of numpy.ndarray
    value: name of file
    '''
    returnDict = {}
    for check_fileName in os.listdir(checkDir):
        # print("Current file check: {0} \\ {1}.".format(checkDir, check_fileName))
        if not isFaceFound(checkDir + "\\" + check_fileName):
            removeFaceless(check_fileName, checkDir, noFaceFoundDir)
        else:
            parsed_image = face_recognition.load_image_file(checkDir+"\\"+check_fileName)
            parsed_encoding = face_recognition.face_encodings(parsed_image)    
            for i in parsed_encoding:
                # require to use tuple, oherwise it'll give an error: TypeError: unhashable type: 'numpy.ndarray' 
                tuppleArr = tuple(i)
                returnDict[tuppleArr] = check_fileName
    return returnDict

def convertToFile(dictionary, filename):
    import pickle
    
    fp = open(filename, 'ab')
    pickle.dump(dictionary, fp)
    fp.close()
    
def main():
    print("Running Face Recognition")
    knownPicDir, unknownPicDir, noFaceFoundDir, sortedDir = initialise()

    # TODO: Read from file if available then add it to the dictionary of knownFaceDict if required.
    
    knownFaceDict = encodeAllPics(knownPicDir, noFaceFoundDir)
    unknownFaceDict = encodeAllPics(unknownPicDir, noFaceFoundDir)
    
    # Find matching face    
    findMatchingFace(knownFaceDict, unknownFaceDict, sortedDir, unknownPicDir)

    # Dump result to json
    convertToFile(knownFaceDict, "knownFaceDict.db") 
    convertToFile(unknownFaceDict, "unknownFaceDict.db")
        
    print("Finish running.")

if __name__ == "__main__":
    main()
    
def getKeyFromVal(dictionary, value):
    key = list(dictionary.keys())[list(dictionary.values()).index(value)]
    return key
    
def loadFromFile(filename):
    import pickle
    dbfile = open(filename, 'rb')
    returnDict = pickle.load(dbfile)
    dbfile.close()
    return returnDict