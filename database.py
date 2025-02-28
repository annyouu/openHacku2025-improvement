import mysql.connector
from mysql.connector import Error

# データベース接続設定
DB_CONFIG = {
    'host': '',
    'user': '',
    'password': '',
    'database': ''
}

# データベースに接続する関数
def connect():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            print("MySQLに接続しました")
            return conn
    except Error as e:
        print(f"MySQL接続エラー: {e}")
    return None

# データベースに食品データを挿入する関数



# meal_type(種類)をmealテーブルに追加する (ユーザが登録って押したら)

def insert_meal(meal_type):
    conn = connect()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor()
        query = "INSERT INTO meals (meal_type) VALUES (%s)"
        cursor.execute(query, (meal_type,))
        conn.commit()
        meal_id = cursor.lastrowid
        if not meal_id:
            print("meal_idの取得に失敗しました")
            return None
        print(f"{meal_type}のmealsテーブルに追加しました (ID: {meal_id})")
        return meal_id
    except Error as e:
        print(f"データ保存エラー: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# mead_idに紐づく食品データをfoodsテーブルに追加する
def insert_food(food_name, meal_id):
    if not meal_id:
        print("meal_idが無効です")
        return False

    conn = connect()
    if conn is None:
        return False
    
    try:
        cursor = conn.cursor()
        query = "INSERT INTO foods (name, meal_id) VALUES (%s, %s)"
        cursor.execute(query, (food_name, meal_id))
        conn.commit()
        print(f"{food_name}をmeal_id {meal_id} に保存しました")
        return True
    except Error as e:
        print(f"データ保存エラー: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ユーザーが新しく作ったフォームの削除ボタンを押したら、meal_typeを削除する
def delete_meal(meal_id):
    if not meal_id:
        print("meal_idが無効です")
        return
    
    conn = connect()
    if conn is None:
        return
    
    try:
        cursor = conn.cursor()

        # meal_idに紐づく食品データを削除
        query_foods = "DELETE FROM foods WHERE meal_id = %s"
        cursor.execute(query_foods, (meal_id,))

        # mealsテーブルからmeal_idを削除
        query_meal = "DELETE FROM meals WHERE id = %s"
        cursor.execute(query_meal, (meal_id,))

        conn.commit()
        print(f"meal_id {meal_id}のデータを削除しました。")
    except Error as e:
        print(f"データ削除エラー: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# foodsテーブルの全データを削除(次以降に影響がないように)
def clear_foods_table():
    conn = connect()
    if conn is None:
        return
    try:
        cursor = conn.cursor()
        query = "DELETE FROM foods"
        cursor.execute(query)
        conn.commit()
        print("foodsテーブルの全てのデータを削除しました。")
    except Error as e:
        print(f"データ削除エラー: {e}")
    finally:
        cursor.close()
        conn.close()

# mealsテーブルの全データを削除(次以降に影響がないように)
def clear_meals_table():
    conn = connect()
    if conn is None:
        return
    try:
        cursor = conn.cursor()
        query = "DELETE FROM meals"
        cursor.execute(query)
        conn.commit()
        print("mealsテーブルの全てのデータを削除しました。")
    except Error as e:
        print(f"データ削除エラー: {e}")
    finally:
        cursor.close()
        conn.close()

