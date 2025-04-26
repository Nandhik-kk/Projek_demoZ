import streamlit as st
from transformers import pipeline

# Judul aplikasi
st.title("🦄 Aplikasi Deteksi Emosi Teks")

# Instruksi penggunaan
st.markdown("""
Masukkan teks yang ingin Anda analisis emosinya di bawah ini.
Aplikasi ini akan memprediksi emosi yang terkandung dalam teks tersebut.
""")

# Memuat model emotion detection
@st.cache_resource
def load_emotion_model():
    return pipeline('text-classification', 
                   model='joeddav/distilbert-base-uncased-go-emotions-student', 
                   return_all_scores=True)

emotion_classifier = load_emotion_model()

# Input teks dari pengguna
user_input = st.text_area("Masukkan teks di sini:", "Saya sangat senang hari ini!")

if st.button("Analisis Emosi"):
    if user_input:
        # Melakukan prediksi
        results = emotion_classifier(user_input)
        
        # Mengolah hasil
        emotions = results[0]
        
        # Menampilkan hasil utama
        top_emotion = max(emotions, key=lambda x: x['score'])
        st.subheader(f"Emosi Utama: {top_emotion['label']} ({top_emotion['score']:.2%})")
        
        # Menampilkan semua skor emosi dalam bentuk diagram batang
        st.subheader("Detail Skor Emosi:")
        
        # Membuat dictionary untuk emosi dan skornya
        emotion_dict = {e['label']: e['score'] for e in emotions}
        
        # Menampilkan diagram batang
        st.bar_chart(emotion_dict)
        
        # Menampilkan tabel detail
        st.write("Detail Skor:")
        for emotion in emotions:
            st.write(f"- {emotion['label']}: {emotion['score']:.2%}")
    else:
        st.warning("Masukkan teks terlebih dahulu!")
