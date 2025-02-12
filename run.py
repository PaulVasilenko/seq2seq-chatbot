#! /usr/bin/python
# -*- coding: utf-8 -*-

import tensorflow as tf
import tensorlayer as tl
from data.twitter import data
from tensorlayer.models.seq2seq import Seq2seq

def initial_setup(data_corpus):
    metadata, idx_q, idx_a = data.load_data(PATH='data/{}/'.format(data_corpus))
    (trainX, trainY), (testX, testY), (validX, validY) = data.split_dataset(idx_q, idx_a)
    trainX = tl.prepro.remove_pad_sequences(trainX.tolist())
    trainY = tl.prepro.remove_pad_sequences(trainY.tolist())
    testX = tl.prepro.remove_pad_sequences(testX.tolist())
    testY = tl.prepro.remove_pad_sequences(testY.tolist())
    validX = tl.prepro.remove_pad_sequences(validX.tolist())
    validY = tl.prepro.remove_pad_sequences(validY.tolist())
    return metadata, trainX, trainY, testX, testY, validX, validY


if __name__ == "__main__":
    data_corpus = "discordbot"

    # data preprocessing
    metadata, trainX, trainY, testX, testY, validX, validY = initial_setup(data_corpus)

    # Parameters
    src_len = len(trainX)
    tgt_len = len(trainY)

    assert src_len == tgt_len

    batch_size = 32
    n_step = src_len // batch_size
    src_vocab_size = len(metadata['idx2w'])  # 8002 (0~8001)
    emb_dim = 1024

    word2idx = metadata['w2idx']  # dict  word 2 index
    idx2word = metadata['idx2w']  # list index 2 word

    unk_id = word2idx['unk']  # 1
    pad_id = word2idx['_']  # 0

    start_id = src_vocab_size  # 8002
    end_id = src_vocab_size + 1  # 8003

    word2idx.update({'start_id': start_id})
    word2idx.update({'end_id': end_id})
    idx2word = idx2word + ['start_id', 'end_id']

    src_vocab_size = tgt_vocab_size = src_vocab_size + 2

    num_epochs = 50
    vocabulary_size = src_vocab_size


    def inference(seed, top_n):
        model_.eval()
        seed_id = [word2idx.get(w, unk_id) for w in seed.split(" ")]
        sentence_id = model_(inputs=[[seed_id]], seq_length=20, start_token=start_id, top_n=top_n)
        sentence = []
        for w_id in sentence_id[0]:
            w = idx2word[w_id]
            if w == 'end_id':
                break
            sentence = sentence + [w]
        return sentence


    decoder_seq_length = 20
    model_ = Seq2seq(
        decoder_seq_length=decoder_seq_length,
        cell_enc=tf.keras.layers.GRUCell,
        cell_dec=tf.keras.layers.GRUCell,
        n_layer=3,
        n_units=256,
        embedding_layer=tl.layers.Embedding(vocabulary_size=vocabulary_size, embedding_size=emb_dim),
    )

    # Uncomment below statements if you have already saved the model

    load_weights = tl.files.load_npz(name='model.npz')
    tl.files.assign_weights(load_weights, model_)

    optimizer = tf.optimizers.Adam(learning_rate=0.001)
    model_.train()

    seeds = ["привет",
             "придется применить",
             "дынную атаку"]

    for seed in seeds:
        print("Query >", seed)
        top_n = 3
        for i in range(top_n):
            sentence = inference(seed, top_n)
            print(" >", ' '.join(sentence))






