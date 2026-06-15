import os
import re
import urllib.request
import pandas as pd
import numpy as np
import joblib

# Aspek kata kunci untuk fallback keyword matching dan sentimen klausa
ASPECT_KEYWORDS = {
    'aspek_rasa': ['kopi', 'minuman', 'rasa', 'enak', 'pahit', 'manis', 'es', 'susu', 'roti', 'menu', 'cup', 'kualitas', 'asin', 'gurih', 'cokelat', 'latte', 'matcha', 'boba', 'tawar', 'encer', 'pekat', 'panas', 'dingin'],
    'aspek_harga': ['harga', 'mahal', 'murah', 'promo', 'diskon', 'cashback', 'ovo', 'gopay', 'shopeepay', 'worth', 'saku', 'pas', 'hemat', 'paket', 'pahe', 'mehong'],
    'aspek_pelayanan': ['pelayanan', 'layan', 'kasir', 'barista', 'staff', 'karyawan', 'ramah', 'sopan', 'jutek', 'galak', 'cuek', 'etika', 'respect', 'sapa', 'senyum', 'baik', 'mbak', 'mas'],
    'aspek_kecepatan': ['lama', 'cepat', 'antri', 'nunggu', 'lambat', 'tunggu', 'antrean', 'gercep', 'lelet', 'durasi', 'menit', 'jam', 'kelewat'],
    'aspek_kebersihan': ['bersih', 'kotor', 'toilet', 'tempat', 'nyaman', 'ac', 'meja', 'kursi', 'suasana', 'rapi', 'cozy', 'wfc', 'colokan', 'colok', 'sejuk', 'dingin', 'berisik', 'luas', 'sempit', 'sofa'],
    'aspek_stok': ['habis', 'stok', 'menu', 'sedia', 'kosong', 'varian', 'kehabisan', 'ready', 'sold', 'out'],
    'aspek_aplikasi': ['app', 'aplikasi', 'grab', 'gojek', 'gofood', 'grabfood', 'order', 'pesan', 'sistem', 'pickup', 'kiosk', 'kks', 'down', 'error', 'apk']
}

# 1. Unduh InSet Lexicon
def download_inset_lexicon():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    for file_name in ['positive.tsv', 'negative.tsv']:
        target_path = os.path.join(data_dir, file_name)
        if not os.path.exists(target_path):
            url = f"https://raw.githubusercontent.com/fajri91/InSet/master/{file_name}"
            print(f"Mengunduh InSet Lexicon: {file_name} ke {target_path}...")
            try:
                urllib.request.urlretrieve(url, target_path)
            except Exception as e:
                print(f"[WARN] Gagal mengunduh {file_name}: {e}")

# 2. Muat data kamus sentimen
def load_lexicon():
    download_inset_lexicon()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pos_path = os.path.join(base_dir, 'data', 'positive.tsv')
    neg_path = os.path.join(base_dir, 'data', 'negative.tsv')
    
    lexicon = {}
    if os.path.exists(pos_path) and os.path.exists(neg_path):
        try:
            pos_df = pd.read_csv(pos_path, sep='\t')
            neg_df = pd.read_csv(neg_path, sep='\t')
            for _, row in pos_df.iterrows():
                lexicon[str(row['word']).lower()] = float(row['weight'])
            for _, row in neg_df.iterrows():
                lexicon[str(row['word']).lower()] = float(row['weight'])
            print(f"Lexicon dimuat. Total {len(lexicon)} kata.")
            return lexicon
        except Exception as e:
            print(f"[WARN] Gagal membaca lexicon dari {pos_path}: {e}")
    print("[ERROR] File lexicon positive/negative tidak ditemukan!")
    return {}

# 3. Potong kalimat menjadi klausa & hitung skor sentimen
def split_into_clauses(text):
    if not isinstance(text, str):
        return []
    parts = re.split(r'[.,;!?\n]+', text)
    clauses = []
    for p in parts:
        subparts = re.split(r'\b(tapi|namun|tetapi|sedangkan|padahal|meskipun|walaupun|lalu|kemudian)\b', p, flags=re.IGNORECASE)
        clauses.extend([sp.strip() for sp in subparts if sp.strip()])
    return clauses

def get_sentiment_for_clause(clause_text, lexicon):
    words = str(clause_text).lower().split()
    score = sum(lexicon.get(w, 0.0) for w in words)
    if score > 0:
        return 'positive'
    elif score < 0:
        return 'negative'
    else:
        return 'neutral'

# 4. Fungsi inference utama
def run_absa_inference(texts, original_texts, aspect_model, tfidf_vectorizer, lexicon):
    """
    Ekstraksi aspek multi-label & penentuan sentimen per-aspek.
    """
    aspect_cols = list(ASPECT_KEYWORDS.keys())
    pred_aspects = np.zeros((len(texts), len(aspect_cols)), dtype=int)
    
    if aspect_model is not None and tfidf_vectorizer is not None:
        try:
            features = tfidf_vectorizer.transform(texts)
            pred_aspects = aspect_model.predict(features)
        except Exception as e:
            print(f"[WARN] Gagal memprediksi dengan model ML, beralih ke keyword matching. Error: {e}")
            aspect_model = None
            
    if aspect_model is None:
        # Fallback ke keyword matching
        for i, text in enumerate(texts):
            text_lower = str(text).lower()
            for j, (aspect, kws) in enumerate(ASPECT_KEYWORDS.items()):
                if any(kw in text_lower for kw in kws):
                    pred_aspects[i, j] = 1

    results = []
    for i in range(len(texts)):
        row_res = {}
        text_clean = str(texts[i])
        orig_text = str(original_texts[i])
        clauses = split_into_clauses(orig_text)
        
        for j, aspect in enumerate(aspect_cols):
            row_res[aspect] = int(pred_aspects[i, j])
            sent_col = aspect.replace('aspek_', 'sentimen_')
            
            if pred_aspects[i, j] == 1:
                kws = ASPECT_KEYWORDS[aspect]
                matched_clauses = [c for c in clauses if any(kw in c.lower() for kw in kws)]
                target_text = " ".join(matched_clauses) if matched_clauses else text_clean
                row_res[sent_col] = get_sentiment_for_clause(target_text, lexicon)
            else:
                row_res[sent_col] = 'None'
                
        results.append(row_res)
        
    return pd.DataFrame(results)

def main():
    print("Inference ABSA Pipeline")
    
    # Paths Setup
    dataset_path = 'cleaned_reviews.csv'
    if not os.path.exists(dataset_path):
        dataset_path = os.path.join('..', 'preprocessing', 'cleaned_reviews.csv')
    if not os.path.exists(dataset_path):
        dataset_path = 'preprocessing/cleaned_reviews.csv'
        
    model_path = 'weights/aspect_classifier_svm.pkl'
    if not os.path.exists(model_path):
        model_path = os.path.join('..', 'weights', 'aspect_classifier_svm.pkl')
        
    vectorizer_path = 'weights/tfidf_vectorizer_aspect.pkl'
    if not os.path.exists(vectorizer_path):
        vectorizer_path = os.path.join('..', 'weights', 'tfidf_vectorizer_aspect.pkl')

    lexicon = load_lexicon()
    
    aspect_model = None
    tfidf_vectorizer = None
    if os.path.exists(model_path) and os.path.exists(vectorizer_path):
        print(f"Memuat model klasifikasi aspek dari {model_path}...")
        try:
            aspect_model = joblib.load(model_path)
            tfidf_vectorizer = joblib.load(vectorizer_path)
            print("Model berhasil dimuat.")
        except Exception as e:
            print(f"[WARN] Gagal memuat model: {e}. Menggunakan fallback keyword matching.")
    else:
        print("[INFO] Model ML belum dilatih. Pipeline akan menggunakan fallback keyword matching.")

    if os.path.exists(dataset_path):
        print(f"Memuat dataset dari {dataset_path}...")
        df = pd.read_csv(dataset_path).dropna(subset=['text_clean', 'ulasan'])
        print(f"Dataset dimuat: {len(df)} ulasan.")
        
        print("Menjalankan ABSA pada dataset...")
        absa_df = run_absa_inference(
            df['text_clean'].values, 
            df['ulasan'].values, 
            aspect_model, 
            tfidf_vectorizer, 
            lexicon
        )
        
        df_out = pd.concat([df.reset_index(drop=True), absa_df], axis=1)
        
        if 'rating' in df_out.columns:
            df_out['rating_num'] = df_out['rating'].str.extract('(\\d+)').astype(float)
            
        output_dir = 'data' if os.path.isdir('data') else '../data'
        os.makedirs(output_dir, exist_ok=True)
        
        df_out.to_csv(os.path.join(output_dir, 'aspect_analysis_gmaps.csv'), index=False)
        
        cols_compact = ['nama_pengulas', 'ulasan', 'text_clean', 'nama_gerai']
        if 'rating_num' in df_out.columns:
            cols_compact.append('rating_num')
        aspect_cols = list(ASPECT_KEYWORDS.keys())
        sentiment_cols = [a.replace('aspek_', 'sentimen_') for a in aspect_cols]
        df_out[cols_compact + aspect_cols + sentiment_cols].to_csv(
            os.path.join(output_dir, 'predictions_gmaps.csv'), 
            index=False
        )
        print("Inference dataset selesai dan disimpan.")
    else:
        print(f"[WARN] Dataset {dataset_path} tidak ditemukan. Melewati batch inference dataset.")

    # Uji coba unit test dengan contoh review
    print("\nRunning Unit Test...")
    test_reviews = [
        "Kopinya enak banget seger manisnya pas tapi sayang antriannya lama banget nunggunya bikin kesel",
        "Pelayanannya ramah banget mas-mas kasirnya murah senyum, tempatnya juga bersih adem cocok buat WFC",
        "Rasa kopinya hambar kaya air dan roti croissant-nya kosong stoknya abis padahal harganya mahal"
    ]
    test_clean = [
        "kopi enak banget seger manis pas sayang antri lama nunggu bikin kesel",
        "layan ramah banget mas kasir murah senyum tempat bersih adem cocok wfc",
        "rasa kopi hambar kaya air roti croissant kosong stok abis padahal harga mahal"
    ]
    
    test_res = run_absa_inference(test_clean, test_reviews, aspect_model, tfidf_vectorizer, lexicon)
    for i in range(len(test_reviews)):
        print(f"\nReview: \"{test_reviews[i]}\"")
        for aspect in ASPECT_KEYWORDS.keys():
            if test_res.loc[i, aspect] == 1:
                sent_col = aspect.replace('aspek_', 'sentimen_')
                print(f"  -> Aspek: {aspect.replace('aspek_', '').upper()} | Sentimen: {test_res.loc[i, sent_col].upper()}")
                
    print("\nSelesai.")

if __name__ == '__main__':
    main()
