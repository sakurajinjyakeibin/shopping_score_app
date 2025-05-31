import streamlit as st
import json
import os

# 保存先のファイル名（同じディレクトリに作成）
DATA_FILE = "products.json"
board_file = "board.json"


# 商品データの読み込み・保存用関数
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    return data


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_board():
    if os.path.exists(board_file):
        with open(board_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_board(posts):
    with open(board_file, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)


# ページのタイトル
st.title("買い物支援アプリ")

# サイドバーでモード選択
mode = st.sidebar.radio("モード選択", ["商品登録", "買い物評価", "掲示板"])

# 読み込み
products = load_data()

if mode == "商品登録":
    st.header("【機能1】 商品登録機能")
    st.write("下記フォームに商品情報を入力して保存してください。")
    with st.form(key="register_form", clear_on_submit=True):
        category = st.selectbox("カテゴリー", ["根菜", "葉物", "果物", "肉", "魚", "調味料", "その他"])
        product_name = st.text_input("商品名")
        price = st.number_input("値段", min_value=0.0, format="%.2f")
        shelf_life = st.number_input("日持ち日数", min_value=0, step=1)
        ease = st.slider("使いやすさ（10段階）", 1, 10, 5)
        comment=st.text_input("コメント（任意）")

        submit_reg = st.form_submit_button("保存")
        if submit_reg:
            if product_name.strip() == "":
                st.error("商品名を入力してください")
            else:
                # 登録情報を辞書にまとめる
                new_product = {
                    "category": category,
                    "product_name": product_name,
                    "price": price,
                    "shelf_life": shelf_life,
                    "ease": ease,
                    "comment": comment
                }
                # 既存データに追加
                products.append(new_product)
                save_data(products)
                st.success(f"商品【{product_name}】を保存しました。")

    # 保存済み商品の一覧表示 + ソート・削除機能
    if products:
        st.subheader("登録済み商品一覧")

        # 🔽 ソートキー選択
        sort_key = st.selectbox("並び替え基準", ["カテゴリー", "値段", "日持ち日数", "使いやすさ"])
        reverse = st.checkbox("降順で並び替える", value=False)

        # 🔄 並び替え処理
        key_map = {
            "カテゴリー": lambda x: x["category"],
            "値段": lambda x: x["price"],
            "日持ち日数": lambda x: x["shelf_life"],
            "使いやすさ": lambda x: x["ease"]
        }
        products = sorted(products, key=key_map[sort_key], reverse=reverse)

        # 表示（インデックス付きで個別削除できるように）
        for idx, prod in enumerate(products):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.write(
                    f"【{prod['category']}】{prod['product_name']} - 値段: {prod['price']}円, "
                    f"日持ち: {prod['shelf_life']}日, 使いやすさ: {prod['ease']}, コメント:{prod['comment']}"
                )
            with col2:
                if st.button("削除", key=f"delete_{idx}"):
                    # 元のデータ（未ソート）から一致する要素を削除
                    original = load_data()
                    original = [o for o in original if not (
                            o["product_name"] == prod["product_name"] and
                            o["category"] == prod["category"]
                    )]
                    save_data(original)
                    st.success(f"商品【{prod['product_name']}】を削除しました。")
                    st.experimental_rerun()  # 再読み込みで反映


elif mode == "買い物評価":
    st.header("【機能2】 買い物評価機能")
    st.write("評価したい商品の商品名と、新たな値段・日持ち日数を入力してください。")

    with st.form(key="evaluate_form"):
        search_name = st.text_input("商品名")
        eval_price = st.number_input("値段", min_value=0.0, format="%.2f")
        eval_shelf_life = st.number_input("日持ち日数", min_value=0, step=1)
        submit_eval = st.form_submit_button("評価する")

    if submit_eval:
        # 商品名で検索
        matched = [p for p in products if p["product_name"].strip() == search_name.strip()]
        if not matched:
            st.error("該当する商品が登録されていません。")
        else:
            product = matched[0]
            st.write("登録されている商品情報：")
            st.write(f"カテゴリー：{product['category']}")
            st.write(f"商品名：{product['product_name']}")
            st.write(f"登録値段：{product['price']}円")
            st.write(f"登録日持ち日数：{product['shelf_life']}日")
            st.write(f"使いやすさ：{product['ease']}（10段階）")

            # 評価スコアの算出
            # 例：score = 使いやすさ × (登録値段 / 入力値段) × (入力日持ち日数 / 登録日持ち日数)
            # ゼロ除算対策として、入力値段や登録日持ちがゼロの場合はスコア計算を行いません
            if eval_price == 0 or product["price"] == 0 or product["shelf_life"] == 0:
                st.error("評価計算に必要な値が0になっています。値段と日持ちは0以外の値を入力してください。")
            else:
                score = product["ease"] * (product["price"] / eval_price) * (eval_shelf_life / product["shelf_life"])
                st.subheader(f"評価スコア：{score:.2f}")

                # 例として、スコアが登録時の使いやすさ以上なら買い、そうでなければ買わないと判断する
                if score >= product["ease"]:
                    st.success("【おすすめ】買う！")
                else:
                    st.warning("【再検討】買いかどうか要検討")

                st.info("※スコアの算出方法：使いやすさ×(登録値段/入力値段)×(入力日持ち/登録日持ち)")

elif mode=="掲示板":
    st.header("掲示板")
    post_text = st.text_area("投稿内容を入力してください")

    if st.button("投稿する"):
        if post_text.strip():
            posts = load_board()
            new_post = {"text": post_text.strip()}
            posts.insert(0, new_post)  # 新しい投稿が先頭に
            save_board(posts)
            st.success("投稿が完了しました！")
            st.experimental_rerun()
        else:
            st.warning("空の投稿はできません。")

    # 投稿一覧表示
    st.subheader("過去の投稿")
    posts = load_board()
    if posts:
        for i, post in enumerate(posts):
            st.markdown(f"**{i+1}.** {post['text']}")
    else:
        st.info("まだ投稿がありません。")
