import os
import cv2
from flask import Flask, request, redirect, render_template, flash
from werkzeug.utils import secure_filename
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.preprocessing import image

import numpy as np


#classes = ["0","1","2","3","4","5","6","7","8","9"]
image_size = 28

UPLOAD_FOLDER = "uploads"
INTERMEDIATE_FOLODER = "intermediates"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#model = load_model('./model.h5')#学習済みモデルをロード
model_vgg16 = load_model('./modelvgg16_64_18_adam.h5')#学習済みモデルをロード
model_vgg16_normal = load_model('./modelvgg16_64_18_adam_N.h5')#学習済みモデルをロード
#カスケード型分類器に使用する分類器のデータ（xmlファイル）を読み込み
#HAAR_FILE = R"C:\Users\ejpks\Application\python\Driver Drowsiness\PythonCode\source\haarcascade_eye_tree_eyeglasses.xml"
HAAR_FILE = R".\haarcascade_eye_tree_eyeglasses.xml"
cascade = cv2.CascadeClassifier(HAAR_FILE)

@app.route('/', methods=['GET', 'POST'])
# 画像を一枚受け取り、OPEN_EYEかCLOSE_EYEを判定して返す関数
# def pred_gender(img):
#     img = cv2.resize(img, (82,82))
#     img = img.astype('float32') / 255
#     img = np.expand_dims(img, axis=0)
#     pred = model.predict(img)
#     if np.argmax(pred) == 0:
#         return 'OPEN_EYE'
#     else:
#         return 'CLOSE_EYE'



# def upload_file():
#     if request.method == 'POST':
#         if 'file' not in request.files:
#             flash('ファイルがありません')
#             return redirect(request.url)
#         file = request.files['file']
#         if file.filename == '':
#             flash('ファイルがありません')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(UPLOAD_FOLDER, filename))
#             filepath = os.path.join(UPLOAD_FOLDER, filename)

#             #受け取った画像を読み込み、np形式に変換
#             img = cv2.imread(filepath)
#             img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#             img = cv2.resize(img_rgb, (82,82))
#             img = img.astype('float32') / 255
#             img = np.expand_dims(img, axis=0)
#             pred = model.predict(img)
#             if np.argmax(pred) == 0:
#                 result = 'OPEN_EYE'    
#             else:
#                 result = 'CLOSE_EYE'

# #            plt.imshow(img)
# #            plt.show()
# #            print(pred_gender(img)) 
# #            img = image.img_to_array(img)
# #            data = np.array([img])
# #            #変換したデータをモデルに渡して予測する
# #            result = model.predict(data)[0]
# #            predicted = result.argmax()
#             pred_answer = "これは " + result + " です"

#             return render_template("index.html",answer=pred_answer)

#     return render_template("index.html",answer="")
def upload_file():
    vgg16_count = 0
    vgg16_normal_count = 0
    vgg16_status = ''
    vgg16_normal_status = ''
    vgg16_drowsiness_level = ''
    vgg16_normal_drowsiness_level = ''
    if request.method == 'POST':
        if 'files' not in request.files:
            flash('ファイルがありません')
            return redirect(request.url)
        file = request.files['files']
        if file.filename == '':
            flash('ファイルがありません')
            return redirect(request.url)
        files = request.files.getlist('files')  # 'files'はinputタグのname属性
        for file in files:
            def get_drowsiness_level(close_count ,totalcount):
                persent = close_count / totalcount * 100
                if persent >= 98:
                    return '居眠り'
                if persent >= 75:
                    return 'かなり眠たい'
                if persent >= 25:
                    return '眠たい'
                if persent >= 5:
                    return 'やや眠たい'
                return '覚醒'            
            # ここでファイルを処理する
            # 例: ファイルを保存する、画像解析を行うなど
            print(file)
            print(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            face = cv2.imread(filepath,0)

            eye = cascade.detectMultiScale(face)
 
            #顔の座標を表示する

            if eye is None:
                print('CLOSE_EYE')
                continue
            try:
                x,y,w,h = eye[0]
            except IndexError:
                print('CLOSE_EYE')
                continue      
            # if eye[0] is None:
            #     print(eye[1])
            #     x,y,w,h = eye[1]
            # else:
            #     print(eye[0])
            #     x,y,w,h = eye[0]
            #顔部分を切り取る

            eye_cut = face[y-h//3:y+h*10//8, x-w//3:x+w*10//8]
#            eye_cut = img[y:y+h, x:x+w]
#            eye_cut = img[y-w//2:y+w//2, x:x+w]
            #白枠で顔を囲む
#            x,y,w,h = eye[0]
            cv2.rectangle(face,(x-w//2,y-h//2),(x+w*10//8,y+h*10//8),(255,255,255),2)
 
            #cv2.rectangle(img,(x,y-w//2),(x+w,y+w//2),(255,255,255),2)
 
            #画像の出力
            filepath = "eye_"+file.filename
            filepath = os.path.join(INTERMEDIATE_FOLODER, filepath)
            cv2.imwrite(filepath, eye_cut)
            filepath = 'face_'+file.filename
            filepath = os.path.join(INTERMEDIATE_FOLODER, filepath)
            cv2.imwrite(filepath, face)
            #ヒストグラム平坦化
            eye_cut_hist = cv2.equalizeHist(eye_cut)
            cv2.imwrite(filepath, eye_cut_hist)        
            img_rgb = cv2.cvtColor(eye_cut_hist, cv2.COLOR_BGR2RGB)   
#            img_rgb = cv2.cvtColor(eye_cut, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img_rgb, (82,82))
            img = img.astype('float32') / 255
            img = np.expand_dims(img, axis=0)
            pred = model_vgg16.predict(img)
            if np.argmax(pred) == 0:
                result = 'OPEN_EYE'    

            else:
                result = 'CLOSE_EYE'
#
#           VGG16
#
            pred = model_vgg16.predict(img)
            if np.argmax(pred) == 0:
                result_vgg16 = 'OPEN_EYE'    
            else:
                result_vgg16 = 'CLOSE_EYE'
            filepath = 'face_vgg16'+result_vgg16+file.filename
            filepath = os.path.join(INTERMEDIATE_FOLODER, filepath)
            cv2.imwrite(filepath, face)
            pred_answer = 'vgg16:'+file.filename+ "は、" + result_vgg16
            print(pred_answer)
#
#           VGG16 NORMALIZATION
#
            pred = model_vgg16_normal.predict(img)
            if np.argmax(pred) == 0:
                result_vgg16_normal = 'OPEN_EYE'    
            else:
                result_vgg16_normal = 'CLOSE_EYE'
            filepath = 'face_vgg16_normal'+result_vgg16_normal+file.filename
            filepath = os.path.join(INTERMEDIATE_FOLODER, filepath)
            cv2.imwrite(filepath, face)
            pred_answer = 'vgg16_normal:'+file.filename+ "は、" + result_vgg16_normal
            print(pred_answer)
            pred_answer = file.filename+ "は、" + result
            print(pred_answer)
#           vgg16
            if result_vgg16 == "CLOSE_EYE":
                vgg16_count = vgg16_count +1
                vgg16_status += 'C'
            else:
                vgg16_status += 'O'
            vgg16_drowsiness_level = get_drowsiness_level(vgg16_count,len(files))
#           vgg16 normalization
            if result_vgg16_normal == "CLOSE_EYE":
                vgg16_normal_count = vgg16_normal_count + 1
                vgg16_normal_status += 'C'
            else:
                vgg16_normal_status += 'O'
            vgg16_normal_drowsiness_level = get_drowsiness_level(vgg16_normal_count,len(files))
            VGG16_RESULT =                  "転移学習VGG16非正規：クローズ数／枚数　"+ str(vgg16_count)+"/"+ str(len(files))+"   " + vgg16_drowsiness_level +vgg16_status[:10]
            VGG16_NORMAL_RESULT =           "転移学習VGG16正規  ：クローズ数／枚数　"+ str(vgg16_normal_count)+"/"+ str(len(files))+"   "+ vgg16_normal_drowsiness_level+vgg16_normal_status[:10]        
        return render_template("index.html",answer=VGG16_RESULT,answer2 = VGG16_NORMAL_RESULT) 
    return render_template("index.html",answer="")
# if __name__ == "__main__":
#     app.run()
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host ='0.0.0.0',port = port)