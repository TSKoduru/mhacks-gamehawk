# import onnxruntime as ort

# # qucik debug script
# import numpy as np
# sess = ort.InferenceSession("models/yoloactual.onnx", providers=["CPUExecutionProvider"])
# input_name = sess.get_inputs()[0].name
# dummy = np.random.rand(1, 3, 224, 224).astype(np.float32)

# try:
#     outputs = sess.run(None, {input_name: dummy})
# except Exception as e:
#     print(e)


from tensorflow.keras.models import load_model

ocr = load_model("models/ocr_model.h5")
print(ocr.input_shape)
