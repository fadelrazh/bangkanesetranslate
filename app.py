from flask import Flask, render_template, request, jsonify
from keras.models import Model
import numpy as np
from tensorflow.keras.layers import Input, Dense, Embedding
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow as tf
import pickle
import keras as k

app = Flask(__name__, static_url_path='/static')

# Load the models and tokenizers
models = {
    'bn-id': {'model': '/Users/fadelrazsiah/Desktop/bangkanesetranslate/models/model_bn2id.h5',
              'src_tokenizer': '/Users/fadelrazsiah/Desktop/bangkanesetranslate/tokenizer/source_bn2id.pkl',
              'tgt_tokenizer': '/Users/fadelrazsiah/Desktop/bangkanesetranslate/tokenizer/target_bn2id.pkl',
              },
    'bn-en': {'model': '/Users/fadelrazsiah/Desktop/bangkanesetranslate/models/model_bn2en.h5',
              'src_tokenizer': '/Users/fadelrazsiah/Desktop/bangkanesetranslate/tokenizer/source_bn2en.pkl',
              'tgt_tokenizer': '/Users/fadelrazsiah/Desktop/bangkanesetranslate/tokenizer/target_bn2en.pkl',
              },
    'id-bn': {'model': '/Users/fadelrazsiah/Desktop/bangkanesetranslate/models/model_id2bn.h5',
              'src_tokenizer': '/Users/fadelrazsiah/Desktop/bangkanesetranslate/tokenizer/source_id2bn.pkl',
              'tgt_tokenizer': '/Users/fadelrazsiah/Desktop/bangkanesetranslate/tokenizer/target_id2bn.pkl',
              },
    'id-en': {'model': '/Users/fadelrazsiah/Desktop/bangkanesetranslate/models/model_id2en.h5',
              'src_tokenizer': '/Users/fadelrazsiah/Desktop/bangkanesetranslate/tokenizer/source_id2en.pkl',
              'tgt_tokenizer': '/Users/fadelrazsiah/Desktop/bangkanesetranslate/tokenizer/target_id2en.pkl',
              },
    'en-id': {'model': '/Users/fadelrazsiah/Desktop/bangkanesetranslate/models/model_en2id.h5',
              'src_tokenizer': '/Users/fadelrazsiah/Desktop/bangkanesetranslate/tokenizer/source_en2id.pkl',
              'tgt_tokenizer': '/Users/fadelrazsiah/Desktop/bangkanesetranslate/tokenizer/target_en2id.pkl',
              },
    'en-bn': {'model': '/Users/fadelrazsiah/Desktop/bangkanesetranslate/models/model_en2bn.h5',
              'src_tokenizer': '/Users/fadelrazsiah/Desktop/bangkanesetranslate/tokenizer/source_en2bn.pkl',
              'tgt_tokenizer': '/Users/fadelrazsiah/Desktop/bangkanesetranslate/tokenizer/target_en2bn.pkl',
              },
}

@app.route("/")
def index():
    return render_template("index.html")

# Load the tokenizers and models
for lang_pair in models.keys():
    with open(models[lang_pair]['src_tokenizer'], 'rb') as handle:
        models[lang_pair]['src_tokenizer'] = pickle.load(handle)
    with open(models[lang_pair]['tgt_tokenizer'], 'rb') as handle:
        models[lang_pair]['tgt_tokenizer'] = pickle.load(handle)
    models[lang_pair]['model'] = tf.keras.models.load_model(models[lang_pair]['model'])


@app.route('/translate', methods=['POST'])
def translate():
    src_input_text = request.form['source_text']
    src_lang = request.form['source_language']
    tgt_lang = request.form['target_language']
    lang_pair = src_lang + '-' + tgt_lang

    latent_dim = 50

    # inference encoder
    encoder_inputs_inf = models[lang_pair]['model'].input[0]
    encoder_outputs_inf, inf_state_h, inf_state_c = models[lang_pair]['model'].layers[4].output
    encoder_inf_states = [inf_state_h, inf_state_c]
    encoder = Model(encoder_inputs_inf, encoder_inf_states)

    # inference decoder
    decoder_state_h_input = Input(shape = (latent_dim,))
    decoder_state_c_input = Input(shape = (latent_dim,))
    decoder_state_input = [decoder_state_h_input, decoder_state_c_input]

    decoder_input_inf = models[lang_pair]['model'].input[1]
    decoder_emb_inf = models[lang_pair]['model'].layers[3](decoder_input_inf)
    decoder_lstm_inf = models[lang_pair]['model'].layers[5]
    decoder_output_inf, decoder_state_h_inf, decoder_state_c_inf = decoder_lstm_inf(decoder_emb_inf, initial_state= decoder_state_input)
    decoder_state_inf = [decoder_state_h_inf, decoder_state_c_inf]

    # inference dense layer
    dense_inf = models[lang_pair]['model'].layers[6]
    decoder_output_final = dense_inf(decoder_output_inf)
    decoder = Model([decoder_input_inf] + decoder_state_input, [decoder_output_final] + decoder_state_inf)

    reverse_word_map_target = dict(map(reversed, models[lang_pair]['tgt_tokenizer'].word_index.items()))

    def decode_seq(input_seq):
        state_values_encoder = encoder.predict([input_seq])
        target_seq = np.zeros((1, 1))
        target_seq[0, 0] = models[lang_pair]['tgt_tokenizer'].word_index['start']
        stop_condition = False
        decoder_sentance = ''
        while not stop_condition:
            sentance, decoder_h, decoder_c = decoder.predict([target_seq] + state_values_encoder)
            sample_word_index = np.argmax(sentance[0,-1,:])
            decoder_word = reverse_word_map_target[sample_word_index]
            decoder_sentance += ' ' + decoder_word
            if (decoder_word == 'end' or
                    len(decoder_sentance) > 70):
                stop_condition = True
            target_seq[0, 0] = sample_word_index
            state_values_encoder = [decoder_h, decoder_c]
        return decoder_sentance

    sentance = request.form['source_text']

    input_seq = models[lang_pair]['src_tokenizer'].texts_to_sequences([sentance])
    max_len = len(input_seq[0])
    pad_sequence = pad_sequences(input_seq, maxlen = max_len, padding = 'post')

    translation = decode_seq(pad_sequence)

    k.backend.clear_session()

    return render_template("index.html", translate = "{}".format(translation[:-3]), sentance = "{}".format(sentance))

if __name__ == '__main__':
    app.run(debug=True)

