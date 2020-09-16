1. Install:

```sh
python venv -m venv venv
source venv/bin/activate

pip install -r ./requirements.txt

cd ../../
python setup.py install
```

2. Convert model to pico-detect:

```sh
python load_model.py shape_predictor_5_face_landmarks.dat > model.txt
python convert.py model.txt ../pico-detect/models/shaper_5_face_landmarks.bin
```
