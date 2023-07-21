import pickle

with open("./model.pkl", 'rb') as f:
    model = pickle.load(f)


feats = [[0,0,0,0,0,0,0,0]]

feats = [[5000.998244,1,0,0,14496916779,24425419430,4537732291,22866275]]
#                                                         195403355440   36301858328    182930200
feats = [[25162.237936, 2250.0, 31.0, 0.0, 63590058102.0, 34544847947.0, 14846581017.0, 68622529336.0]]

feats_scale = [list(map(lambda x: x/60, feats[0]))]
print(feats_scale)
print(str( model.predict(feats_scale)  ))