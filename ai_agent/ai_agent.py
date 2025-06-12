import pandas as pd
import google.generativeai as genai
import pickle
import re
from api_key import gemini_api_key
from model import input_csv_path , output_pkl_path

# Đọc dữ liệu và mô hình
def load_model_and_data():
    try:
        with open(output_pkl_path, 'rb') as f:
            model_data = pickle.load(f)
        return model_data['data'], model_data['tfidf'], model_data['cosine_sim']
    except FileNotFoundError:
        print("Model file not found. Running with raw data.")
        return load_laptop_data(), None, None

def load_laptop_data():
    try:
        laptop_data = pd.read_csv(input_csv_path, encoding='latin-1')
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

# Khởi tạo Gemini
def initialize_gemini():
    try:
        genai.configure(api_key=gemini_api_key)
        # Thử dùng 'gemma-3n-e4b-it', nếu lỗi thì fallback sang 'gemini-pro'
        try:
            model = genai.GenerativeModel('gemma-3n-e4b-it')
            print("Using model: gemma-3n-e4b-it")
            return model
        except Exception as e:
            print(f"Model 'gemma-3n-e4b-it' not available: {e}. Falling back to 'gemini-pro'.")
            model = genai.GenerativeModel('gemini-pro')
            print("Using model: gemini-pro")
            return model
    except Exception as e:
        print(f"Error initializing Gemini: {e}")
        return None

# Tìm laptop tương tự
def get_recommendations(laptop_name, laptop_data, tfidf, cosine_sim, n=3):
    if tfidf is None or cosine_sim is None or laptop_data.empty:
        return laptop_data.sample(n=n) if not laptop_data.empty else pd.DataFrame()
    idx = laptop_data.index[laptop_data['name'].str.lower() == laptop_name.lower()].tolist()
    if not idx:
        return laptop_data.sample(n=n) if not laptop_data.empty else pd.DataFrame()
    idx = idx[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_indices = [i[0] for i in sim_scores[1:n+1]]  # Loại bỏ chính nó
    return laptop_data.iloc[sim_indices]

# AI agent như nhà tư vấn
def ai_agent(query: str, laptop_data: pd.DataFrame, tfidf, cosine_sim, model) -> str:
    if not model:
        return "AI model not initialized. Please check your API key."

    # Chuẩn bị ngữ cảnh
    context = "Tôi là một nhà tư vấn bán hàng laptop nhiệt tình. Dưới đây là dữ liệu laptop:\n"
    if not laptop_data.empty:
        for _, row in laptop_data.iterrows():
            context += (f"- {row['name']}: Giá {row['price']}đ, CPU {row['cpu']}, "
                        f"RAM {row['ram']}GB, ROM {row['rom']}GB\n")
    else:
        context += "Hiện tại không có dữ liệu laptop đầy đủ. Hãy kiểm tra file CSV.\n"

    # Prompt cho Gemini
    prompt = (f"Act as a warm and engaging laptop sales consultant. Use the context: '{context}'. "
              f"Respond to the user query: '{query}'. For greetings, welcome warmly and ask how to assist. "
              f"For laptop queries (e.g., 'recommend a laptop under 20 million' or 'suggest a gaming laptop'), "
              f"use the context to suggest 1-3 laptops with details (name, price, CPU, RAM, ROM). "
              f"For farewells, say goodbye warmly. If unsure, encourage the user positively.")

    try:
        response = model.generate_content(prompt)
        # Bổ sung khuyến nghị từ mô hình nếu có, nhưng không lọc số vì price là chuỗi
        if "recommend" in query.lower() or "gợi ý" in query.lower():
            if not laptop_data.empty:
                recommendations = get_recommendations(query.split()[-1] if query.split() else "", laptop_data, tfidf, cosine_sim)
                if not recommendations.empty:
                    rec_text = "\nKhuyến nghị:\n" + "\n".join([f"- {row['name']}: {row['price']}đ, CPU {row['cpu']}, RAM {row['ram']}GB, ROM {row['rom']}GB" for _, row in recommendations.iterrows()])
                    return response.text + rec_text
        return response.text
    except Exception as e:
        return f"Error processing query: {e}. Hãy thử lại!"

# Vòng lặp tương tác
if __name__ == "__main__":
    laptop_data, tfidf, cosine_sim = load_model_and_data()
    model = initialize_gemini()
    print("Chào mừng! Tôi là trợ lý bán hàng laptop của bạn. Nói 'hello' hoặc hỏi (ví dụ: 'Gợi ý laptop dưới 20 triệu'), hoặc nhập 'exit' để thoát.")
    while True:
        user_query = input("Câu hỏi của bạn: ")
        if user_query.lower() == 'exit':
            break
        response = ai_agent(user_query, laptop_data, tfidf, cosine_sim, model)
        print(response)