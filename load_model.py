import tensorflow as tf
from keras.applications.vgg16 import preprocess_input
import os

os.environ['TF_CPP_MIN_LOG_LEVEL']='3'

# 모델 불러오기
model = tf.keras.models.load_model('model/10cycle.h5')

def predict(image_file):
  # 이미지 로드 (path는 추후 수정해도 될 듯)
  path=image_file
  image_arr = tf.keras.preprocessing.image.load_img(path, target_size=(224, 224))

  # numpy array로 전환
  image_arr = tf.keras.preprocessing.image.img_to_array(image_arr)

  # model에 맞춰서 reshape()
  image_arr = image_arr.reshape((1, image_arr.shape[0], image_arr.shape[1], image_arr.shape[2]))

  # VGG model에 맞는 image로 변환
  image_arr = preprocess_input(image_arr)

  yhat = model.predict(image_arr)
  answer=yhat.argmax() # 가장 큰 값을 정답값으로 생각하자!!!

  result = {
    0: "glass",
    1: "metal",
    2: "paper",
    3: "plastic"
  }

  return result.get(answer)

  #코드 피드백 받기전 코드
  # if answer==0:
  #   return "glass"
  # elif answer==1:
  #   return "metal"
  # elif answer==2:
  #   return "paper"
  # elif answer==3:
  #   return "plastic"

# pred = predict('image/hwarang.jpeg')
# print(pred)
