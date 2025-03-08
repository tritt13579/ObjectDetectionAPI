def process_video(results):
    boxes = results[0].boxes.data.tolist()
    return [{"x": box[0], "y": box[1], "w": box[2], "h": box[3], "conf": box[4], "class": box[5]} for box in boxes]