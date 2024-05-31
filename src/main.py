# Face recognition using face_recognition library

import face_recognition
import os
from pathlib import Path

'''Global Variables'''
currentWorkingDirectory = os.getcwd()
faceFilenameDict = {}

def main():
    print("Running Face Recognition")
    knownPicDir, unknownPicDir, noFaceFoundDir, sortedDir = initialise()
   
    # Find matching face
    findMatchingFace(knownPicDir, unknownPicDir, noFaceFoundDir, sortedDir)

    print("Finish running. Printing dict: {0}".format(faceFilenameDict))
    
def initialise():
    '''
    Make directory if not found.
    
    Tested on Windows 10.
    
    Enhancement:
    1. Ensure this is also working on Linux.
    '''
    
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

def findMatchingFace(knownPicDir, unknownPicDir, noFaceFoundDir, sortedDir):
    '''
    For every picture in knownPicDir:
        For every picture in unknownPicDir:
            If face not found:
                remove picture to no face directory
            If face found:
                if picture in unknownPicDir have the same encoding as picture in knownPicDir:
                    Rename file to be the same as picture in knownPicDir+number
                    Goal:
                    make a directory by the name of th efile in knownPicDir if it has not been created
                    move the file to the new direcory
                
                
    Possible enhancement:
    1. Get multiple different pictures of a known person to be applied on 2nd run (after new directory is created).
    '''
    for knownPic_filename in os.listdir(knownPicDir):
        known_image = face_recognition.load_image_file(knownPicDir+"\\"+knownPic_filename)
        known_encoding = face_recognition.face_encodings(known_image) # face_recognition.face_encodings(known_image)[0] # Initial test, this assumes there is only 1 face in a picture.
        known_face_name = os.path.splitext(knownPic_filename)[0] # get File Name of the file of known face.
        for check_fileName in os.listdir(unknownPicDir):
            #print("Current file check: {0}".format(check_fileName))
            fileMovedFlag = False
            if not isFaceFound(unknownPicDir + "\\" + check_fileName):
                removeFaceless(check_fileName, unknownPicDir, noFaceFoundDir)
            else:
                parsed_image = face_recognition.load_image_file(unknownPicDir+"\\"+check_fileName)
                parsed_encoding = face_recognition.face_encodings(parsed_image)
                
                for i in parsed_encoding: # Parse through all possible encodings in unknwownPicDir
                    result = face_recognition.compare_faces(known_encoding, i) # True if face matches.
                    #print("Result: {0}.i:{1}.".format(result, i[0]))
                    if True in result:
                        try:
                            os.makedirs(sortedDir+"\\"+known_face_name)
                        except FileExistsError:
                            pass # directory exists.
                        #print('Filename: {0} have the result: {1}.'.format(knownPic_filename, result)) # testing purposes.
                        os.rename(unknownPicDir+"\\"+check_fileName, sortedDir+"\\"+known_face_name+"\\"+check_fileName) # Move known face to their directory
                        print("File moved to {0}".format(sortedDir+"\\"+known_face_name+"\\"+check_fileName))
                        fileMovedFlag = True
                        break
                        
                if not fileMovedFlag:
                    for i in parsed_encoding:
                        # require to use tuple, oherwise it'll give an error: TypeError: unhashable type: 'numpy.ndarray' 
                        tuppleArr = tuple(i)
                        faceFilenameDict[tuppleArr] = check_fileName

if __name__ == "__main__":
    main()