# Face recognition using face_recognition library

import face_recognition
import os
from pathlib import Path

'''Global Variables'''
currentWorkingDirectory = os.getcwd()

def main():
    print("Running Face Recognition")
    knownDir = parseDir = outlierDir = ""
    knownDir, parseDir, outlierDir = initialise()
    
    # Remove all faceless picture.
    removeFaceless(parseDir, outlierDir)
   
    # Find matching face
    findMatchingFace(knownDir, parseDir)


def initialise():
    '''
    Make directory if not found.
    '''
    knownDir = currentWorkingDirectory + "\\known_face"
    try:
        os.makedirs(knownDir)
    except FileExistsError:
        pass # directory exists.
    
    parseDir = currentWorkingDirectory + "\\to_be_parsed"
    try:
        os.makedirs(parseDir)
    except FileExistsError:
        pass # directory exists.
    
    outlierDir = currentWorkingDirectory + "\\outlier"
    try:
        os.makedirs(outlierDir)
    except FileExistsError:
        pass # directory exists.
        
    return knownDir, parseDir, outlierDir
    
def isFaceFound(imageFile):
    image = face_recognition.load_image_file(imageFile)
    face_locations = face_recognition.face_locations(image)
    if not face_locations:
        return False
    return True

def removeFaceless(parseDir, outlierDir):
    '''
    For every files in the parseDir:
        check if face exists
    '''
    for filename in os.listdir(parseDir):
        if not isFaceFound(parseDir + "\\" + filename):
            Path(parseDir+"\\"+filename).rename(outlierDir+"\\"+filename)
            #os.rename(parseDir+"\\"+filename, outlierDir)
            print("Move the file: "+ filename)

def findMatchingFace(knownDir, parseDir):
    '''
    For every picture in knownDir:
        For every picture in parseDir:
            if picture in parseDir have the same encoding as picture in knownDir:
                Rename file to be the same as picture in knownDir+number
                Goal:
                make a directory by the name of th efile in knownDir if it has not been created
                move the file to the new direcory
                
                
    Possible enhancement:
    1. Get multiple different pictures of a known person to be applied on 2nd run (after new directory is created).
    '''
    for knownPic_filename in os.listdir(knownDir):
        known_image = face_recognition.load_image_file(knownDir+"\\"+knownPic_filename)
        known_encoding = face_recognition.face_encodings(known_image)[0]
        i = 0
        for check_fileName in os.listdir(parseDir):
            parsed_image = face_recognition.load_image_file(parseDir+"\\"+check_fileName)
            parsed_encoding = face_recognition.face_encodings(parsed_image)[0]
            oldExt = os.path.splitext(check_fileName)[1]
            
            result = face_recognition.compare_faces([known_encoding], parsed_encoding)[0]
            if result:
                #print('Filename: {0} have the result: {1}.'.format(knownPic_filename, result))
                os.rename(parseDir+"\\"+check_fileName, parseDir+"\\"+knownPic_filename+"_"+str(i)+oldExt)
                i += 1
        
            # Make directory if directory doesn't exist.
            # Path(currentWorkingDirectory+"\\"+knownPic_filename).mkdir(parent=True, exist_ok=True)
            
if __name__ == "__main__":
    main()