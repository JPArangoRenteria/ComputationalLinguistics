def data_collection(filepath):
    return

def is_argot(word):
    return
def detection_process(word):
    return
def text_processing(filepath):
    file = open(filepath, 'r')
    lines = file.readlines
    argot_detect = []
    for line in lines:
        words = line.split()
        for word in words:
            argot_detect.append(word)
    return argot_detect
