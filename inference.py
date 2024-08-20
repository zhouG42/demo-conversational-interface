import os
import logging
os.environ['TF_CPP_MIN_LOG_LEVEL']='2' # disable tensorflow from showing all debugging logs
import tensorflow as tf
tf.get_logger().setLevel(logging.ERROR)
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
#from nltk.corpus import stopwords


#sw_nltk = stopwords.words('english')
sw_nltk = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 
'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 
'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 
'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are',
 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 
'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 
'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 
'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 
'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 
's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y',
 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 
'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn',
 "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 
'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

sw_nltk.remove('on')
sw_nltk.remove('off')
sw_nltk.remove('is')
stop_words = sw_nltk


# Load primitive model weights and context
device_name = "hues"
context = np.load('./trained_model/{device}/word-context.npy'.format(device=device_name), allow_pickle=True).item()
max_encoder_seq_length = context['encoder_max_seq_length']
max_decoder_seq_length = context['decoder_max_seq_length']
num_encoder_tokens = context['num_encoder_tokens']
num_decoder_tokens = context['num_decoder_tokens']

# Load saved word index mappings
input_word2idx = np.load('./trained_model/{device}/word-input-word2idx.npy'.format(device=device_name), allow_pickle=True).item()
input_idx2word = np.load('./trained_model/{device}/word-input-idx2word.npy'.format(device=device_name), allow_pickle=True).item()
target_word2idx = np.load('./trained_model/{device}/word-target-word2idx.npy'.format(device=device_name), allow_pickle=True).item()
target_idx2word = np.load('./trained_model/{device}/word-target-idx2word.npy'.format(device=device_name), allow_pickle=True).item()

encoder_model = load_model('./trained_model/{device}/encoder-weights.h5'.format(device=device_name), compile=False)
decoder_model = load_model('./trained_model/{device}/decoder-weights.h5'.format(device=device_name), compile=False)


# Load compound model weights and context
device_name_compound = "sd_hue"
context_compound = np.load('./trained_model/{device}/word-context.npy'.format(device=device_name_compound), allow_pickle=True).item()
max_encoder_seq_length_compound = context['encoder_max_seq_length']
max_decoder_seq_length_compound = context['decoder_max_seq_length']
num_encoder_tokens_compound = context['num_encoder_tokens']
num_decoder_tokens_compound = context['num_decoder_tokens']

# Load saved word index mappings
input_word2idx_compound = np.load('./trained_model/{device}/word-input-word2idx.npy'.format(device=device_name_compound), allow_pickle=True).item()
input_idx2word_compound = np.load('./trained_model/{device}/word-input-idx2word.npy'.format(device=device_name_compound), allow_pickle=True).item()
target_word2idx_compound = np.load('./trained_model/{device}/word-target-word2idx.npy'.format(device=device_name_compound), allow_pickle=True).item()
target_idx2word_compound = np.load('./trained_model/{device}/word-target-idx2word.npy'.format(device=device_name_compound), allow_pickle=True).item()

encoder_model_compound = load_model('./trained_model/{device}/encoder-weights.h5'.format(device=device_name_compound), compile=False)
decoder_model_compound = load_model('./trained_model/{device}/decoder-weights.h5'.format(device=device_name_compound), compile=False)




# Decode based on text input
def generate_code(input_sentence): 
    input_seq = []
    input_wids = []
    input_sentence = input_sentence.lower().split()
    input_tokens = [tok for tok in input_sentence if tok not in stop_words]
    for word in input_tokens:
        idx = 1  # default idx 1 for <UNK>
        if word in input_word2idx:
            idx = input_word2idx[word]
        input_wids.append(idx)
    input_seq.append(input_wids)

    # pad to max encoder input length
    input_seq = pad_sequences(input_seq, max_encoder_seq_length)
    #print("input_seq_after_pad", input_seq)
    states_value = encoder_model.predict(input_seq, verbose=0)
    target_seq = np.zeros((1, 1, num_decoder_tokens))
    target_seq[0, 0, target_word2idx['<SOS>']] = 1
    target_text = ''
    target_text_len = 0
    terminated = False
    decoder_model.layers[-2].reset_states(states=states_value)

    while not terminated:
        output_tokens = decoder_model.predict(target_seq, verbose=0)
        sample_token_idx = np.argmax(output_tokens[0, -1, :])
        sample_word = target_idx2word[sample_token_idx]
        #print("output tokens: ", sample_word)

        target_text_len += 1

        if sample_word != '<SOS>' and sample_word != '<EOS>':
                target_text += '' + sample_word
        
        if sample_word == '<EOS>' or target_text_len >= max_decoder_seq_length:
            terminated = True 
        
        target_seq = np.zeros((1, 1, num_decoder_tokens))
        target_seq[0, 0, sample_token_idx] = 1   
    print(target_text.strip('.'))     
    return target_text.strip('.')



if __name__ == '__main__':
    print("Some examples of command --- code")
    generate_code("when button 3 released on streamdeck, turn on philips hue")
    #decode("hello how are you?")