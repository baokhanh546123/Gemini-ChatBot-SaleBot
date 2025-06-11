import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Đọc và làm sạch dữ liệu từ file Excel
def load_laptop_data():
    try:
        laptop_data = pd.read_csv('D:\\python\\HocData\\Scrape_Data\\laptop\\output.csv', encoding='latin-1')
        print("Raw data loaded successfully. Shape:", laptop_data.shape)
        
        # Kiểm tra và in số lượng giá trị thiếu
        print("Missing values per column:\n", laptop_data.isnull().sum())
        
        # Xóa tất cả hàng chứa NaN
        initial_rows = len(laptop_data)
        laptop_data.dropna(inplace=True)
        if len(laptop_data) < initial_rows:
            print(f"Dropped {initial_rows - len(laptop_data)} rows due to NaN values.")
        
        # Chuyển các cột cần thiết sang kiểu chuỗi (nếu cần)
        laptop_data['cpu'] = laptop_data['cpu'].astype(str)
        laptop_data['name'] = laptop_data['name'].astype(str)
        laptop_data['price'] = laptop_data['price'].astype(str)  # Giữ 'Liên hệ' như chuỗi
        laptop_data['ram'] = laptop_data['ram'].astype(str)
        laptop_data['rom'] = laptop_data['rom'].astype(str)
        
        print("Cleaned data shape:", laptop_data.shape)
        print("Cleaned data sample:\n", laptop_data.head())
        return laptop_data
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        return pd.DataFrame(columns=['cpu', 'name', 'price', 'ram', 'rom'])
    except ValueError as e:
        print(f"Data validation error: {e}")
        return pd.DataFrame(columns=['cpu', 'name', 'price', 'ram', 'rom'])
    except Exception as e:
        print(f"Unexpected error loading data: {e}")
        return pd.DataFrame(columns=['cpu', 'name', 'price', 'ram', 'rom'])
    
# Huấn luyện mô hình khuyến nghị
def train_recommendation_model(laptop_data):
    try:
        if laptop_data.empty:
            raise ValueError("No valid data to train model.")
        
        # Kết hợp các đặc trưng thành văn bản
        features = laptop_data.apply(lambda row: f"{row['cpu']} {row['name']} {row['price']} {row['ram']} {row['rom']}", axis=1)
        if features.empty or all(feature.strip() == '' for feature in features):
            raise ValueError("Features are empty or invalid after processing.")
        
        # Sử dụng TfidfVectorizer với tiền xử lý tùy chỉnh
        tfidf = TfidfVectorizer(stop_words=None, token_pattern=r'(?u)\b\w+\b')  # Không loại stop words
        tfidf_matrix = tfidf.fit_transform(features)
        if tfidf_matrix.shape[1] == 0:
            raise ValueError("TF-IDF matrix has empty vocabulary. Check data variability.")
        
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        return tfidf, cosine_sim
    except ValueError as e:
        print(f"Training error: {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error during training: {e}")
        return None, None

# Lưu mô hình
if __name__ == "__main__":
    try:
        laptop_data = load_laptop_data()
        print("Loaded data sample with NaN handled:\n", laptop_data.head() if not laptop_data.empty else "No data available")
        tfidf, cosine_sim = train_recommendation_model(laptop_data)
        if tfidf is not None and cosine_sim is not None:
            with open('D:\\python\\HocData\\Scrape_Data\\laptop\\recommendation_model.pkl', 'wb') as f:
                pickle.dump({'tfidf': tfidf, 'cosine_sim': cosine_sim, 'data': laptop_data}, f)
            print("Model trained and saved successfully.")
        else:
            print("Failed to train model. Please check data and error messages above.")
    except Exception as e:
        print(f"Main execution error: {e}")