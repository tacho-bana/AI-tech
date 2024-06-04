from flask import Flask, render_template, request, jsonify, send_file
import numpy as np
import scipy.io.wavfile as wavfile
import csv
import io

app = Flask(__name__)

def load_morse_code_dict(filename):
    morse_code_dict = {}
    with open(filename, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            character = row['Character'].strip()
            morse_code = row['MorseCode'].strip()
            morse_code_dict[character] = morse_code
    return morse_code_dict

def to_morse_code(text, morse_code_dict):
    text = text.upper()
    morse_code = ''
    for char in text:
        if char in morse_code_dict:
            morse_code += morse_code_dict[char] + ' '
        else:
            morse_code += '? '  # 未定義の文字は「?」とします。
    return morse_code.strip()

def generate_morse_audio(morse_code, dot_duration=0.1, dash_duration=0.3, frequency=800.0, sample_rate=44100):
    audio = np.array([], dtype=np.float32)
    for symbol in morse_code:
        if symbol == '.':
            tone = np.sin(2 * np.pi * np.arange(sample_rate * dot_duration) * frequency / sample_rate).astype(np.float32)
        elif symbol == '-':
            tone = np.sin(2 * np.pi * np.arange(sample_rate * dash_duration) * frequency / sample_rate).astype(np.float32)
        else:
            tone = np.zeros(int(sample_rate * dot_duration), dtype=np.float32)
        
        audio = np.concatenate((audio, tone, np.zeros(int(sample_rate * dot_duration), dtype=np.float32)))
    
    # メモリ内に音声ファイルを生成
    virtual_file = io.BytesIO()
    wavfile.write(virtual_file, sample_rate, audio)
    virtual_file.seek(0)
    return virtual_file

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_sound', methods=['POST'])
def generate_sound():
    input_text = request.form['input_text']
    morse_code_dict = load_morse_code_dict('morse_code.csv')
    morse_code = to_morse_code(input_text, morse_code_dict)
    print(f"モールス信号: {morse_code}")
    audio_file = generate_morse_audio(morse_code)
    return send_file(audio_file, mimetype='audio/wav')

if __name__ == '__main__':
    app.run(debug=True)


