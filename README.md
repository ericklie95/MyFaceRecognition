Library used:
- face_recognition - https://pypi.org/project/face-recognition/
pip install face_recognition
- dlib - https://github.com/davisking/dlib
pip install dlib

Instruction to install: https://github.com/ageitgey/face_recognition/issues/175#issue-257710508

Current feature:
- Read through pictures in folder called "known_face", compare result to all pictures in folder called "to_be_parsed".
- All pictures with no face detected will be moved to "outlier" folder - This is inaccurate.

To activate virtual environment:
- .\Scripts\activate

