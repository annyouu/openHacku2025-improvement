# 必要な.pyファイル(1) app.py(Flaskのメインアプリ)

import os
from flask import Flask, request, render_template, jsonify
from ultralytics import YOLO
from database import insert_food, clear_foods_table, insert_meal,clear_meals_table
from nutrition_api import get_food_info
from deepl_translator import translate_text

app = Flask(__name__)

# アップロードフォルダを設定
UPLOAD_FOLDER = "static/uploads/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# YOLOモデルの読み込み
model = YOLO("yolov8n.pt")

API_KEY = ""

# 男性の推奨摂取カロリー（基準）設定
MALE_CALORIE_REQUIREMENT = {
    "total": 2200  # 合計カロリーのみ
}


@app.route("/", methods=["GET","POST"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "morning_file" not in request.files or "lunch_file" not in request.files or "dinner_file" not in request.files:
        return jsonify({"error:" "ファイルが見つかりません"}, 400)
    
    morning_file = request.files["morning_file"]
    noon_file = request.files["lunch_file"]
    night_file = request.files["dinner_file"]

    if morning_file.filename == "" or noon_file.filename == "" or night_file.filename == "":
        return jsonify({"error": "ファイル名が空です"}, 400)
    
    # 固定ファイルを保存
    morning_filepath = os.path.join(app.config["UPLOAD_FOLDER"], morning_file.filename)
    lunch_filepath = os.path.join(app.config["UPLOAD_FOLDER"], noon_file.filename)
    dinner_filepath = os.path.join(app.config["UPLOAD_FOLDER"], night_file.filename)
    morning_file.save(morning_filepath)
    noon_file.save(lunch_filepath)
    night_file.save(dinner_filepath)

    # 食事を追加したとき
    additional_meals = []
    for key in request.files:
        if key.startswith("meal_file_"):
            index = key.split("_")[-1]
            meal_name = request.form.get("meal_name_" + index)
            file = request.files[key]
            if meal_name and file.filename:
                additional_meals.append({"name": meal_name, "file": file})
    
    # 食事追加のファイル保存
    additional_meals_data = []
    for meal in additional_meals:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], meal["file"].filename)
        meal["file"].save(filepath)
        additional_meals_data.append({"name": meal["name"], "filepath": filepath})
    
    # 前回のデータを削除
    clear_foods_table()
    clear_meals_table()

    # YOLOによる物体検出の共通処理
    def detect_objects(filepath):
        results = model(filepath)
        objects = []
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls.item())
                class_name = model.names[class_id]
                objects.append(class_name.replace("_", " "))
        return objects
    
    # 固定食事のオブジェクト検出
    objects_morning = detect_objects(morning_filepath)
    objects_noon = detect_objects(lunch_filepath)
    objects_night = detect_objects(dinner_filepath)

    # 追加食事のオブジェクト検出
    for meal in additional_meals_data:
        meal["objects"] = detect_objects(meal["filepath"])

    # データベースに固定食事の保存
    meal_id_morning = insert_meal("朝食")
    meal_id_noon = insert_meal("昼食")
    meal_id_night = insert_meal("夕食")
    for obj in objects_morning:
        insert_food(obj, meal_id_morning)
    for obj in objects_noon:
        insert_food(obj, meal_id_noon)
    for obj in objects_night:
        insert_food(obj, meal_id_night)

    # 追加食事の保存
    for meal in additional_meals_data:
        meal_id = insert_meal(meal["name"])
        for obj in meal["objects"]:
            insert_food(obj, meal_id)

    # 栄養情報を取得する処理
    def get_nutrition_data(food_names):
        nutrition_info = []
        for food_name in food_names:
            food_data = get_food_info(food_name, API_KEY)
            if food_data:
                food_nutrients = food_data["nutrients"]
                info = {
                    "food_name": translate_text(food_data["food_name"]),
                    "calories": food_nutrients.get("calories", "N/A"),
                    "carbs": food_nutrients.get("carbs", "N/A"),
                    "protein": food_nutrients.get("protein", "N/A"),
                    "fat": food_nutrients.get("fat", "N/A"),
                    "fiber": food_nutrients.get("fiber", "N/A"),
                }
                nutrition_info.append(info)
        return nutrition_info
    
    # 固定食事の栄養情報
    nutrition_info_morning = get_nutrition_data(objects_morning)
    nutrition_info_noon = get_nutrition_data(objects_noon)
    nutrition_info_night = get_nutrition_data(objects_night)

    # 追加食事の栄養情報とカロリー計算
    def calculate_calories(nutrition_info):
        total = 0
        for food in nutrition_info:
            if isinstance(food["calories"], dict):
                total += food["calories"].get("value", 0)
            elif isinstance(food["calories"], (int, float)):
                total += food["calories"]
        return total
    
    additional_meal_nutrition = []
    for meal in additional_meals_data:
        nutrition_info = get_nutrition_data(meal["objects"])
        meal["nutrition_info"] = nutrition_info
        meal["total_calories"] = calculate_calories(nutrition_info)
        meal["filename"] = os.path.basename(meal["filepath"])
        additional_meal_nutrition.append(meal)
    
    # 全ての合計カロリー
    total_calories_morning = calculate_calories(nutrition_info_morning)
    total_calories_noon = calculate_calories(nutrition_info_noon)
    total_calories_night = calculate_calories(nutrition_info_night)
    total_calories_additional = sum(meal["total_calories"] for meal in additional_meal_nutrition)

    daily_total_calories = total_calories_morning + total_calories_noon + total_calories_night + total_calories_additional

    # 男性の推奨摂取カロリー（基準）との比較
    calorie_comparison = {
        "total_calories": daily_total_calories,
        "recommended_calories": MALE_CALORIE_REQUIREMENT["total"],
        "calorie_difference": daily_total_calories - MALE_CALORIE_REQUIREMENT["total"],
        "calorie_status": "不足" if daily_total_calories < MALE_CALORIE_REQUIREMENT["total"] else "超過" if daily_total_calories > MALE_CALORIE_REQUIREMENT["total"] else "適正"
    }

    return render_template("result.html",
                           filename_morning=morning_file.filename,
                           filename_noon=noon_file.filename,
                           filename_night=night_file.filename,
                           nutrition_info_morning=nutrition_info_morning,
                           nutrition_info_noon=nutrition_info_noon,
                           nutrition_info_night=nutrition_info_night,
                           total_calories_morning=total_calories_morning,
                           total_calories_noon=total_calories_noon,
                           total_calories_night=total_calories_night,
                           additional_meals=additional_meal_nutrition,
                           daily_total_calories=daily_total_calories,
                           calorie_comparison=calorie_comparison)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)


    