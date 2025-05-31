import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="買う物評価", layout="centered")

# サンプルデータ
if "items" not in st.session_state:
    st.session_state.items = []

st.title("買う物比較ツール")

# 商品入力
st.header("商品を追加")
with st.form("item_form"):
    category = st.selectbox("カテゴリー", ["食品", "家電", "日用品", "その他"])
    name = st.text_input("商品名")
    price = st.number_input("価格", min_value=0.0)
    value = st.slider("性能（例: 満足度）", 1, 10, 5)
    submitted = st.form_submit_button("追加")
    if submitted:
        st.session_state.items.append({
            "カテゴリー": category,
            "商品名": name,
            "価格": price,
            "性能": value
        })

# ユーザーごとの重み
st.header("ユーザーの重み設定")
col1, col2 = st.columns(2)
with col1:
    st.subheader("ユーザーA")
    weight_price_A = st.slider("価格重視", 0.0, 1.0, 0.5)
    weight_value_A = 1.0 - weight_price_A
with col2:
    st.subheader("ユーザーB")
    weight_price_B = st.slider("価格重視", 0.0, 1.0, 0.5)
    weight_value_B = 1.0 - weight_price_B

# スコア計算
def compute_score(item, w_price, w_value):
    norm_price = 1 / (item["価格"] + 1)  # 安いほど高評価（簡易正規化）
    norm_value = item["性能"] / 10       # 10段階で正規化
    return w_price * norm_price + w_value * norm_value

# 表示
if st.session_state.items:
    st.header("スコア比較")
    df = pd.DataFrame(st.session_state.items)
    df["ユーザーAスコア"] = df.apply(lambda x: compute_score(x, weight_price_A, weight_value_A), axis=1)
    df["ユーザーBスコア"] = df.apply(lambda x: compute_score(x, weight_price_B, weight_value_B), axis=1)
    st.dataframe(df.sort_values("ユーザーAスコア", ascending=False))

